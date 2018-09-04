import datetime as dt
import json
import re
import string
import time
import traceback
import pytz
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
import traceback
import uuid
from job_by_websites import Amazon_driver
from google.cloud import storage
def printable_filter(inputstr):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, inputstr))

class WebDriverLoadOverTimeException(Exception):
    pass

def actullay_do_the_job(payload, driver):
    payload = json.loads(payload)
    retdir = {}
    for key, item in payload.items():
        if key != 'JOB':
            retdir[key] = item
    retdir['JOB'] = {}
    for key, item in payload['JOB'].items():
        retdir['JOB'][key] = None
    payload_url = payload['URL']
    pre_reqlst= []
    if 'PRE_REQ' in payload and payload['PRE_REQ'] is not None:
        if type(payload['PRE_REQ'] )!=list:
            pre_reqlst = [payload['PRE_REQ']]
        else:
            pre_reqlst = payload['PRE_REQ']

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
                    WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, eachpre)))
        except KeyboardInterrupt:
            raise
        except:
            print(traceback.format_exc())


        if 'PRE_SETUP' in payload and payload['PRE_SETUP'] is not None:
            presetup = payload['PRE_SETUP']
            if type(payload['PRE_SETUP'])!=list:
                presetup=[payload['PRE_SETUP']]
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
                            elem=driver.find_element_by_xpath(eachitem['target'])
                            elem.click()
                        elif eachitem['actioncode'] == 'clear':
                            elem = driver.find_element_by_xpath(eachitem['target'])
                            elem.clear()
                        elif eachitem['actioncode'] == 'send_keys':
                            elem = driver.find_element_by_xpath(eachitem['target'])
                            if len(re.findall('^Keys.(.*)$', eachitem['value']))>0:
                                thiskey = re.findall('Keys.(.*)', eachitem['value'])[0]
                                if thiskey == 'RETURN':
                                    elem.send_keys(Keys.RETURN)
                            else:
                                elem.send_keys(eachitem['value'])
                        elif eachitem['actioncode'] == 'wait':
                            tic = time.time()
                            Found = False
                            elapsed = time.time() - tic
                            while elapsed < eachitem['timeout'] and not Found:
                                try:
                                    elem = driver.find_element_by_xpath(eachitem['target'])
                                    Found = True
                                except NoSuchElementException as e:
                                    print('Not Found')
                                    time.sleep(eachitem['inteval'])
                                    elapsed = time.time() - tic
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
        jobretdir = {}
        for key, item in payload['JOB'].items():
            thisitemlst = item
            if type(item) != list:
                thisitemlst = [item]

            for eachitem in thisitemlst:
                #print(eachitem)
                if eachitem is None:
                    jobretdir[key] = None
                    continue
                if key == 'meta':
                    tempvalue = jobretdir[key] if key in jobretdir and jobretdir[key] is not None else ''
                jsstrlst = re.findall('^ *js\((.*?)\) *$', eachitem.strip(), re.DOTALL)
                if len(jsstrlst) > 0:
                    try:
                        #print(jsstrlst[0])
                        js_res = driver.execute_script(jsstrlst[0])
                        jobretdir[key] = str(js_res) if js_res is not None else None
                    except WebDriverException:
                        print(traceback.format_exc())
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
                    jobretdir[key] = tempvalue+'::'+jobretdir[key] if len(tempvalue)>0 and jobretdir[key] is not None\
                                    else jobretdir[key] if jobretdir[key] is not None \
                                    else tempvalue if len(tempvalue)>0 \
                                    else None

        retdir['JOB'] = jobretdir
        retdir['STATUS'] = 'DONE'
    except WebDriverLoadOverTimeException:
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

