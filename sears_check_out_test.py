import time
from selenium import webdriver
from selenium.common.exceptions import *
url='''http://www.sears.com/x/p-04680933000P'''

driver = webdriver.Chrome(executable_path="C:\\Users\\Jianw\\OneDrive\\work\\desktop_proj\\crawler_v2\\chromedriver_win32\\chromedriver.exe")
driver.get(url)

t = time.time()
while True:
	try:
		driver.find_element_by_xpath('''//figure[contains(@class,'productFulfillmentDeliveryPanel-page')]''').click()
		time.sleep(1)
		break
	except WebDriverException as e:
		time.sleep(0.1)
		if time.time()-t > 10:
			raise
t = time.time()
while True:
	try:
		driver.find_element_by_xpath('''//figure[contains(@class,'productFulfillmentDeliveryPanel-page')]//form[@class='submitLocationForm']/input''').send_keys('60656')
		time.sleep(1)
		break
	except WebDriverException as e:
		time.sleep(0.1)
		if time.time()-t > 10:
			raise
t = time.time()
while True:
	try:
		driver.find_element_by_xpath('''//figure[contains(@class,'productFulfillmentDeliveryPanel-page')]//form[@class='submitLocationForm']/button''').click()
		time.sleep(1)
		break
	except WebDriverException as e:
		time.sleep(0.1)
		if time.time()-t > 10:
			raise
t = time.time()
while True:
	try:
		driver.find_element_by_xpath('''//div[@class='productCartForm-page']//button''').click()
		time.sleep(1)
		break
	except WebDriverException as e:
		time.sleep(0.1)
		if time.time()-t > 10:
			raise
t = time.time()
while True:
    try:
        price = driver.find_element_by_xpath(
            '''//*[@id="miniCartContainer"]//div[@class="productOptionPrices"]//h3[@class="salePrice"]''').text
        print(price)
        time.sleep(1)
        break
    except WebDriverException as e:
        time.sleep(0.1)
        if time.time() - t > 10:
            raise
