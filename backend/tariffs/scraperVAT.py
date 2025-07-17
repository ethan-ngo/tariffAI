import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

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
    prompt = f"""
    What is the best estimate of the VATrate in {target_country} for {prod_desc}?
    If multiple rates exist, choose the most typical or average one. The output should be a single number (e.g., 18.0) with no text or symbols.
    If the rate is not explicitly available, make a reasonable numeric estimate based on similar products or general VAT guidelines.
    """
    res = callOpenAI(prompt)
    return float(res.strip())