def do_the_job(search_pid, driver=None):
    search_template = {
        'JOB': {
            'PID':'''//*[@id="result_0"]/@data-asin''',
            'URL':'''//*[@id="result_0"]//a[@title]/@href'''
        },
        'CONTENT_REQ':['''//*[@id="twotabsearchtextbox"]'''],
        'PRE_SETUP': [
            {'actioncode': 'click',
             'target': '''//*[@id="twotabsearchtextbox"]'''},
            {'actioncode': 'clear',
             'target': '''//*[@id="twotabsearchtextbox"]'''},
            {
                'actioncode': 'send_keys',
                'target': '''//*[@id="twotabsearchtextbox"]''',
                'value': search_pid['PID']
            },
            {
                'actioncode': 'send_keys',
                'target': '''//*[@id="twotabsearchtextbox"]''',
                'value': 'Keys.RETURN'
            },
            {
                'actioncode': 'wait',
                'target': '''//*[@id="noResultsTitle"]|//*[@id="result_0"]''',
                'timeout': 10,
                'inteval': 1
            },

        ],
        'STATUS': 'READY',
        'URL':'https://www.amazon.com'
    }


    workload = {
        'WEBSITE': 'Amazon',
        'PID': None,
        'SKU': None,
        'URL': None,
        'TAG': 'model_search'
    }
    try:
        # Try to find PID in the following code:
        search_ret = actullay_do_the_job(json.dumps(search_template),driver)
        try:
            workload['PID'] = search_ret['ret']['JOB']['PID']
            workload['URL'] = search_ret['ret']['JOB']['URL']
        except KeyError:
            workload['PID'] = None
            workload['URL'] = None

        if workload['PID'] is not None:
            return Amazon_driver.do_the_job(workload, driver)
        else:
            retdir = {
                'WEBSITE': search_pid['WEBSITE'],
                'PID': search_pid['PID'],
                'SKU': search_pid['SKU'],
                'URL': search_pid['URL'],
                'STATUS': 'FAIL',
                'PAYLOAD': {'Reason': 'Model_search_not_found'},
            }

            return retdir
    except:
        retdir = {
            'WEBSITE': search_pid['WEBSITE'],
            'PID': search_pid['PID'],
            'SKU': search_pid['SKU'],
            'URL': search_pid['URL'],
            'STATUS': 'FAIL',
            'PAYLOAD': {'Reason':'Model searching error',
                     'Detail': traceback.format_exc()},
        }
        return retdir



if __name__ == '__main__':
    payload_dict = {
        'WEBSITE': 'Amazon',
        'PID': '742169002aaab722',
        'SKU': None,
        'URL': None,
        'TAG': 'model_search'
    }
    import platform
    if platform.system() == 'Darwin':
        pathstr = '../chromedriver_mac64/chromedriver'
    if platform.system() == 'Linux':
        pathstr = '../chromedriver_linux64/chromedriver'
    if platform.system() == 'Windows':
        pathstr = '../chromedriver_win32/chromedriver.exe'
    # os.environ["webdriver.chrome.driver"] = "/home/jianwei.xiao/crawler/chromedriver_linux64/chromedriver"
    prefs = {"profile.managed_default_content_settings.images": 2}
    co = Options()
    # zco.add_extension('./proxy_config.zip')
    co.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path="./{}".format(pathstr),
                              chrome_options=co)
    driver.set_page_load_timeout(15)
    driver.set_window_size(1024, 1440)

    retdir = {
        'WEBSITE': payload_dict['WEBSITE'],
        'PID': payload_dict['PID'],
        'SKU': payload_dict['SKU'],
        'URL': payload_dict['URL'],
        'STATUS': None,
        'PAYLOAD': None,
    }
    try:
        retdict_temp = do_the_job(payload_dict, driver)
        retdir['STATUS'] = retdict_temp['STATUS']
        retdir['PAYLOAD'] = retdict_temp['PAYLOAD']
    except:
        retdir['STATUS'] = 'FAIL'
        retdir['PAYLOAD'] = json.dumps({'Reason': traceback.format_exc()})
    finally:
        retdir['LAST_CRAWL'] = \
            dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        retstr = json.dumps({'ret': retdir})
        print(retdir)
        driver.delete_all_cookies()
        driver.quit()