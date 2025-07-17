from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests

load_dotenv()
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

def callOpenAI(query: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": query
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        return chatbot_output
    else:
        return ("Error:", response.status_code, response.text)

driver = webdriver.Chrome()
driver.get("https://www.tradecomplianceresourcehub.com/2025/07/14/trump-2-0-tariff-tracker/")
time.sleep(2)

# Extract the table objects from driver
table = driver.find_elements(By.TAG_NAME, "table")
country_table, prod_table= table[0], table[1]


# Extract the list of products from table
prod_rows = prod_table.find_elements(By.TAG_NAME, "tr")
productSet = set()
for row in prod_rows[1:]:
    product = row.find_element(By.TAG_NAME,"td").text
    productSet.add(product)
productHeader = prod_rows[0].get_attribute("outerHTML")
'''
Returns base reciprocal rate(10%, status-dates)
'''
def getAllReciprocal() -> tuple[str, str]:
    allRow = country_table.find_elements(By.TAG_NAME, "tr")[1]
    allCells = allRow.find_elements(By.TAG_NAME, "td")
    allRate = allCells[2].text.split("%")[0]
    allStatus = allCells[1].text.split("\n\n")[0].replace("\n", " ")
    return (allRate, allStatus)

def getRecipricalByCountry(country) -> tuple[str, str]:
    rows = country_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == country:
            countryCells = row.find_elements(By.TAG_NAME, "td")
            countryRate = countryCells[2].text.split("%")[0]
            status = countryCells[1].text.split("\n\n")[0].replace("\n", " ")
            if "Threatened" in status:
                return (0, status + " - " + countryRate)
            else:
                return (countryRate, status)

def getReciprocalByProduct(product):
    rows = prod_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == product:
            return(row.get_attribute("outerHTML"))

def getReciprocal(product_desc, country):
    allReciprocal = getAllReciprocal()
    countryReciprocal = getRecipricalByCountry(country)
    prompt = f"""
    You are a classification assistant.

    Categorize the following product description into **one of these categories**:
    {productSet}

    ### Rules:
    - Output **only** the category name from the list above — nothing else.
    - If the product description does **not** clearly fit into any category, return **nothing** (empty string).

    Product description: "{product_desc}"
    """
    category = callOpenAI(prompt)
    print(category)
    if category == "Nothing":
        return [allReciprocal, countryReciprocal]
    
    html = getReciprocalByProduct(category)
    prompt = f""""
    You are a tariff data extractor.

    Extract the most relevant and ***recent*** tariff on **{product_desc}** imported from **{country}**, using the HTML table provided.

    ### Rules:
    - Consider the **"Additional Information"** column for **exceptions**, such as:
        - “Reciprocal tariff exception”
        - “Not subject to tariffs”
        - Section 232 exclusions
    - Return in this format with these exact fields:
    tariff_rate:<number, no percent sign>~status:<full summary in **status column**>

    HTML content:
    {productHeader}
    {html}
    """
    print(prompt)
    prodReciprocal = callOpenAI(prompt)
    tariffRate, status = prodReciprocal.split('~')
    parsedTariff = tariffRate.split(':')[1]
    parsedStatus = status.split(':')[1]
    return [allReciprocal, countryReciprocal, (parsedTariff, parsedStatus)]