#! /bin/bash
sudo -u jianwei.xiao git clone git@scraperv2.github.com:sears-harlem125/scraper_v2.git /home/jianwei.xiao/crawler
sudo chmod +x /home/jianwei.xiao/crawler/chromedriver_linux64/chromedriver
cd /home/jianwei.xiao/crawler
sudo -u jianwei.xiao python3 worker_job_index.py general_scraping 3 &> logfile.txt
