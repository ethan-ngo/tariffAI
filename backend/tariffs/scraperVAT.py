import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

response = requests.get("https://taxsummaries.pwc.com/quick-charts/value-added-tax-vat-rates", verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find("table")

"""
Search for VAT tariff by country

Returns:
    tuple: (tariff percent, link to source) or None if not found
"""
def getVAT(target_country: str) -> tuple[str, str]:
    for row in table.find_all("tr"):
        country_link = row.find("a")
        if country_link and target_country.lower() in country_link.text.lower():
            vat_cell = row.find("td", style="width: 35vw")
            if vat_cell:
                tariff = vat_cell.text.strip()
                if tariff == "NA":
                    tariff = "0.0"
                link = country_link.get("href")
                return (tariff, link)
    return None

def getVAT_AI(target_country: str, prod_desc: str) -> float:
    res = model.generate_content(contents=f"What is the VAT rate of {target_country} for {prod_desc}? The output should only be a number.")
    return float(res.text.strip())