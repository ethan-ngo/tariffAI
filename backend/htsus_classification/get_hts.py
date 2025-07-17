import csv
import os
from dotenv import load_dotenv
import pycountry

AGREEMENT_CODE_TO_COUNTRIES = {
    "A": [
    ],
    "A*": [
    ],
    "A+": [
    ],
    "AU": ["AU"],
    "B": ["CA"], # canada via apta
    "BH": ["BH"],
    "C": [],
    "CA": ["CA"],
    "CL": ["CL"],
    "CO": ["CO"],
    "D": [
        "AO","BJ","BW","CV","CF","TD","KM","CG","CD","DJ",
        "EG","ER","ET","GM","GH","GN","GW","KE","LS","LR",
        "MG","MW","ML","MR","MZ","NA","NE","NG","RW","ST",
        "SN","SL","SO","SS","SZ","TZ","TG","UG","ZM"
    ],
    "E": [
        "AG","AI","AN","BS","BB","BZ","KY","DM","DO","GD",
        "GT","HT","JM","MS","NI","PA","PR","KN","LC","VC",
        "TT"
    ],
    "E*": [],
    "IL": ["IL"],
    "J": ["BO","CO","EC","PE"],
    "J*": [],
    "J+": ["BO","CO","EC","PE"],
    "JO": ["JO"],
    "JP": ["JP"],
    "K": ["K"],
    "KR": ["KR"],
    "L": ["L"],
    "MA": ["MA"],
    "MX": ["MX"],
    "OM": ["OM"],
    "P": ["CR","DO","SV","GT","HN","NI","PA"],
    "P+": ["CR","DO","SV","GT","HN","NI","PA"],
    "PA": ["PA"],
    "PE": ["PE"],
    "R": ["BB", "BZ", "DM", "DO", "GD", "GT", "GY", "HT", "HN", "JM", "KN", "LC", "NI", "PA", "VC", "TT"],
    "SG": ["SG"],
    "S": ["CA", "MX"],  # USMCA/US, Canada, Mexico
    "S+": ["CA", "MX"],
}

# commonly ambiguous country names
manual_map = {
    "korea": "KR",  # Default South Korea
    "south korea": "KR",
    "republic of korea": "KR",
    "north korea": "KP",
    "democratic people's republic of korea": "KP",
    "congo": "CG",  # Republic of Congo by default
    "democratic republic of the congo": "CD",
    "ivory coast": "CI",
    "côte d'ivoire": "CI",
    "russia": "RU",
    "russian federation": "RU",
    "syria": "SY",
    "syrian arab republic": "SY",
    "vietnam": "VN",
    "viet nam": "VN",
    "united states": "US",
    "usa": "US",
    "united states of america": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "palestine": "PS",
    "palestinian territories": "PS",
    "taiwan": "TW",
    "taiwan, province of china": "TW",
    "macedonia": "MK",
    "north macedonia": "MK",
    "venezuela": "VE",
    "bolivarian republic of venezuela": "VE",
    "brunei": "BN",
    "brunei darussalam": "BN",
    "czech republic": "CZ",
    "czechia": "CZ",
    "cape verde": "CV",
    "cabo verde": "CV",
    "east timor": "TL",
    "timor-leste": "TL",
    "laos": "LA",
    "lao people's democratic republic": "LA",
    "moldova": "MD",
    "republic of moldova": "MD",
    "myanmar": "MM",
    "burma": "MM",
    "state of palestine": "PS",
    "st kitts and nevis": "KN",
    "saint kitts and nevis": "KN",
    "st vincent and the grenadines": "VC",
    "saint vincent and the grenadines": "VC",
    "united arab emirates": "AE",
    "uae": "AE",
    "swaziland": "SZ",
    "eswatini": "SZ",
    "vatican": "VA",
    "holy see": "VA",
    "svalbard and jan mayen": "SJ",
    "uk": "GB",
}

load_dotenv()

# Set up the environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
csv_path = os.path.join(BASE_DIR, "data", "htsus_flattened_with_chapters.csv")
prompt_path = os.path.join(BASE_DIR, "prompts", "prompt_get_final_HTS_duty.txt")

url = os.getenv("OPENAI_URL")
api_key = os.getenv("OPENAI_API_KEY")

# remove all '.' and make it 10 digits
def normalize_hts_number(hts_number: str) -> str:
    # Remove all dots
    normalized = hts_number.replace('.', '')
    # Add '00' if length is 8 digits to make it 10 digits
    if len(normalized) == 8:
        normalized += '00'
    # If already 10 digits, do nothing
    return normalized

# get the whole htsus row from the hts number
def find_hts_row(csv_path: str, hts_number: str):
    target_hts = normalize_hts_number(hts_number)

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

# use fuzzy search to get country code
def get_country_code(name):
    name_lower = name.strip().lower()

    # account for commonly ambiguous names
    name_lower = name.strip().lower()
    if name_lower in manual_map:
        return manual_map[name_lower]

    country = pycountry.countries.get(name=name)
    if country:
        print("returning ", country.alpha_2)
        return country.alpha_2
    
    # Try fuzzy search if exact match fails
    try:
        matches = pycountry.countries.search_fuzzy(name)
        if matches:
            print("fuzzy returning ", matches[0].alpha_2)
            return matches[0].alpha_2
    except LookupError:
        pass

    return None

# determine the duty rate given a htsus row and origin country
def determine_duty_rate(hts_row: dict, origin_country: str) -> str:
    general_duty = hts_row.get("General Rate of Duty", "").strip()
    special_duty = hts_row.get("Special Rate of Duty", "").strip()
    column2_duty = hts_row.get("Column 2 Rate of Duty", "").strip()
    additional_duty = hts_row.get("Additional Duties", "").strip()

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
    
    # Special case: Column 2 countries (e.g., North Korea, Cuba)
    if country_code.strip().upper() in {"KP", "CU"}:
        print("country is KP or CU")
        base_duty = column2_duty if column2_duty else ""
    else:
        print("not KP or CU")
        # Determine if Special Rate applies
        special_applies = False
        if "(" in special_duty and ")" in special_duty:
            codes_in_parens = special_duty.split("(")[-1].rstrip(")").split(",")
            codes_in_parens = [c.strip() for c in codes_in_parens]

            # Check if the country code matches any country under any of these agreement codes
            for code in codes_in_parens:
                countries_for_code = AGREEMENT_CODE_TO_COUNTRIES.get(code, [])
                if country_code in countries_for_code:
                    special_applies = True
                    print(f"Special applies via agreement code: {code}")
                    break
                
        # Also check if the country code appears directly in the list (fallback)
        if not special_applies and country_code in codes_in_parens:
            special_applies = True
            print("Special applies via direct country code match")

        # Determine base duty
        if special_applies:
            base_duty = special_duty.split(" ")[0]  # e.g., "Free"
        else:
            base_duty = general_duty

        # Normalize "Free"
        if base_duty.lower() == "free":
            base_duty = "0%"

    # Append additional duties
    if additional_duty:
        base_duty += f" + {additional_duty}"

    return base_duty

# get the final hts duty given the htsus code and origin country
def get_final_HTS_duty(input_hts, origin_country):
    matched_row = find_hts_row(csv_path, input_hts)

    if matched_row: 
        rate = determine_duty_rate(matched_row, origin_country)
        return rate
    else:
        print("HTS number not found.")
        return ""

if __name__ == "__main__": 
    # print(get_final_HTS_duty("0302.23.00", "Mexico"))
    pass
