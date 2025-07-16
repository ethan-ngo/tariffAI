from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
url = os.getenv("OPENAI_URL")  # e.g. https://your-custom-openai.com/v1

driver = webdriver.Chrome()
driver.get("https://www.tradecomplianceresourcehub.com/2025/07/14/trump-2-0-tariff-tracker/")
time.sleep(2)

# Extract the table objects from driver
table = driver.find_elements(By.TAG_NAME, "table")
country_table, prod_table= table[0], table[1]

# Extract the base reciprocal row for all countries
allRowHTML = country_table.find_elements(By.TAG_NAME, "tr")[1].get_attribute("outerHTML")

def getRecipricalByCountry(country):
    rows = country_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == country:
            print(row.get_attribute("outerHTML"))

def getReciprocalByProduct(product):
    rows = country_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == product:
            print(row.get_attribute("outerHTML"))
            
getRecipricalByCountry("China")
driver.quit()

# input_text = f"""
# Extract all relevant tariff information for China.
# Format as JSON with keys: counter_measure, scope, tariff_rate, status.

# HTML content:
# {table_html}
# """

# headers = {
#         "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
#         "Content-Type": "application/json",
#         "Accept": "application/json"
#     }
# data = {
#     "text": input_text
# }

# response = requests.post(url, headers=headers, json=data)
# output = response.json().get("text")
# print(output)