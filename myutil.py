from google.cloud import storage
import google.cloud
import time
import sys
import pandas as pd
import io

def read_csv_from_sto(fullpath, retry=2):
    try_cnt = 0
    rule_df = None
    while try_cnt < retry:
        try:
            sto_client = storage.Client('yl3573')
            bucketname = fullpath.split('/')[0]
            blobpath = '/'.join(fullpath.split('/')[1:])
            bucket = sto_client.bucket(bucketname)
            blob = bucket.blob(blobpath)
            rule_data = blob.download_as_string()
            rule_df = pd.read_csv(io.BytesIO(rule_data), encoding='utf8')
            break
        except google.cloud.exceptions.NotFound:
            return None
        except google.cloud.exceptions.GoogleCloudError:
            try_cnt += 1
            time.sleep(1)
            continue
    return rule_df

def save_csv_to_sto(fullpath, projname, df, retry=5):
    try_cnt = 0
    while try_cnt < retry:
        try:
            sto_client = storage.Client(projname)
            bucketname = fullpath.split('/')[0]
            blobpath = '/'.join(fullpath.split('/')[1:])
            bucket = sto_client.bucket(bucketname)
            blob = bucket.blob(blobpath)
            blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
            break
        except google.cloud.exceptions.GoogleCloudError:
            print(sys.exc_info())
            try_cnt += 1
            time.sleep(1)
            continue
    print('Done')

def list_file(bucket_name):
    retlst = []
    try:
        sto_client = storage.Client('yl3573')
        bucketname = bucket_name
        bucket = sto_client.bucket(bucketname)
        retlst = list(bucket.list_blobs())
    except google.cloud.exceptions.GoogleCloudError:
        pass
    finally:
        return retlst

def delete_file(fullpath, projname):
    try:
        sto_client = storage.Client(projname)
        bucketname = fullpath.split('/')[0]
        blobpath = '/'.join(fullpath.split('/')[1:])
        bucket = sto_client.bucket(bucketname)
        blob = bucket.blob(blobpath)
        blob.delete()
    except google.cloud.exceptions.GoogleCloudError:
        pass
