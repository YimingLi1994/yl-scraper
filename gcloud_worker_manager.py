import datetime as dt
import importlib
import json
import math
import os
import random
import socket
import subprocess as sp
import time
import uuid
from multiprocessing.pool import ThreadPool as Pool

import pytz
from dateutil import parser, tz


def delete_vm(del_vm_lst):
    pass
    # shellstr = '''sudo gcloud compute instances delete {name} --zone {zone} --quiet --project yl3573''' \
    #     .format(name=vm_namelst, zone=zone)
    # sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)


def runshell(shellstr):
    a = sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
    print(shellstr)
    return a.returncode


class ServerManager():
    def init(self, profilename=None, IP=None, PORT=None, key=None, vm_name_filter=None, startup_script=None,
             conversion_rate=None, vm_lmt=None, vm_lifecycle=None, first_time=True):
        if profilename is None and first_time:
            raise RuntimeError('Please input profile name')
        if profilename is not None:
            self.profilename = profilename
        if IP is not None:
            self.server = IP
        if PORT is not None:
            self.port = PORT
        if key is not None:
            self.key = key
        self.zonelst = [
            'us-central1-c',
            'us-central1-b',
            'us-central1-a',
            'us-east1-b',
            'us-east1-d',
            'us-east1-c',
            'us-west1-a',
            'us-west1-b',
            'us-west1-c'
        ]
        if conversion_rate is not None:
            self.conversion = conversion_rate
        if vm_lifecycle is not None:
            self.lifecycle = vm_lifecycle  # in min
        if first_time:
            self.currentVMdict = {}
            self.currentRunAmt = 0
            self.deletelst = []
            self.thistotaljob_size = 0
            self.server_clr_counter = 0
            self.server_clr_limit = 1
        if vm_name_filter is not None:
            self.vm_name_filter = vm_name_filter
        if startup_script is not None:
            self.startup_script = startup_script
        if vm_lmt is not None:
            self.vm_lmt = vm_lmt

    def __init__(self, thisprofilename, IP, PORT, key, vm_name_filter, startup_script, conversion_rate, vm_lmt, vm_lifecycle):
        self.init(thisprofilename, IP, PORT, key, vm_name_filter, startup_script, conversion_rate, vm_lmt, vm_lifecycle,
                  True)

    def maintainserver(self):
        while True:
            myprofile = importlib.import_module('myprofile')
            PROFILE = myprofile.profile
            thisPROFILE = PROFILE[self.profilename]
            self.init(conversion_rate=thisPROFILE['conversion_rate'],
                      vm_lmt=thisPROFILE['vm_lmt'], vm_lifecycle=thisPROFILE['vm_lifecycle'], first_time=False)

            status_dict = self.server_status()
            if status_dict is not None:
                # print(status_dict)
                if status_dict["job_queue"] == 0:
                    totalvmamt = 0
                else:
                    totalvmamt = min(math.ceil(max(status_dict["job_queue"], self.conversion * 10) / self.conversion),
                                     self.vm_lmt)
                self.thistotaljob_size = max(self.thistotaljob_size, totalvmamt)
                if status_dict["job_queue"] == 0 and status_dict["waitDict"] == 0 \
                        and len(self.currentVMdict) != 0:  # Currently running
                    self.server_clr_counter += 1
                else:
                    self.server_clr_counter = 0
                self.batchnum = math.ceil(self.thistotaljob_size / 800)
                if self.batchnum == 0:
                    self.eachbatch = 0
                else:
                    self.eachbatch = self.thistotaljob_size // self.batchnum
                # print(self.batchnum)
                # print(self.eachbatch)
                shellstr = '''sudo gcloud compute instances list --project yl3573 --format json'''
                retcode = sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE, )
                # retcode = sp.run(shellstr, stdout=sp.PIPE, stderr=sp.PIPE, shell = True)
                if retcode.returncode == 0:
                    vm_dict = json.loads(retcode.stdout.decode('ascii', 'ignore'))
                    currentrunlst = []
                    for item in vm_dict:
                        if self.vm_name_filter in item['name']:
                            thisname = item['name']
                            if thisname not in self.currentVMdict:
                                dt1 = parser.parse(item['creationTimestamp'])
                                dt1 = dt1.astimezone(tz.tzlocal())
                                dt1 = dt1.replace(tzinfo=None)
                                vm_dict_tt = {'name': thisname,
                                              'zone': item['zone'],
                                              'creation_dt': dt1
                                              }
                                self.currentVMdict[thisname] = vm_dict_tt
                            if item['status'] == 'TERMINATED':
                                self.deletelst.append(vm_dict_tt)
                                if thisname in self.currentVMdict:
                                    self.currentVMdict.pop(thisname)
                            else:
                                currentrunlst.append(thisname)
                    key_pop_lst = []
                    for key, item in self.currentVMdict.items():
                        if key not in currentrunlst:
                            key_pop_lst.append(key)
                    for eachkey in key_pop_lst:
                        self.currentVMdict.pop(eachkey)
                    if len(currentrunlst) < self.batchnum * self.eachbatch:
                        self.createserver(self.batchnum * self.eachbatch - len(currentrunlst))
                    timenow = dt.datetime.now(pytz.timezone('America/Chicago')).replace(tzinfo=None)
                    key_pop_lst = []
                    for key, itm in self.currentVMdict.items():  # delete vm overtime
                        if (timenow - itm['creation_dt']).seconds > self.lifecycle * 60:
                            self.deletelst.append(itm)
                            key_pop_lst.append(key)
                    for eachkey in key_pop_lst:
                        self.currentVMdict.pop(eachkey)
                    self.delserver()
                if self.server_clr_counter > self.server_clr_limit:
                    self.clear_all()
            if len(self.currentVMdict) != 0:
                time.sleep(10)
            else:
                time.sleep(60)

    def delserver(self):
        zonedict = {}
        runningshelllist = []
        for eachitem in self.deletelst:
            if eachitem['zone'] not in zonedict:
                zonedict[eachitem['zone']] = []
            zonedict[eachitem['zone']].append(eachitem['name'])
        for key, item in zonedict.items():
            name_str = ' '.join(item)
            shellstr = '''sudo gcloud compute instances delete {name} --zone {zone} --quiet --project yl3573''' \
                .format(name=name_str, zone=key)
            runningshelllist.append(shellstr)
        with Pool(4) as pool:
            pool.map(runshell, runningshelllist)
        self.deletelst = []

    def createserver(self, amt):
        each_batch_size = self.eachbatch
        res = amt
        while res > 0:
            thisbatch = min(res, each_batch_size)
            res = res - thisbatch
            while True:
                namelst = []
                thiszone = self.zonelst[random.randint(0, len(self.zonelst) - 1)]
                for idx in range(thisbatch):
                    namelst.append(
                        '{nameprefix}-{id}'.format(nameprefix=self.vm_name_filter, id=str(uuid.uuid4())[-6:]))
                createstr = '''sudo gcloud compute instances create {machinename} --preemptible --zone {zone} --scopes https://www.googleapis.com/auth/cloud-platform --machine-type n1-standard-1 --image=crawler --metadata-from-file startup-script={start_up_script} --project yl3573''' \
                    .format(start_up_script='{}/{}'.format(os.path.dirname(os.path.abspath(__file__)),
                                                           self.startup_script),
                            machinename=' '.join(namelst), zone=thiszone)
                retcode = sp.run(createstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
                if 'created' in retcode.stderr.decode('ascii', 'ignore').lower():
                    print('Successfully created')
                    break
                else:
                    print('Failed, retry')
                    print(retcode.stderr)
                    time.sleep(5)

    def clear_all(self):
        '''
        All Finished clean up
        '''
        self.thistotaljob_size = 0
        runningshelllist = []
        shellstr = '''sudo gcloud compute instances list --project yl3573 --format json'''
        vm_dict = None
        for idx in range(5):
            retcode = sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
            if retcode.returncode == 0:
                vm_dict = json.loads(retcode.stdout.decode('ascii', 'ignore'))
                break
            time.sleep(10)
        if vm_dict is None:
            return
        dellst = []
        for item in vm_dict:
            if self.vm_name_filter in item['name']:
                dellst.append(item)
        zonedict = {}
        for eachitem in dellst:
            if eachitem['zone'] not in zonedict:
                zonedict[eachitem['zone']] = []
            zonedict[eachitem['zone']].append(eachitem['name'])
        for key, item in zonedict.items():
            name_str = ' '.join(item)
            shellstr = '''sudo gcloud compute instances delete {name} --zone {zone} --quiet --project yl3573''' \
                .format(name=name_str, zone=key)
            # print(shellstr)
            # sp.run(shellstr.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
            runningshelllist.append(shellstr)
            with Pool(10) as pool:
                pool.map(runshell, runningshelllist)

    def server_status(self):
        data_dict = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server, self.port))
                sendstr = 'GET /?key={}'.format(self.key)
                s.sendall(sendstr.encode('ascii'))
                data = s.recv(4096).decode('ascii', 'ignore')
            try:
                data_lst = data.split()
                if data_lst[1] == str(200):
                    real_data = ''.join(data_lst[3:])
                    data_dict = json.loads(real_data)
            except ValueError as e:
                data_dict = None
                print(e)
        except TimeoutError as e:
            data_dict = None
            print(e)
        finally:
            return data_dict


if __name__ == '__main__':
    import sys

    myprofile = importlib.import_module('myprofile')
    PROFILE = myprofile.profile

    profilename = sys.argv[1]
    thisPROFILE = PROFILE[profilename]
    HOST = thisPROFILE['status_server'][0]
    PORT = thisPROFILE['status_server'][1]
    key = thisPROFILE['statuskey']
    startup_script = thisPROFILE['start_up_script']
    vm_name_filter = 'dp-crawler-' + thisPROFILE['vm_name_filter']
    mymanager = ServerManager(profilename,HOST, PORT, key, vm_name_filter, startup_script,
                              conversion_rate=thisPROFILE['conversion_rate'],
                              vm_lmt=thisPROFILE['vm_lmt'],
                              vm_lifecycle=thisPROFILE['vm_lifecycle'])
    print('gcloud manager started')
    mymanager.maintainserver()
