#! /bin/bash
sudo -u jianwei.xiao git clone git@scraperv2.github.com:sears-harlem125/scraper_v2.git /home/jianwei.xiao/crawler
sudo chmod +x /home/jianwei.xiao/crawler/chromedriver_linux64/chromedriver
cd /home/jianwei.xiao/crawler
sudo -H pip3 install -U pip
sudo -H pip3 install -U setuptools
sudo -H pip3 install lxml google-cloud-storage==1.6.0
sudo -u jianwei.xiao python3 worker_job_index.py custom_scraping 3
