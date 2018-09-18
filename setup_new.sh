#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install wget -y
sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable xvfb -y
sudo apt-get install python3-dev python3-pip -y
sudo pip3 install pandas google-cloud-storage google-cloud-bigquery google-cloud-pubsub python-dateutil pytz jsonpath_ng lxml xvfbwrapper selenium


sudo pip3 install --upgrade urllib3

# how to keep login github
# create a image