import os
from dotenv import load_dotenv
import requests

load_dotenv()
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

def determineIntent(query: str) -> str:
    return

def workflow(query):
    userIntent = determineIntent(query)
    if userIntent == "HTS_Classifcation":
        # Call AI function
        return
    elif userIntent == "General HTS Questions":
        # GPT API call with different prompt
        return
    
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


    
    