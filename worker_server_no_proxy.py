import datetime as dt
import json
import multiprocessing as mp
import platform
import pytz
import re
import socket
import string
import struct
import sys
import time
import traceback
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
if platform.system() in ('Linux',):
    from xvfbwrapper import Xvfb

from myprofile import profile as PROFILE
thisprofile = PROFILE['test_index']

class WebDriverLoadOverTimeException(Exception):
    pass


def do_the_job(payload, driver):
    payload = json.loads(payload)
    retdir = {}
    for key, item in payload.items():
        if key != 'JOB':
            retdir[key] = item
    retdir['JOB'] = {}
    for key, item in payload['JOB'].items():
        retdir['JOB'][key] = None
    payload_url = payload['URL']
    pre_reqlst = []
    if 'PRE_REQ' in payload and payload['PRE_REQ'] is not None:
        if type(payload['PRE_REQ']) != list:
            pre_reqlst = [payload['PRE_REQ']]
        else:
            pre_reqlst = payload['PRE_REQ']
    jobretdir = {}
    try:
        # print(payload_url)
        try:
            driver.get(payload_url)
        except TimeoutException:
            try:
                driver.execute_script('''return window.stop''')
            except TimeoutException:
                try:
                    driver.get(payload_url)
                except:
                    raise WebDriverLoadOverTimeException
        content_reqlst=[]
        if 'CONTENT_REQ' in payload and payload['CONTENT_REQ'] is not None:
            if type(payload['CONTENT_REQ']) != list:
                content_reqlst = [payload['CONTENT_REQ']]
            else:
                content_reqlst = payload['CONTENT_REQ']
        try:
            for eachpre in content_reqlst:
                jsstrlst = re.findall('^ *js\((.*?)\) *$', eachpre.strip(), re.DOTALL)
                if len(jsstrlst) > 0:
                    ispass = False
                    retry = 50
                    while not ispass:
                        if driver.execute_script(jsstrlst[0]) is True:
                            ispass = True
                        else:
                            retry -= 1
                            if retry == 0:
                                raise RuntimeError('Dep Not Pass')
                            time.sleep(0.1)
                    print(retry)
                else:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, eachpre)))
        except KeyboardInterrupt:
            raise
        except:
            print(traceback.format_exc())


        if 'PRE_SETUP' in payload and payload['PRE_SETUP'] is not None:
            presetup = payload['PRE_SETUP']
            if type(payload['PRE_SETUP']) != list:
                presetup = [payload['PRE_SETUP']]
            for eachitem in presetup:
                if type(eachitem) == str:
                    jsstrlst = re.findall('^ *js\((.*?)\) *$', eachitem.strip(), re.DOTALL)
                    if len(jsstrlst) > 0:
                        try:
                            driver.execute_script(jsstrlst[0])
                        except KeyboardInterrupt:
                            raise
                        except:
                            print(traceback.format_exc())
                elif type(eachitem) == dict:
                    try:
                        if eachitem['actioncode'] == 'click':
                            elem = driver.find_element_by_xpath(eachitem['target'])
                            elem.click()
                        elif eachitem['actioncode'] == 'clear':
                            elem = driver.find_element_by_xpath(eachitem['target'])
                            elem.clear()
                        elif eachitem['actioncode'] == 'send_keys':
                            elem = driver.find_element_by_xpath(eachitem['target'])
                            elem.send_keys(eachitem['value'])
                        elif eachitem['actioncode'] == 'sleep':
                            time.sleep(int(eachitem['value']))
                    except:
                        pass
                time.sleep(0.5)
        time.sleep(1)
        try:
            for eachpre in pre_reqlst:
                jsstrlst = re.findall('^ *js\((.*?)\) *$', eachpre.strip(), re.DOTALL)
                if len(jsstrlst) > 0:
                    ispass = False
                    retry = 50
                    while not ispass:
                        if driver.execute_script(jsstrlst[0]) is True:
                            ispass = True
                        else:
                            retry -= 1
                            if retry == 0:
                                raise RuntimeError('Dep Not Pass')
                            time.sleep(0.1)
                    print(retry)
                else:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, eachpre)))
        except KeyboardInterrupt:
            raise
        except:
            pass

        for key, item in payload['JOB'].items():
            thisitemlst = item
            if type(item) != list:
                thisitemlst = [item]
            tempvalue=None
            for eachitem in thisitemlst:
                # print(eachitem)
                if eachitem is None:
                    jobretdir[key] = None
                    continue
                # if key == 'meta':
                #     tempvalue = jobretdir[key] if key in jobretdir and jobretdir[key] is not None else ''
                jsstrlst = re.findall('^ *js\((.*?)\) *$', eachitem.strip(), re.DOTALL)
                if len(jsstrlst) > 0:
                    try:
                        # print(jsstrlst[0])
                        js_res = driver.execute_script(jsstrlst[0])
                        jobretdir[key] = str(js_res) if js_res is not None else None
                    except WebDriverException:
                        # print(traceback.format_exc())
                        jobretdir[key] = None
                else:
                    try:
                        elem = driver.find_element_by_xpath(eachitem)
                        jobretdir[key] = elem.text
                    except InvalidSelectorException as e:
                        try:
                            jobretdir[key] = driver.find_element_by_xpath('/'.join(eachitem.split('/')[:-1])) \
                                .get_attribute(eachitem.split('/')[-1][1:])
                        except NoSuchElementException as e:
                            jobretdir[key] = None
                        except ValueError as e:
                            jobretdir[key] = None
                    except KeyboardInterrupt:
                        raise
                    except:
                        jobretdir[key] = None

                    jobretdir[key] = None if jobretdir[key] == '' else jobretdir[key]
                if jobretdir[key] is not None:
                    printable = set(string.printable)
                    jobretdir[key] = ''.join(filter(lambda x: x in printable, jobretdir[key]))
                    jobretdir[key] = jobretdir[key].replace('\n', '~').replace('\r', '~').replace('\t', '~')
                    jobretdir[key] = re.sub(' +', ' ', jobretdir[key])
                    if key != 'meta':
                        break
                if key == 'meta':
                    if tempvalue is None:  # first time
                        tempvalue = '' if jobretdir[key] is None else jobretdir[key]
                    else:
                        tempvalue = tempvalue+ ' ;; ' + ('' if jobretdir[key] is None else jobretdir[key])
            if key == 'meta':
                jobretdir[key] = tempvalue



        retdir['JOB'] = jobretdir
        retdir['STATUS'] = 'DONE'
    except WebDriverLoadOverTimeException:
        retdir['STATUS'] = 'WebDriver OT'
        raise
    except KeyboardInterrupt:
        raise
    except:
        print(traceback.format_exc())
    finally:
        retdir['LAST_CRAWL'] = \
            dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
    ret_all = {
        'recv': payload,
        'ret': retdir
    }
    return ret_all

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def res_upload(IP, PORT, key, res_json):
    for idx in range(5):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((IP, PORT))
                sendstr = ('POST /?key={} '.format(key) + res_json.strip()).encode('ascii')
                s.sendall(sendstr)
                break
        except TimeoutError as e:
            print('Upload error {}'.format(str(e)))
            continue


