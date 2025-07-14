from selenium import webdriver
from selenium.webdriver.common.by import By
import time
driver = webdriver.Chrome()
driver.get("https://www.tradecomplianceresourcehub.com/2025/07/14/trump-2-0-tariff-tracker/")
time.sleep(2)
rows = driver.find_elements(By.TAG_NAME, "tr")
# TODO: Create function for returning effective date
def getBaseReciprocal():
    firstRow = rows[1]
    tariffRate = firstRow.find_elements(By.TAG_NAME, "td")[2]
    cleanedRate = tariffRate.text[0:3]
    return cleanedRate

# TODO: Check to see if reciprocal is effective vs threatened/rescinded
def getRecipricalByCountry(country):
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text == country:
            print(cells[2].text.replace(" ", "").split("%")[0])

getBaseReciprocal()
driver.quit()