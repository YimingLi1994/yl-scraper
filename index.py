import datetime as dt
import multiprocessing as mp
import os
import sys
import time
from multiprocessing import Lock, Value

import pytz

import job_distributor  # Distribute payload to workers
import receiver  # Receive result from workers
import result_fetch  # Analyize result from workers
import status_server
import storage_fetch  # FETCH CSV FROM STORAGE
import wrapper  # UPLOAD TO BIGQUERY
from myprofile import profile as PROFILE
import platform

def main(chooseprofile, start_gcloud_worker):
    if chooseprofile not in PROFILE:
        raise ValueError('Profile name not found')
    thisPROFILE = PROFILE[chooseprofile]
    receiver_port = thisPROFILE['receiver_server'][1]
    distributor_port = thisPROFILE['distributor_server'][1]
    status_port = thisPROFILE['status_server'][1]
    distributor_key = thisPROFILE['distributor_key']
    receiver_key = thisPROFILE['receiver_key']
    sto_prefix = 'crawl_job_' + thisPROFILE['storage_name_filter']
    if start_gcloud_worker:
        vm_prefix = 'dp-crawler-' + thisPROFILE['vm_name_filter']
        if 'dp-crawler' not in vm_prefix:
            raise NameError('Worker name must start with dp-crawler')
    status_key = thisPROFILE['statuskey']
    timeout_sec = thisPROFILE['recycle_timeout']
    retry_lmt = thisPROFILE['retry_lmt']
    distributed_lmt = thisPROFILE['distribution_lmt']

    # Start Program


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

    mp.Process(target=job_distributor.server_distributor,
               args=(distributor_port, distributor_key, job_queue, wait_dict, wait_lock)).start()

    mp.Process(target=storage_fetch.listen_to_stoage,
               args=('yl-crawl', job_queue, sto_prefix)).start()

    mp.Process(target=receiver.server_receiver,
               args=(receiver_port, receiver_key, global_counter, counter_lock, ret_dict, ret_lock)).start()

    mp.Process(target=result_fetch.result_fetch,
               args=(job_queue, upload_queue, wait_dict, ret_dict, wait_lock, ret_lock, retry_lmt, distributed_lmt,
                     timeout_sec)).start()

    mp.Process(target=wrapper.wrapper, args=(upload_queue,)).start()

    mp.Process(target=status_server.status_server,
               args=(status_port, wait_dict, ret_dict, global_counter, speed_counter,
                     job_queue, upload_queue, status_key)).start()
    if start_gcloud_worker is True:
        import subprocess as sp

        shelllst = ['python3', '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), 'gcloud_worker_manager.py'),
                    chooseprofile]
        sp.Popen(shelllst)

    print('all started')
    while True:
        starttime = dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None)
        base = int(global_counter.value)
        time.sleep(30)
        print('Wait dict: '+str(len(wait_dict)) + ' ------ Ret dict: '+str(len(ret_dict)))# + ' ---- uploadQueue: ' + str(upload_queue.qsize()))
        endtime = dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None)
        secs = (endtime - starttime).seconds
        upper = int(global_counter.value)
        with speed_counter_lock:
            speed_counter['speed'] = (upper - base) / secs


if __name__ == '__main__':
    chooseprofile = sys.argv[1]
    runserver = True
    gcloudmanager = False
    proc = None
    if len(sys.argv) > 2:
        if sys.argv[2] not in ('no-worker', 'local-worker-only', 'gcloud-worker', 'local-worker'):
            raise NameError('Unknown parameter')
        if sys.argv[2] == 'gcloud-worker':
            gcloudmanager = True

        if sys.argv[2] in ('local-worker', 'local-worker-only'):
            import subprocess as sp

            workernum = sys.argv[3]
            if platform.system() == 'Windows' or platform.system() == 'Linux':
                shelllst = ['python', 'worker_job_index.py', chooseprofile, workernum]
                proc = sp.Popen(shelllst, shell=True)
            elif platform.system() == 'Darwin':
                shelllst = ['python3', 'worker_job_index.py', chooseprofile, workernum]
                proc = sp.Popen(shelllst)
            if sys.argv[2] == 'local-worker-only':
                runserver = False
    if runserver is True:
        main(chooseprofile, gcloudmanager)
    else:
        proc.wait()
