# htsus_classifier_gemini.py
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

def load_htsus_data(flattened_csv):
    htsus_dict = {}
    with open(flattened_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['HTS_Number'].strip()
            # Normalize codes by removing trailing dots/spaces if needed
            htsus_dict[code] = row
    return htsus_dict

# Extract HTS code and duty rate from Gemini output (adjust regex as needed)
def parse_gemini_output(text):
    hts_pattern = r'\b(\d{4}\.\d{2}\.\d{4})\b'
    duty_pattern = r'(\d+(?:\.\d+)?)%'

    hts_codes = re.findall(hts_pattern, text)
    duty_rates = re.findall(duty_pattern, text)

    list_of_pairs = list(zip(hts_codes, [rate + '%' for rate in duty_rates]))
    return list_of_pairs

# Check if Gemini's HTS code and duty match your data
def validate_classification(hts_code, duty, htsus_dict):
    if hts_code not in htsus_dict:
        return False
    
    local_row = htsus_dict[hts_code]
    
    # Check if duty matches any duty rate field (simple contains, case insensitive)
    duty_fields = ['General_Rate_of_Duty', 'Special_Rate_of_Duty', 'Column_2_Rate_of_Duty', 'Additional_Duties']
    for field in duty_fields:
        local_duty = local_row.get(field, '').strip()
        if local_duty and duty and duty in local_duty:
            return True
    
    return False

def get_hts_rows_by_codes(htsus_dict, hts_codes):
    return [htsus_dict[code] for code in hts_codes if code in htsus_dict]

def ask_gemini_to_validate(product_description, hts_rows):
    rows_text = "\n".join([
        f"{row['HTS_Number']}: {row['Full_Description']} | General Duty: {row['General_Rate_of_Duty'] or 'N/A'}"
        for row in hts_rows
    ])

    prompt_validation_file = "prompt_validate_gemini.txt"
    with open(prompt_validation_file, "r", encoding="utf-8") as f:
        prompt_validation_txt = f.read()

    prompt = "This is the product description: " + product_description + "\n\n" + "This is rows_text: " + rows_text + "\n\n" + "This is the prompt: " + prompt_validation_txt

    response = model.generate_content(prompt)
    
    try:
        return eval(response.text.strip())  # Or json.loads() if Gemini outputs real JSON
    except Exception as e:
        print("Failed to parse Gemini validation response:", e)
        return []

def find_hts_codes_by_keywords(input_csv, query, top_n=3):
    query_keywords = set(re.findall(r'\b\w+\b', query.lower()))

    matches = []

    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            description = row['Full_Description'].lower()
            desc_words = set(re.findall(r'\b\w+\b', description))
            match_score = len(query_keywords & desc_words)

            if match_score > 0:
                print("found a possible match with score ", match_score, " and hts code", row['HTS_Number'])
                matches.append((match_score, row))

    # Sort by best match score descending
    matches.sort(key=lambda x: x[0], reverse=True)

    # Return top N matches
    return [match[1] for match in matches[:top_n]]

def classify_with_validation(product_description, htsus_dict, max_attempts=2, delay=1):
    attempts = 3
    while attempts < max_attempts:
        attempts += 1

        # use gemini to classify the product_description
        gemini_response = classify_htsus(product_description)
        pairs = parse_gemini_output(gemini_response)

        if not pairs:
            print("Parsing failed, retrying...")
            time.sleep(delay)
            continue

        for hts_code, duty in pairs:
            print("HTS Code:", hts_code, "| Duty:", duty)

        # Load HTSUS rows for Gemini's suggestions
        hts_codes = [code for code, _ in pairs]
        print(f"hts_codes are {hts_codes}")
        hts_rows = get_hts_rows_by_codes(htsus_dict, hts_codes)

        print(f"hts_rows are {hts_rows}")

        if not hts_rows:
            print("No valid HTS codes found in local data, retrying...")
            time.sleep(delay)
            continue

        # Ask Gemini to verify its own answer
        validated = ask_gemini_to_validate(product_description, hts_rows)

        if validated:
            print(f"Valid classification(s) found on attempt {attempts}:")
            for entry in validated:
                print(f"- {entry['HTS_Code']} @ {entry['Duty']} — {entry['Reason']}")
            return validated, gemini_response
        else:
            print("Gemini says none of its suggestions match. Retrying...")
            time.sleep(delay)

        # res = []
        
        # for hts_code, duty in zip(hts_codes, duties):
        #     if hts_code and duty:
        #         if validate_classification(hts_code, duty, htsus_dict):
        #             print(f"Valid classification found on attempt {attempts}: {hts_code} with duty {duty}")
        #             # return hts_code, duty, gemini_response
        #             res.append((hts_code, duty))
        #         else:
        #             print(f"Attempt {attempts}: HTS code or duty mismatch, retrying...")
        #     else:
        #         print(f"Attempt {attempts}: Could not parse HTS code or duty, retrying...")
            
        #     time.sleep(delay)  # optional delay between retries

        # return res, gemini_response
    
    print("Max attempts reached, classification may be inaccurate. Directly search csv file for keywords.")
    
    find_hts_codes_by_keywords("htsus_flattened.csv", product_description, top_n=3)

    return None, None, "Max attempts reached"

def load_hts_descriptions(input_csv):
    descriptions = []
    rows = []
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Full_Description']:
                cleaned = re.sub(r'[^a-z0-9\s]', '', row['Full_Description'].lower())
                descriptions.append(cleaned)
                rows.append(row)
    return descriptions, rows

def find_hts_codes_tfidf(input_csv, query, top_n=5):
    descriptions, rows = load_hts_descriptions(input_csv)
    
    # # Add the user query to the list temporarily for TF-IDF
    # cleaned_query = re.sub(r'[^a-z0-9\s]', '', query.lower())
    # corpus = descriptions + [cleaned_query]
    
    # vectorizer = TfidfVectorizer(stop_words='english')
    # tfidf_matrix = vectorizer.fit_transform(corpus)

    # # Compare query vector to all description vectors
    # cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # # Get top N results by similarity
    # top_indices = cosine_sim.argsort()[::-1][:top_n]

    # return [(rows[i]['HTS_Number'], rows[i]['Full_Description'], cosine_sim[i]) for i in top_indices]

# Example usage
if __name__ == "__main__":
    # classify_htsus("Men 100 cotton denim jeans") # works! it outputted 6203.42.4011 & 16.6%; WRONG SHUD BE 6203.42.07.11
    # classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # classify_htsus("Smartphone with 128GB storage, OLED screen, and 5G support") # works! it outputted 8517.13.0000 & 0%
    # classify_htsus("Leather handbag") # works! it outputted the 3 possibilities shown in few_shot.txt
    # classify_htsus("Porcelain plate") # wrong! it outputted 6911.10.0000 and 2.9% instead of 6911.10.5200 and 25%
    # classify_htsus("Cordless drill") # wrong! it outputted 8467.21.0000 but 3.7% instead of 1.7%

    # TEST parse_gemini_output
    # res = classify_htsus("cotton plushie") # works! it outputted 9503.00.0073 & 0%
    # print(parse_gemini_output(res))
    # res = classify_htsus("Leather handbag") # works! it outputted 9503.00.0073 & 0%
    # print(parse_gemini_output(res))

    htsus_dict = load_htsus_data("htsus_flattened.csv")
    # This calls classify_with_validation which internally calls classify_htsus and retries if needed
    hts_code, duty, full_response = classify_with_validation("Men 100 cotton denim jeans", htsus_dict)

    results = find_hts_codes_tfidf("htsus_flattened.csv", "Men 100 cotton denim jeans", top_n=5)
for hts, desc, score in results:
    print(f"{hts} — {desc} (score: {score:.4f})")
