# python_scraper_distributed
Hello :)

## Introduction
This is a general job distribution tool which can distribute job out into thousands of gcloud premptive vms
This framework is error tolerable


## Installation

## Structure

## Getting Started
### Set up profile.py first
Job is defined by profile so you can set the master node know what you want to do.

Example of a valid profile.py entry:
```python
'test_no_proxy' : {   ### profile name need to be typed in the command shell in order to activate this profile   
    'status_server' : ['127.0.0.1', 10055], ### Status_server IP and PORT, used to control google cloud VMs
    'distributor_server' : ['127.0.0.1', 10056], ### Job distributor server
    'receiver_server' : ['127.0.0.1', 10057], ### Result receiver server
    'vm_name_filter' : 'test-proxy', ### VM name prefix, Caution when dealing with this, make sure the name so that you won't delete any other vms 
    'storage_name_filter' : 'test', ### Name filter in the storage
    'start_up_script' : 'start_up_script.sh.sh', ### start_up_script for creating a vm
    'distributor_key' : 'aewrkjwearofikjwsewthewldamnmrykqwoaslxmnzvp40ekt85kj',  # distributor key
    'receiver_key' : 'agwreaeg$KLZ!@}Kwthnwstrgarfga4', # receiver key 
    'statuskey' : '23rafaerfargareg', # status server key
}
```

### Standalone mode:
```bash
python index.py [profile_name] local-worker [worker_number]
```
### Google Cloud Server mode:
- Prerequisite:
    - Google cloud SDK and api access on Google Cloud Compute Engine
    - 
- Note that this command will create standard-1 preemptive vms in google cloud 
based on the number in the job distribution queue, maximum number of vm is 2000
```bash
python index.py [profile_name]
```


### Server only mode:
```bash
python index.py [profile_name] no-worker
```


## Feature



