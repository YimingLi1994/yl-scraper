import datetime as dt
import json
import platform
import re
import string
import time
import traceback


import pytz

from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
import uuid
from google.cloud import storage
def printable_filter(inputstr):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, inputstr))

class WebDriverLoadOverTimeException(Exception):
    pass


def work_on_the_job(payload, driver):
    # payload = json.loads(payload)
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
        content_reqlst = []
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
            tempvalue = None
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
                        tempvalue = tempvalue + ' ;; ' + ('' if jobretdir[key] is None else jobretdir[key])
            if key == 'meta':
                jobretdir[key] = tempvalue

        retdir['JOB'] = jobretdir
        # retdir['LAST_CRAWL'] = \
        #     dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
        return retdir['JOB']
    except WebDriverLoadOverTimeException:
        retdir['STATUS'] = 'WebDriver OT'
        raise




def get_captcha(inputstr):
    import re
    import requests
    import binascii
    retlst = re.findall('https://.*?amazon.com/captcha/.*?.jpg', inputstr)
    retstr = None
    try:
        if len(retlst) > 0:
            url = retlst[0]
            r = requests.get(url, timeout=0.5)
            retstr = binascii.b2a_qp(r.content).decode('ascii')
    except:
        retstr = traceback.format_exc()
    return retstr


def do_the_job(jobdict, driver=None):
    workload = {'JOB': {
        'SKU': [
            '''//th[contains(text(), 'ASIN')]/parent::tr/td''',
            '''js(return window.location.href)''',
            'js(return JSON.parse(document.evaluate("//*[@id=\'addServices_feature_div\']//script[contains(@data-a-state,\'vas-common-vm\')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.text)[\'productAsin\'])'],
        'UPC': None,
        'availability': ['//*[@id="availability"]',
                         '//*[@id="sns-availability"]/div/span[contains(@class,\'size-medium\')]',
                         '//*[@id="outOfStock"]',
                         '//*[@id="fast-track"]',
                         "//img[contains(@src,'title') and contains(@src,'error') and contains(@alt, 'orry')]/@alt"],
        'brand': ['//div[@id="product-details-grid_feature_div"]//tr[contains(.,"Brand") or contains(.,"brand") ]',
                  '//*[@id="bylineInfo"]'],
        'channel': ['//*[@id="merchant-info"]',
                    '//*[@id="sns-availability"]/div/span[contains(@class,\'size-base\')]'],
        'meta': None,
        'model': ['//div[@id="product-details-grid_feature_div"]//tr[contains(.,"Model") or contains(.,"model")]',
                  '//*[@id="detail-bullets"]//li[contains(.,\'model number\')]',
                  '//*[@id="productDetailsTable"]//th[contains(.,\'model number\')]/parent::tr'],
        'page_path': ['//div[@id="wayfinding-breadcrumbs_feature_div"]/ul[contains(@class, "list")]',
                      '//*[@id="nav-subnav"]/a[1]'],
        'price': [
            '//div[@id="price"]//span[@id="priceblock_ourprice"]|//div[@id="price"]//span[@id="priceblock_dealprice"]',
            '//*[@id="onetimeOption"]//div[contains(@class,\'buybox-price\')]',
            'js(return JSON.parse(document.evaluate("//*[@id=\'addServices_feature_div\']//script[contains(@data-a-state,\'vas-common-vm\')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.text)[\'buyboxPrice\'])'],
        'price_type': ['//*[@id="onetimeOption"]/label/span',
                       '//*[@id="addon"]//i[contains(@class,\'addon\')]',
                       '//*[@id="burjActionPanelAddOnBadge"]'],
        'product_title': ['//span[@id="productTitle"]',
                          "//img[contains(@src,'title') and contains(@src,'error') and contains(@alt, 'orry')]/@alt"],
        'rating': '//span[@id="acrPopover"]/@title',
        'reviews': ['//div[@id="averageCustomerReviews_feature_div"]//a[contains(@id,"CustomerReviewLink")]/span[@id]',
                    '//*[@id="averageCustomerReviews"]'],
        'shipping': ['//*[@id="ourprice_shippingmessage"]'],
        'style': ['//*[@id="variation_color_name"]',
                  '//*[@id="shelf-label-color_name"]'],
        'style2': ["//div[@id and contains(@class,'variation-dropdown')]//option[@id and @selected]",
                   '//div[@id="variation_size_name"]//div[@class]',
                   '//*[@id="shelf-label-size_name"]']},
        'PID': jobdict['PID'],
        'STATUS': 'READY',
        'URL': 'http://www.amazon.com/gp/product/{}?psc=1'.format(jobdict['PID']) if jobdict['URL'] is None else
        jobdict['URL'],
        'WEBSITE': 'Amazon'}

    ret_dict = work_on_the_job(workload, driver)
    #ret_dict['SKU'] = jobdict['SKU']
    if ret_dict['product_title'] is None:
        rawpagestr = printable_filter(driver.page_source)
        sto_client = storage.Client('yl3573')
        bucketname = 'scraper_error_log'
        blobpath = str(uuid.uuid4())
        bucket = sto_client.bucket(bucketname)
        blob = bucket.blob(blobpath)
        blob.upload_from_string(rawpagestr)
        retwrapper = {
            'STATUS': 'FAIL',
            'PAYLOAD': json.dumps({'Reason': 'Product Title does not exists',
                                   'Rawpage': blobpath})
        }
    else:
        retwrapper = {
            'STATUS': 'SUCCESS',
            'PAYLOAD': json.dumps(ret_dict),
        }
    return retwrapper


if __name__ == '__main__':
    payload_dict = {"WEBSITE": "Amazon",
                    "PID": "B00NNKC8AO",
                    "SKU": "B00NNKC8AO",
                    "URL": None, #"https://www.amazon.com/gp/product/B007UI47PY/ref=s9_acsd_al_bw_c_x_2_w",
                    "TAG": 'test'}

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

        # 3,6,8,9,14,20,22,24,26,32,34,37,42,46,49,52,71,96,
