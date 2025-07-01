import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
response = requests.get('https://ustr.gov/themes/custom/ustr2021/tariff/hts_new.json?offset=0&limit=10', verify=False)
data = response.json()  # Assuming this is a list of dicts
search_code = 85016101

found = False
for item in data:
    if item['HTS_id'] == search_code:
        print(item)
        found = True
        break

if not found:
    print("Code not found")
    
# driver = webdriver.Chrome()
# driver.get("https://ustr.gov/issue-areas/enforcement/section-301-investigations/search")
# time.sleep(2)
# HTSUS = "84328000"
# input_box = driver.find_element(By.ID, "searchbox")
# input_box.send_keys(HTSUS)

# search_button = driver.find_element(By.CLASS_NAME, "bsearch")
# search_button.click()
# print(driver.find_elements(By.CLASS_NAME, "documents"))
# time.sleep(200)
