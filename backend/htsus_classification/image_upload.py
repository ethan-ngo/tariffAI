import requests
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("IMAGE_URL")
api_key = os.getenv("OPENAI_API_KEY")

def predictImage(file):

    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        'API-Package': 'DFIS_AI_Related',
        "Accept": "application/json"
    }

    files = {
    'content': file
    }
    response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        return response.json()['predictions'][0]
    else:
        return ("Error:", response.status_code, response.text)
