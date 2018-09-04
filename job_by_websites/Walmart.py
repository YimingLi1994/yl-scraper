import json
import traceback
from io import StringIO
import lxml.html as lh
import requests
# from jsonpath_ng import
from jsonpath_ng.ext import parse
import string
import re
__all__ = ["do_the_job"]

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
    with open('walmartcheck.html','w') as f:
        f.write((ready_str))
    elem_tree = lh.parse(StringIO(ready_str))
    xpath = '''//*[@id = 'atf-content']'''
    elemlst = elem_tree.xpath(xpath)
    if len(elemlst) == 0:
        elemlst = re.findall('window.__WML_REDUX_INITIAL_STATE__ *= *({.*});',ready_str,re.MULTILINE|re.DOTALL)
        if len(elemlst) == 0:
            raise RuntimeError('Cannot find xpath:{} or __WML_REDUX_INITIAL_STATE__'.format(xpath))
        else:
            printable = set(string.printable)
            clean_str = ''.join(filter(lambda x: x in printable, elemlst[0]))
    else:
        printable = set(string.printable)
        clean_str=''.join(filter(lambda x: x in printable,elemlst[0].text))
    elemdict = json.loads(clean_str)
    return elemdict


def do_the_job(jobdict, driver=None):
    def getoffer(offerid, elemdict):
        return parse('$..product.offers."{}"'.format(offerid)).find(elemdict)[0].value

    #jobdict = json.loads(payload_json)
    PID = jobdict['PID']
    URL = jobdict['URL']
    SKU = None
    if URL is None:
        URL = 'https://www.walmart.com/ip/{}'.format(PID)
    try:
        elemdict = get_content(URL)
        reportback = \
        list(filter(lambda x: x.value['usItemId'] == '{}'.format(PID), parse('$..product.products.*').find(elemdict)))[
            0].value
        if 'offers' in reportback:
            reportback['offers_feched'] = [getoffer(x, elemdict) for x in reportback['offers']]
        else:
            reportback['offers_feched'] = None

        retwrapper = {
            'STATUS':'SUCCESS',
            'PAYLOAD': json.dumps(reportback),
        }
    except:
        retwrapper = {
            'STATUS': 'FAIL',
            'PAYLOAD': json.dumps({'Reason':traceback.format_exc()}),
        }
    return retwrapper


if __name__ == '__main__':
    testdict = {"WEBSITE":"Walmart",
                "PID": "124269570",
                "SKU": "124269570",
                "URL": "https://www.walmart.com/ip/Round-Center-Cubic-Zirconia-Ring-Sterling-Silver-925/124269570"}
    print(do_the_job(testdict))