def worker_index(job_queue, key, CONNECTINFO):
    if platform.system() == 'Darwin':
        pathstr = 'chromedriver_mac64/chromedriver'
    if platform.system() == 'Linux':
        pathstr = 'chromedriver_linux64/chromedriver'
    if platform.system() == 'Windows':
        pathstr = 'chromedriver_win32/chromedriver.exe'
    # os.environ["webdriver.chrome.driver"] = "/home/jianwei.xiao/crawler/chromedriver_linux64/chromedriver"
    prefs = {"profile.managed_default_content_settings.images": 2}
    co = Options()
    # zco.add_extension('./proxy_config.zip')
    co.add_experimental_option("prefs", prefs)
    if platform.system() in ('Linux',):
        vdisplay = Xvfb()
        vdisplay.start()
    try:
        while True:
            try:
                driver = webdriver.Chrome(executable_path="./{}".format(pathstr),
                                          chrome_options=co)
                driver.set_page_load_timeout(15)
                driver.set_window_size(1024, 1440)
                for idx in range(100):
                    payload_json = job_queue.get()
                    retdir = do_the_job(payload_json, driver)
                    driver.delete_all_cookies()
                    try:
                        retstr = json.dumps(retdir)
                    except KeyboardInterrupt:
                        raise
                    except:
                        print(sys.exc_info())
                        time.sleep(5)
                        continue
                    # print(retstr)
                    res_upload(CONNECTINFO[0], CONNECTINFO[1], key, res_json=retstr)
            except KeyboardInterrupt:
                raise
            except:
                pass
            finally:
                driver.quit()
    finally:
        if platform.system() in ('Linux',):
            vdisplay.stop()


def get_payload(connectinfo, distributor_key, job_queue, speed):
    startkey = 'thispayload:'
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(tuple(connectinfo))
                s.sendall('GET /?key={}'.format(distributor_key).encode('ascii'))
                data = recv_msg(s).decode('ascii', 'ignore')
                # data = s.recv(4096).decode('ascii', 'ignore')
            try:
                pos = data.index(startkey) + len(startkey)
                payload = data[pos:].strip()
                if payload != 'empty':
                    job_queue.put(payload)
                    time.sleep(1/speed)
                else:
                    time.sleep(3*1/speed)
            except ValueError as e:
                print(e)
        except KeyboardInterrupt:
            raise
        except:
            time.sleep(0.1)
            # print(traceback.format_exc())


def main(profilestr, worker_num):
    thisPROFILE = PROFILE[profilestr]
    distributor_server = thisPROFILE['distributor_server']
    receiver_server = thisPROFILE['receiver_server']
    distributor_key = thisPROFILE['distributor_key']
    receiver_key = thisPROFILE['receiver_key']
    speed = thisPROFILE['speed_per_worker']
    payloadqueue = mp.Queue( 1 )
    mp.Process(target=get_payload,
               args=(
                   distributor_server,
                   distributor_key,
                   payloadqueue,
                   speed
               )
               ).start()

    plist = []

    for idx in range(worker_num):
        p = mp.Process(target=worker_index,
                       args=(payloadqueue,
                             receiver_key,
                             receiver_server)
                       )
        p.start()
        plist.append(p)
        time.sleep(2)

    while True:
        if platform.system() == 'Darwin':
            print(payloadqueue.empty())
        else:
            print(payloadqueue.qsize())
        time.sleep(10)


if __name__ == '__main__':
    # HOST = '146.148.86.98'  # The remote host
    profilestr = sys.argv[1]
    worker = int(sys.argv[2])
    # time.sleep(10)
    main(profilestr, worker)