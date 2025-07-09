import csv
import os
import requests
from dotenv import load_dotenv
import pycountry

load_dotenv()

def normalize_hts_number(hts_number: str) -> str:
    print("entered normalize_hts func")
    print("hts_number received:", hts_number)

    # Remove all dots
    normalized = hts_number.replace('.', '')
    # Add '00' if length is 8 digits to make it 10 digits
    if len(normalized) == 8:
        normalized += '00'
    # If already 10 digits, do nothing
    print("normalized code is: ", normalized)
    return normalized

def find_hts_row(csv_path: str, hts_number: str):
    print("entered find_hts_row")
    target_hts = normalize_hts_number(hts_number)
    print("target_hts is: " + target_hts)

    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Normalize CSV hts_number as well to compare
            row_hts = row['HTS_Number'].replace('.', '')
            if len(row_hts) == 8:
                row_hts += '00'
            if row_hts == target_hts:
                return row  # Return the matching row as dict
    return None  # If no match found

def is_valid_country_code(code):
    return pycountry.countries.get(alpha_2=code.upper()) is not None

def get_country_code(name):
    country = pycountry.countries.get(name=name)
    if country:
        return country.alpha_2
    
    # Try fuzzy search if exact match fails
    try:
        matches = pycountry.countries.search_fuzzy(name)
        if matches:
            return matches[0].alpha_2
    except LookupError:
        pass

    return None

def determine_duty_rate(hts_row: dict, origin_country: str) -> str:
    general_duty = hts_row.get("General Rate of Duty", "").strip()
    special_duty = hts_row.get("Special Rate of Duty", "").strip()
    column2_duty = hts_row.get("Column 2 Rate of Duty", "").strip()
    additional_duty = hts_row.get("Additional Duties", "").strip()

    print("gen: ", general_duty, "special: ", special_duty, "col2: ", column2_duty, "additional: ", additional_duty)

    # Normalize origin_country (e.g., "China" => "CN")
    country_code = ""
    if len(origin_country) == 2:
        if not is_valid_country_code(origin_country):
            print("not valid country code")
            return 
        country_code = origin_country.upper()
    else: 
        country_code = get_country_code(origin_country)

    if not country_code:
        print("country code not found")
        return
    
    country_code = country_code.strip()

    print("Country code is ", country_code)
    
    # Special case: Column 2 countries (e.g., North Korea, Cuba)
    if country_code.strip().upper() in {"KP", "CU"}:
        print("country is KP or CU")
        base_duty = column2_duty if column2_duty else ""
    else:
        print("not KP or CU")
        # Determine if Special Rate applies
        special_applies = False
        if "(" in special_duty and ")" in special_duty:
            print("checking special duty countries")
            codes_in_parens = special_duty.split("(")[-1].rstrip(")").split(",")
            codes_in_parens = [c.strip() for c in codes_in_parens]
            if country_code in codes_in_parens:
                special_applies = True
                print("Special applies")

        # Determine base duty
        if special_applies:
            base_duty = special_duty.split(" ")[0]  # e.g., "Free"
            print("special applies")
        else:
            base_duty = general_duty
            print("general duty applies")
            print("base_duty: ", base_duty)

        # Normalize "Free"
        if base_duty.lower() == "free":
            base_duty = "0%"

    # Append additional duties
    if additional_duty:
        base_duty += f" + {additional_duty}"

    return base_duty

# Set up the environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
csv_path = os.path.join(BASE_DIR, "data", "htsus_flattened_with_chapters.csv")
prompt_path = os.path.join(BASE_DIR, "prompts", "prompt_get_final_HTS_duty.txt")

url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

def get_final_HTS_duty(input_hts, origin_country):
    print("entered get_final_HTS_duty func")
    matched_row = find_hts_row(csv_path, input_hts)

    if matched_row: 
        # print("Found HTS row:", matched_row)
        rate = determine_duty_rate(matched_row, origin_country)
        print("final duty rate is ", rate)
        return rate
    else:
        print("HTS number not found.")
        return ""

if __name__ == "__main__": 
    print(get_final_HTS_duty("0102.29.40", "Brazil"))
