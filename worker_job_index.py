import importlib
import json
import multiprocessing as mp
import os
import platform
import re
import socket
import struct
import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime as dt
import pytz
if platform.system() in ('Linux',):
    from xvfbwrapper import Xvfb
import profile as PROFILE

comp_module_dict = {}
for root, dirs, files in os.walk("./job_by_websites"):
    for filename in files:
        res = re.findall('^.*?.py$', filename)
        if len(res) > 0:
            comp_module_dict[re.findall('^(.*)?.py$', filename)[0]] = \
                importlib.import_module('job_by_websites.'+re.findall('^(.*)?.py$', filename)[0])


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
    for idx in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((IP, PORT))
                sendstr = ('POST /?key={} '.format(key) + res_json.strip()).encode('ascii')
                s.sendall(sendstr)
                break
        except TimeoutError as e:
            print('Upload error {}'.format(str(e)))
            continue


def module_selector(WEBSITE, TAG_json):
    tagdict = json.loads(TAG_json)
    if WEBSITE == 'Walmart':
        if tagdict['proxy'] is False and tagdict['webdriver'] is False:
            return 'Walmart'
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Walmart_driver'
    if WEBSITE == 'Sears':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Sears_driver'
    if WEBSITE == 'Lowes':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Lowes_driver'
    if WEBSITE == 'Home Depot':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Home_Depot_driver'
    if WEBSITE == 'BestBuy':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'BestBuy_driver'
    if WEBSITE == 'Amazon':
        if 'search' in tagdict and tagdict['search'] is True:
            return 'Amazon_search'
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Amazon_driver'
    if WEBSITE == 'Target':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Target_driver'
    if WEBSITE == 'ToysRUs':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'ToysRus_driver'
    if WEBSITE == 'Staples':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Staples_driver'
    if WEBSITE == 'Wayfair':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Wayfair_driver'
    if WEBSITE == 'JC Penney':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'JCPenney_driver'
    if WEBSITE == 'Kohls':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Kohls_driver'
    if WEBSITE == 'SearsHometownStores':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'SearsHometownStores_driver'
    if WEBSITE == 'Kmart':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Kmart_driver'
    if WEBSITE == 'Purple':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Purple'
    if WEBSITE == 'Tuftandneedle':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Tuftandneedle'
    if WEBSITE == 'Casper':
        if tagdict['proxy'] is False and tagdict['webdriver'] is True:
            return 'Casper'
    raise RuntimeError('Module selector cannot choose file for Website: {} and {}'.format(WEBSITE,TAG_json))


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
                    payload_dict = json.loads(payload_json)
                    retdir = {
                        'WEBSITE': payload_dict['WEBSITE'],
                        'PID': payload_dict['PID'],
                        'SKU': payload_dict['SKU'],
                        'URL': payload_dict['URL'],
                        'TAG': payload_dict['TAG'],
                        'STATUS': None,
                        'PAYLOAD': None,
                        'retry':payload_dict['retry'],
                        'DISTRIBUTED_TIME' : payload_dict['DISTRIBUTED_TIME'],
                        'DISTRIBUTED_ID': payload_dict['DISTRIBUTED_ID'],
                        'distributed': payload_dict['distributed'],
                    }
                    try:
                        retdict_temp = (comp_module_dict[module_selector(payload_dict['WEBSITE'],payload_dict['JOB_TAG'])]
                                   .do_the_job(payload_dict, driver))
                        retdir['STATUS'] = retdict_temp['STATUS']
                        retdir['PAYLOAD'] = retdict_temp['PAYLOAD']

                    except KeyboardInterrupt:
                        raise
                    except:
                        retdir['STATUS'] = 'FAIL'
                        retdir['PAYLOAD'] = json.dumps({'Reason':traceback.format_exc()})
                    finally:
                        retdir['LAST_CRAWL'] =\
                            dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
                        retstr = json.dumps({'ret':retdir})
                        print(retstr)
                        res_upload(CONNECTINFO[0], CONNECTINFO[1], key, res_json=retstr)
                        driver.delete_all_cookies()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
            finally:
                try:
                    driver.quit()
                except Exception as e:
                    print(e)
    finally:
        if platform.system() in ('Linux',):
            vdisplay.stop()


def get_payload(connectinfo, distributor_key, job_queue,speed):
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
                    time.sleep(3/speed)
            except ValueError as e:
                print(e)
        except KeyboardInterrupt:
            raise
        except:
            time.sleep(0.1)
            # print(traceback.format_exc())


def main(profilestr, worker_num):
    from myprofile import profile as PROFILE
    thisPROFILE = PROFILE[profilestr]
    distributor_server = thisPROFILE['distributor_server']
    receiver_server = thisPROFILE['receiver_server']
    distributor_key = thisPROFILE['distributor_key']
    receiver_key = thisPROFILE['receiver_key']
    speed = thisPROFILE['speed_per_worker']
    payloadqueue = mp.Queue(1)
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
