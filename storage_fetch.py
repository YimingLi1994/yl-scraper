from google.cloud import storage
from dateutil import tz
import google.cloud
import pandas as pd
import datetime as dt
import pytz
import time
import json
import myutil


def payload_check(inputdf):
    if 'payload' in inputdf.columns:
        return True
    else:
        return False


def listen_to_stoage(bucket_name, crawlqueue, sto_name_prefix):
    client = storage.Client('yl3573')
    bucket = client.bucket('yl-crawl')
    while True:
        jobdf = []
        retlst = myutil.list_file(bucket_name)
        for each in retlst:
            if sto_name_prefix in each.name and '.csv' in each.name:
                print(each.name)
                blob = bucket.blob(each.name)
                try:
                    blob.reload()
                except google.cloud.exceptions.NotFound:
                    continue
                timenow = (dt.datetime.now(pytz.timezone('America/Chicago'))).replace(tzinfo=None)
                if (timenow - blob.updated.astimezone(tz.tzlocal()).replace(tzinfo=None)).seconds < 40:
                    continue
                df = myutil.read_csv_from_sto(bucket_name + '/' + each.name)
                if payload_check(df) is True:
                    jobdf.append(df)
                each.delete()

        if len(jobdf) != 0:
            df_all = pd.concat(jobdf)
            val = df_all.values.flatten()
            for eachval in val:
                try:
                    payload_str = json.loads(eachval)
                    crawlqueue.put(payload_str)
                except ValueError:
                    print('Json Parse Error: {}'.format(str(eachval)))
                    continue
        time.sleep(60)

if __name__ == '__main__':
    from myprofile import profile as PROFILE
    import multiprocessing as mp
    from multiprocessing import Lock, Value
    chooseprofile = 'test_index'
    start_gcloud_worker = False

    if chooseprofile not in PROFILE:
        raise ValueError('Profile name not found')
    thisPROFILE = PROFILE[chooseprofile]
    receiver_port = thisPROFILE['receiver_server'][1]
    distributor_port = thisPROFILE['distributor_server'][1]
    status_port = thisPROFILE['status_server'][1]
    distributor_key = thisPROFILE['distributor_key']
    receiver_key = thisPROFILE['receiver_key']
    sto_prefix = 'yl-crawl_' + thisPROFILE['storage_name_filter']
    if start_gcloud_worker:
        vm_prefix = 'dp-crawler-' + thisPROFILE['vm_name_filter']
        if 'dp-crawler' not in vm_prefix:
            raise NameError('Worker name must start with dp-crawler')

    mp_manger = mp.Manager()
    job_queue = mp.Queue()
    wait_dict = mp_manger.dict()
    wait_lock = mp.Lock()  # Used to lock wait dict
    ret_dict = mp_manger.dict()
    ret_lock = mp.Lock()  # Used to lock ret dict
    upload_queue = mp.Queue()
    global_counter = Value('i', 0)
    speed_counter = mp_manger.dict()
    speed_counter['speed'] = 0
    speed_counter_lock = mp.Lock()
    counter_lock = mp.Lock()

    status_key = thisPROFILE['statuskey']
    timeout_sec = thisPROFILE['recycle_timeout']
    retry_lmt = thisPROFILE['retry_lmt']
    distributed_lmt = thisPROFILE['distribution_lmt']
    listen_to_stoage('yl-crawl', job_queue, sto_prefix)
