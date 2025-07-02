# htsus_classifier_openai.py
import os
import csv
import re
import time
import csv
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
import chromadb


# Load environment variables from .env file
load_dotenv()

# Set up the environment
# DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="htsus_codes") # My HTSUS collection

# Get the key
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

# Few-shot prompt template for HTSUS classification along with the CSV file path
# csv_file = "htsus.csv"
prompt_file = "prompt_openai.txt"
few_shot_file = "few_shot.txt"

# Uses Gemini Flash to get the HTSUS code and duty tax for a given product description
def classify_htsus(product_description):
    # Step 1: Load prompt template
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_txt = f.read()

    # Step 2: Load few-shot examples
    with open(few_shot_file, "r", encoding="utf-8") as f:
        few_shot_txt = f.read()

    # Step 3: Retrieve relevant HTSUS codes from ChromaDB
    results = collection.query(
        query_texts=[product_description],
        n_results=5  # get top 5 most relevant chunks
    )
    # retrieved_docs = results['documents']
    retrieved_docs = results['documents'][0]  # Flatten one level
    
    # full_prompt = f"This is the product description: {product_description}\n\nThis is htsus.csv:{csv_txt}\n\nThis is few_shot.txt{few_shot_txt}\n\n{prompt_txt}"
    # full_prompt = f"This is the product description: {product_description}\n\nThis is few_shot.txt{few_shot_txt}\n\nThis is the prompt: {prompt_txt}\n\nThese are the data of the HTSUS codes to choose from: Here is the data:{chr(10).join(retrieved_docs)}"
    full_prompt = (
        f"Product description:\n{product_description}\n\n"
        f"Few-shot examples:\n{few_shot_txt}\n\n"
        f"Instructions:\n{prompt_txt}\n\n"
        "HTSUS data to choose from:\n"
        + "\n---\n".join(retrieved_docs)
    )

    

    # Step 4: Generate response using OpenAI 
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "text": full_prompt
    }

    response = requests.post(url, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        print("Simplified result:", response.json())
        # response_json = response.json()  # Parse the JSON response
        # chatbot_output = response_json.get("text", "")  # Get the "text" field safely
        # print("Simplified result:", chatbot_output)
    else:
        print("Error:", response.status_code, response.text)

# Example usage
if __name__ == "__main__":
    classify_htsus("Men 100 cotton denim jeans") # works! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # works! it outputted 8517.13.0000 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    # classify_htsus("Porcelain plate") # wrong! it outputted 6911.10.0000 and 2.9% instead of 6911.10.5200 and 25%
    # classify_htsus("Cordless drill") # wrong! it outputted 8467.21.0000 but 3.7% instead of 1.7%
    