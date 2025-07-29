from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests
import re
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
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

allRow = country_table.find_elements(By.TAG_NAME, "tr")[1]
allCells = allRow.find_elements(By.TAG_NAME, "td")
allRate = allCells[2].text.split("%")[0]
allStatus = allCells[1].text.split("\n\n")[0].replace("\n", " ")
allReciprocal = (allRate, "Baseline " + allStatus)

countryMap = {}
rows = country_table.find_elements(By.TAG_NAME, "tr")
for row in rows[1:]:
    cells = row.find_elements(By.TAG_NAME, "td")
    if cells:
        country = cells[0].text
        countryRate = cells[2].text.split("%")[0]
        status = cells[1].text.split("\n\n")[0].replace("\n", " ")

        if "Threatened" in status:
            countryTuple = ('0', status + " - " + countryRate)
        else:
            if countryRate:
                countryTuple = (countryRate, country + " " + status)
            else:
                countryTuple = ('0', country)
        
        countryMap[country] = countryTuple

productMap = {}
rows = prod_table.find_elements(By.TAG_NAME, "tr")
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if cells:
        product = cells[0].text
        productMap[product] = row.get_attribute("outerHTML")

driver.quit()

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

def formatHTML(tableHTML):
    soup = BeautifulSoup(tableHTML, 'html.parser')
    headerRow, prodRow = soup.find_all("tr")

    headerCells = []
    for cell in headerRow.find_all("td"):
        headerCells.append(cell.get_text())

    prodDict = {}
    prodCells = prodRow.find_all("td")

    for i, cell in enumerate(headerCells):
        raw_html = prodCells[i].decode_contents()
        
        # Step 1: Replace all <br> or <br/> with a placeholder
        raw_html = re.sub(r'<br\s*/?>', '[[BR]]', raw_html, flags=re.IGNORECASE)

        # Step 2: Replace one or more [[BR]] with a single `;\n`
        raw_html = re.sub(r'(\[\[BR\]\]\s*)+', ';\n', raw_html)

        # Step 3: Clean up remaining HTML
        formatted = BeautifulSoup(raw_html, 'html.parser').get_text(separator=' ', strip=True)
        
        prodDict[cell] = formatted
    return prodDict

def getReciprocal(product_desc, country):

    countryReciprocal = countryMap[country]
    prompt = f"""
    You are a classification assistant.

    Categorize the following product description into **one of these categories**:
    {productSet}

    ### Rules:
    - Output **only** the category name from the list above — nothing else.
    - If the product description does **not** fit into any category, return **nothing** (empty string).

    Product description: "{product_desc}"
    """
    category = callOpenAI(prompt)
    if category == "Nothing":
        return [allReciprocal, countryReciprocal]
    
    html = productMap[category]
    table = formatHTML(productHeader + html)
    prompt = f""""
    You are a tariff data extractor.

    Your task is to extract the **most relevant and most recent** tariff for the product described below when imported from the given country, using the provided HTML table.

    Product description: **{product_desc}**
    Country of origin: **{country}**

    ### TABLE (includes column headers):
    {table.items()}

    ### Instructions:
    - Focus on the <td></td?(s) relevant to **{country}** and **{product_desc}**.
    - Review the **"Additional Information"** column to check for any exceptions or overrides:
        - “Reciprocal tariff exception”
        - “Not subject to tariffs”
        - Section 232 exclusions
    - If an exception applies, return a `tariff_rate:0` with the **reason included in status**.

    ### Output format (strictly):
    Return a **single line** in this exact format (no extra words or commentary):
    tariff_rate:<number only, no percent sign>~status:<full text from the status column>

    ### Examples:
    - `tariff_rate:10~status:Reciprocal tariff in effect since July 2025`
    - `tariff_rate:0~status:Not subject to tariffs under Section 232 exclusion`
    """
    prodReciprocal = callOpenAI(prompt)
    tariffRate, status = prodReciprocal.split('~')
    parsedTariff = tariffRate.split(':')[1]
    parsedStatus = status.split(':')[1]
    return [allReciprocal, countryReciprocal, (parsedTariff, category + " " + parsedStatus)]