import os
from dotenv import load_dotenv
import requests
from .htsus_classifier_openai import classify_htsus
from tariffs.scraper301 import get301Desc
from tariffs.scraperVAT import getVAT
from .get_hts import get_final_HTS_duty

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


def determineIntent(query: str) -> str:
    prompt = f"""
    You are a classification assistant trained to assign user questions to exactly one of four categories.

    You must return only one of the following formats, depending on the input. Your response must **not contain any quotation marks, parentheses, or extra explanation**.

    ### Output Categories:

    1. HTS_Classification,product_description,country,weight,weight_unit,quantity
    → Use when the user asks to classify a product or calculate duties.
    → Example: HTS_Classification,leather shoes,Italy,2,kg,10

    2. General HTS Questions
    → Use for general questions about HTS structure, headings, duties, or rules.
    → Example: General HTS Questions

    3. VAT rate,country
    → Use when the user asks for a country's VAT rate.
    → Example: VAT rate,Germany

    4. 301 rate,hts_code_no_periods
    → Use when the user asks about Section 301 or China tariffs.
    → Clean the HTS code by removing periods and trimming or padding to 8 digits.
    → Example: 301 rate,61091000

    5. Duty Rate, hts_code, country
    → Use when the user wants to know about the duty rate of a code.
    → Example: Duty Rate,3303.00.3000, China

    ### Final Rule:
    Your response must be plain text. Do **not** include any quotation marks (`"`), parentheses (`()`), brackets (`[]`), or additional comments. Return only the selected class and required values in **exactly the format above**.
    If there is enough information to determine a class prompt, but not enough information to fill the parameters. Prompt the user for the neccesary information.
    Now classify the following input:
    {query}
    """
    res = callOpenAI(prompt)
    return res

def workflow(query):
    print(query)
    userIntent = determineIntent(query)
    print(userIntent)
    output = "I am unable to answer"

    if "HTS_Classifcation" in userIntent:
        _, prod_desc, country, weight, weight_unit, quantity = [x.strip() for x in userIntent.split(',')]
        classification_result = classify_htsus(prod_desc, country, weight, weight_unit, quantity)
        output = f"HTSUS Classification for '{prod_desc}' from {country}:\n{classification_result}"

    elif userIntent == "General HTS Questions":
        prompt = f"""
        You are an intelligent customs assistant specializing in the Harmonized Tariff Schedule of the United States (HTSUS). Your job is to accurately and clearly answer general questions related to:

        - HTS code structure and formatting
        - Classification rules (e.g., General Rules of Interpretation)
        - Duty rates, MFN, Section 301 tariffs, and reciprocal tariffs
        - Chapter and heading meanings
        - Subheadings and legal notes
        - How to classify items based on description or material
        - Country of origin effects
        - Anti-dumping and countervailing duties (AD/CVD)
        - VAT and total landed cost concepts

        Instructions:
        - Answer clearly and factually.
        - If a specific HTS code is mentioned, explain its structure or meaning.
        - For duty rates or special tariffs (e.g., 301, reciprocal), cite their purpose and how they’re applied.
        - If a concept is not related to HTSUS (e.g., EU VAT laws), respond politely that it's outside your scope.

        When unsure or if no info is available, say:
        “I’m sorry, I don’t have that information based on the HTSUS.”

        Avoid:
        - Guessing or fabricating HTS codes
        - Providing legal or binding advice
        
        Now classify the following input:
        {query}
        """
        output = callOpenAI(prompt)

    elif "VAT rate" in userIntent:
        country = userIntent.split(',')[1]
        res = getVAT(country)
        output = f'{res[0]}<br><br>Source: <a href="{res[1]}" target="_blank">{res[1]}</a>'
    elif "301 rate" in userIntent:
        code = userIntent.split(',')[1]
        res = get301Desc(code)
        output = res[0]
        if res[1]:
            output += "<br><br>" + res[1]
    
    elif "Duty Rate" in userIntent:
        _, code, country = userIntent.split(',')
        dutyRate = get_final_HTS_duty(code, country)
        output = dutyRate

    return output

