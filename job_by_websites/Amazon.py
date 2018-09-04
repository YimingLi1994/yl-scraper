import json
import string
import traceback
from io import StringIO

import lxml.html as lh
import requests
# from jsonpath_ng import
from jsonpath_ng.ext import parse

__all__ = ["do_the_job"]


def get_xpath(xpthstr, elem_tree):
    elemlst = elem_tree.xpath(xpthstr)
    if len(elemlst) > 0:
        return elemlst[0]
    else:
        return None


def get_content(URL):
    # proxy = {"http": "http://10099:M9GUfa@hn4.nohodo.com:10099/",
    #          "https": "http://10099:M9GUfa@hn4.nohodo.com:10099/"}
    headers = {'Connection': 'keep-alive',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'accept-language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    r = requests.get(URL, headers=headers, timeout=10)
    ready_str = r.text
    printable = set(string.printable)
    ready_str = ''.join(filter(lambda x: x in printable, ready_str))
    with open('Amzcheck.html','w') as f:
        f.write(ready_str)
    elem_tree = lh.parse(StringIO(ready_str))
    return elem_tree

def fill_template(job_template):
    elem_tree = get_content(job_template['URL'])
    retdict={}
    for key,value in job_template['JOB'].items():
        retdict[key] = None
        thisvalue = value
        if type(thisvalue) != list:
            thisvalue = [thisvalue]
        for each in thisvalue:
            if each is None:
                continue
            ret = get_xpath(each, elem_tree)
            if ret is not None:
                retdict[key] = ret


def do_the_job(jobdict, driver=None):
    job_template = {
        'JOB': {
            'SKU': '''//*[@id=\'addServices_feature_div\']//script[contains(@data-a-state,\'vas-common-vm\')]''',
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
                '//*[@id=\'addServices_feature_div\']//script[contains(@data-a-state,\'vas-common-vm\')]'],
            'price_type': ['//*[@id="onetimeOption"]/label/span',
                           '//*[@id="addon"]//i[contains(@class,\'addon\')]',
                           '//*[@id="burjActionPanelAddOnBadge"]'],
            'product_title': ['//span[@id="productTitle"]',
                              "//img[contains(@src,'title') and contains(@src,'error') and contains(@alt, 'orry')]/@alt"],
            'rating': '//span[@id="acrPopover"]/@title',
            'reviews': [
                '//div[@id="averageCustomerReviews_feature_div"]//a[contains(@id,"CustomerReviewLink")]/span[@id]',
                '//*[@id="averageCustomerReviews"]'],
            'shipping': ['//*[@id="ourprice_shippingmessage"]'],
            'style': ['//*[@id="variation_color_name"]',
                      '//*[@id="shelf-label-color_name"]'],
            'style2': ["//div[@id and contains(@class,'variation-dropdown')]//option[@id and @selected]",
                       '//div[@id="variation_size_name"]//div[@class]',
                       '//*[@id="shelf-label-size_name"]']},
        'URL': 'http://www.amazon.com/gp/product/{}?psc=1'.format(jobdict['PID']) if jobdict['URL'] is None else
        jobdict['URL'],
        'WEBSITE': 'Amazon'}

    try:
        retdict = fill_template(job_template)
        retwrapper = {
            'STATUS': 'SUCCESS',
            'PAYLOAD': json.dumps(retdict),
        }
    except:
        retwrapper = {
            'STATUS': 'FAIL',
            'PAYLOAD': json.dumps({'Reason': traceback.format_exc()}),
        }
    return retwrapper


if __name__ == '__main__':
    testdict = {"WEBSITE": "Amazon",
                "PID": "B007UI47PY",
                "SKU": "B007UI47PY",
                "URL": "https://www.amazon.com/gp/product/B007UI47PY/ref=s9_acsd_al_bw_c_x_2_w"}
    print(do_the_job(testdict))
