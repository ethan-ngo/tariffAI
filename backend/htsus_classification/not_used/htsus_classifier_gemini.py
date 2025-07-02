# htsus_classifier_openai.py
import os
import csv
import re
import time
import google.generativeai as genai
import csv
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set your API key (replace with your actual key or set as an environment variable)
GENAI_API_KEY = "AIzaSyBmN2rOQVvZ8gOHFz6H8Pfe7hORZpDRE6U "

# Configure Gemini
genai.configure(api_key=GENAI_API_KEY)

# Initialize Gemini Flash model
model = genai.GenerativeModel("gemini-2.0-flash")

# Few-shot prompt template for HTSUS classification along with the CSV file path
csv_file = "htsus.csv"
prompt_file = "prompt_gemini.txt"
few_shot_file = "few_shot.txt"

# Uses Gemini Flash to get the HTSUS code and duty tax for a given product description
def classify_htsus(product_description):
    # Step 1: Load prompt template
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_txt = f.read()

    # Step 2: Load few-shot examples
    with open(few_shot_file, "r", encoding="utf-8") as f:
        few_shot_txt = f.read()

    # Step 3: Load official HTSUS codes, descriptions, and tax rates from CSV file
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_txt = f.read()

    # full_prompt = f"This is the product description: {product_description}\n\nThis is htsus.csv:{csv_txt}\n\nThis is few_shot.txt{few_shot_txt}\n\n{prompt_txt}"
    full_prompt = f"This is the product description: {product_description}\n\nThis is few_shot.txt{few_shot_txt}\n\n{prompt_txt}"

    # Step 4: Generate response using Gemini Flash
    response = model.generate_content(full_prompt)
    # response = model.generate_content("Output the word hello")

    # Step 5: Print the response and return it
    print(response.text.strip())

    return response.text.strip()


# Example usage
if __name__ == "__main__":
    # classify_htsus("Men 100 cotton denim jeans") # works! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # works! it outputted 8517.13.0000 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    # classify_htsus("Porcelain plate") # wrong! it outputted 6911.10.0000 and 2.9% instead of 6911.10.5200 and 25%
    # classify_htsus("Cordless drill") # wrong! it outputted 8467.21.0000 but 3.7% instead of 1.7%
    pass 