import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

response = requests.get('https://ustr.gov/themes/custom/ustr2021/tariff/hts_new.json?offset=0&limit=10', verify=False)
data = response.json()  # Assuming this is a list of dicts

"""
Search for a 301 description by HTSUS code

Returns:
    tuple: (desc, note) or None if not found
"""
def get301Desc(code: str) -> tuple[str, ...]:
    for item in data:
        if str(item['HTS_id']) == code:
            desc = item['action_description']
            note = item['note']
            return (desc, note)
    return None

"""
Search for a 301 tariff by HTSUS code

Returns:
    str: percentage or 0.0% if not found/deleted
"""
def get301Percent(code: str) -> str:
    # Searches for code from API
    found = get301Desc(code)
    if not found:
        return "0.0%"
    
    # Checks to see if code was deleted
    desc, note = found[0], found[1]
    noteList = note.split(" ")
    for word in noteList:
        if word == "deleted":
            return "0.0"

    # Matches percentage from item string
    match = re.search(r'\d+(?:\.\d+)?%', desc)
    return match.group()

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
