#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install python3-pip

# maintenance jobs required
pip3 install pytz
sudo apt-get install libmysqlclient-dev
sudo apt-get install python-dev
pip3 install mysqlclient
pip3 install numpy
pip3 install pandas
pip3 install croniter

# gcloud packages
pip3 install google-cloud-storage
pip3 install google-cloud-bigquery

# for scraping
pip3 install tqdm
pip3 install jsonpath-ng
pip3 install pandas-gbq
pip3 install setuptools
pip3 install google-cloud-pubsub

pip3 install selenium
