import datetime as dt
import multiprocessing as mp
import sys
import time
import traceback
import pandas as pd
import pytz
import uuid
from google.cloud import pubsub_v1
import json

def ret_wrapper(res, collst):
    retlst = [None] * len(collst)
    for idx, col in enumerate(collst):
        if col in res:
            retlst[idx] = res[col]
    return retlst


def upload(df, datestr):
    succflag = False
    retry_attempt = 10
    while succflag is False and retry_attempt > 0:
        try:
            df.to_gbq('scraping.recv_raw_{}'.format(datestr), 'yl3573-214601', if_exists='append')
            succflag = True
        except KeyboardInterrupt:
            raise
        except:
            retry_attempt -= 1
            print(traceback.format_exc())
    if retry_attempt == 0:
        try:
            filename = str(uuid.uuid4()) + '.csv'
            df.to_csv('./error_bucket/{}'.format(filename),index=False)
        except:
            print(traceback.format_exc())

def publish_messages(publisher, topic_path, data):
    """Publishes multiple messages to a Pub/Sub topic."""
        # Data must be a bytestring
    data = data.encode('utf-8')
    publisher.publish(topic_path, data=data)

def jsonwrapper(data, succ_collst):
    retdict = {}
    for eachcol in succ_collst:
        if eachcol in data:
            retdict[eachcol] = data[eachcol]
        else:
            retdict[eachcol] = None
    return json.dumps(retdict)


def wrapper(res_queue: mp.Queue):
    succ_collst = [
        'WEBSITE',
        'URL',
        'PID',
        'SKU',
        'TAG',
        'STATUS',
        'PAYLOAD',
        'LAST_CRAWL',
    ]

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path('yl3573-214601', 'scraper_result')
    while True:
        data=res_queue.get()
        datastr = jsonwrapper(data, succ_collst)
        print("Sending")
        publish_messages(publisher, topic_path, datastr)

