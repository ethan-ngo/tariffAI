import requests
from bs4 import BeautifulSoup

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