sudo apt-get update
sudo apt-get install python3-venv python3-pip -y
python3 -m venv ./dp_scraper_master
mkdir ./dp_scraper_master/dp_scraper
source ./dp_scraper_master/bin/activate
cd ./dp_scraper_master/dp_scraper
pip install -U pip
pip install -U setuptools
pip install google-cloud-storage google-cloud-bigquery pandas pandas-gbq pytz

source ./dp_scraper_master/bin/activate
cd ./dp_scraper_master/dp_scraper
python index.py HA_scraping gcloud-worker
python index.py amazon_scraping gcloud-worker
python index.py general_scraping gcloud-worker
python index.py slow_scraping gcloud-worker
python index.py amz_flash gcloud-worker

sudo gcloud auth login
sudo gcloud auth application-default login
sudo gcloud config set account jianwei.xiao@searshc.com
sudo gcloud config set project yl3573

/home/jianwei.xiao/.config/