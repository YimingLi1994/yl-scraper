import datetime as dt
import multiprocessing as mp
import time

import pytz


def ret_validation(ret_payload, retrynum, retry_lmt, distributed_num, distributed_lmt):
    if distributed_num > distributed_lmt:
        ret_payload['STATUS'] = 'Error: Max Job Distribution Time Limit Reached'
        return True
    if ret_payload['STATUS'] == 'SUCCESS':
        return True
    elif retrynum < retry_lmt:
        return False
    else:
        return True



def result_fetch(crawlqueue: mp.Queue,
                 uploadqueue: mp.Queue,
                 wait_dict: dict,
                 ret_dict: dict,
                 wait_loc: mp.Lock,
                 ret_loc: mp.Lock,
                 retry_lmt,
                 distributed_lmt,
                 timeout_sec
                 ):
    while True:
        timenow = dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None)
        with wait_loc:
            if len(wait_dict) != 0:
                with ret_loc:
                    while len(ret_dict) != 0:
                        (key, itm) = ret_dict.popitem()
                        try:
                            payload = wait_dict.pop(key)
                        except KeyError:
                            continue
                        if ret_validation(ret_payload = itm,
                                          retrynum = payload['retry'],
                                          retry_lmt= retry_lmt,
                                          distributed_num = payload['distributed'],
                                          distributed_lmt = distributed_lmt) is True:
                            uploadqueue.put(itm)
                        else:
                            payload['retry'] += 1
                            crawlqueue.put(payload)
                for key, itm in wait_dict.items():
                    if (timenow - dt.datetime.strptime(itm['DISTRIBUTED_TIME'],
                                                       '%Y-%m-%d %H:%M:%S')).seconds > timeout_sec:
                        delitem = wait_dict.pop(key)
                        crawlqueue.put(delitem)
        time.sleep(3)
