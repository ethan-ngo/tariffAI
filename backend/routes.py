import re
from flask import Blueprint, jsonify, request
from tariffs.scraper301 import get301Percent, get301Desc
from tariffs.scraperVAT import getVAT, getVAT_AI 
from tariffs.landingCost import getLanding_MRN_rate, getLanding_MRN_amt
from htsus_classification.get_hts import get_final_HTS_duty
from htsus_classification.chatbot import workflow

from htsus_classification.htsus_classifier_openai import classify_htsus

main = Blueprint('main', __name__)

@main.route('/scraper/vat/<country>', methods=['GET'])
def scraper_vat(country):
    if not country:
        return jsonify({"error": "Missing 'country' parameter"}), 400
    try:
        vat = getVAT(country)
        if not vat:
            return jsonify({"error": "Country not found"}), 404
        tariff, link = vat
        return jsonify({"tariff": tariff, "link": link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/scraper/301/<code>', methods=['GET'])
def scraper_301(code):
    if not code:
        return jsonify({"error": "Missing 'code' parameter"}), 400
    try:
        percent = get301Percent(code)
        return jsonify({"percent": percent}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/scraper/301desc/<code>', methods=['GET'])
def scraper_301desc(code):
    if not code:
        return jsonify({"error": "Missing 'code' parameter"}), 400
    try:
        desc_tuple = get301Desc(code)
        if not desc_tuple:
            return jsonify({"error": "Code not found"}), 404
        desc, note = desc_tuple
        return jsonify({"description": desc, "note": note}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/landing', methods=['POST'])
def calcLanding():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"error": "Invalid or empty JSON"}), 400
    
    try:
        hts_code = str(data.get('hts_code'))
        country = data.get('country')
        prod_desc = data.get('prod_desc')
        weight = data.get('weight')
        weight_unit = data.get('weight_unit')
        quantity = data.get('quantity')

        try:
            MRN = get_final_HTS_duty(hts_code, country)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        MRN = MRN.strip().lower()
        MRN_rate = -1.0
        MRN_irregular_rate = -1.0
        MRN_total = -1.0

        if MRN == 'free':
            print("MRN is free, turning it to 0.0")
            MRN_rate = 0.0

        if "%" in MRN:
            print("mrn is regular: has percentage, extracting float")
            percent = float(MRN.replace("%", ""))
            MRN_rate = percent # return rate multipier

        # ¢ per kg
        match_cent_per_kg = re.match(r'([\d.]+)¢/kg', MRN)
        if match_cent_per_kg:
            # print("MRN is cents per kg")
            cents = float(match_cent_per_kg.group(1))
            print("cents: ", cents)
            MRN_irregular_rate = round(cents/100, 5)
            print("MRN_irregular_rate: ", MRN_irregular_rate, " and type ", type(MRN_irregular_rate))
            
            print("weight is ", weight, " and qty is ", quantity)
            float_weight = float(weight)
            float_quantity = float(quantity)
            MRN_total = (cents / 100) * float_weight * float_quantity # return dollar amt
            print("MRN_total: ", MRN_total, " and type ", type(MRN_total))

        # $ per kg
        match_dollar_per_kg = re.match(r'\$([\d.]+)/kg', MRN)
        if match_dollar_per_kg:
            print("MRN is dollars per kg")
            MRN_irregular_rate = float(match_dollar_per_kg.group(1))
            MRN_total = MRN_irregular_rate * weight * quantity # return dollar amt

        tax301 = 0.0
        if country == "China":
            # Removes all the . period char and last two digits
            cleaned_code = hts_code.replace(".", "")
            cleaned_code_new = ""

            if len(cleaned_code) == 10:
                cleaned_code_new = cleaned_code[:-2]
            else:
                cleaned_code_new = cleaned_code
    
            print("cleaned_code new: ", cleaned_code_new)
            tax301 = float(get301Percent(cleaned_code_new))
        
        taxVAT = getVAT_AI(country, prod_desc)
        if not taxVAT:
            taxVAT = 0

        print("VAT", taxVAT)

        prod_value = float(data.get('prod_value', 0))
        quantity = int(data.get('quantity', 1))
        shipping = float(data.get('shipping', 0))
        insurance = float(data.get('insurance', 0))

        print("tax301 type in calcLanding", type(tax301))
        # print("tax301:", tax301)

        print("MRN_rate is ", MRN_rate, " and irreg rate is ", MRN_irregular_rate, " and MRN_total is ", MRN_total)
        if MRN_rate == -1 and MRN_irregular_rate == -1 and MRN_total == -1:
            MRN_rate = 0

        # all of these floats should not be divided by 100 yet
        if MRN_rate != -1.0: # the duty tax is a rate
            landing_cost = getLanding_MRN_rate(prod_value, quantity, shipping, insurance, tax301, float(taxVAT), MRN_rate)
        elif MRN_total != -1.0: # the duty tax is an amount
            landing_cost = getLanding_MRN_amt(prod_value, quantity, shipping, insurance, tax301, float(taxVAT), MRN, MRN_total)
        
        return jsonify(landing_cost), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# helper function to get the final duty hts rates
def get_final_duty_hts_rates(classification_text):
    # Split by numbered sections, e.g. "1. HTSUS Code:", "2. HTSUS Code:", etc.
    blocks = re.split(r'\n?\d+\.\sHTSUS Code:', classification_text)

    # The first split element may be empty if string starts with "1. HTSUS Code:", so skip it
    blocks = [b.strip() for b in blocks if b.strip()]

    results = []

    for block in blocks:
        # Add back "HTSUS Code:" prefix removed by split
        block = "HTSUS Code:" + block

        # Extract HTSUS Code (number pattern after "HTSUS Code:")
        code_match = re.search(r'HTSUS Code:\s*([\d.]+)', block)
        total_rate_match = re.search(r'Total HTS Duty Tax Rate:\s*([\d.]+%)', block)

        if code_match and total_rate_match:
            code = code_match.group(1)
            total_rate = total_rate_match.group(1)
            results.append((code, total_rate))

    return results

# get hts from the chatbot
@main.route('/classifier/htsus', methods=['POST'])
def classify_htsus_path():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400
    try:
        product_description = data.get('product_description')
        if not product_description:
            return jsonify({"error": "Missing 'product_description' in JSON data"}), 400    
        origin_country = data.get('origin_country')
        if not origin_country:
            return jsonify({"error": "Missing 'origin_country' in JSON data"}), 400
        weight = data.get('weight')
        if not weight:
            return jsonify({"error": "Missing 'weight' in JSON data"}), 400  
        weight_unit = data.get('weight_unit')
        if not weight_unit:
            return jsonify({"error": "Missing 'weight_unit' in JSON data"}), 400  
        quantity = data.get('quantity')
        if not quantity:
            return jsonify({"error": "Missing 'quantity' in JSON data"}), 400  
        
        # print(f"product_description: {product_description}")
        # print(f"origin_country: {origin_country}")
        
        result = classify_htsus(product_description, origin_country, weight, weight_unit, quantity)

        if not result:
            return jsonify({"error": "Classification failed"}), 500 
        
        duty_taxes = get_final_duty_hts_rates(result)
        updated_duty_taxes = []

        for code, rate in duty_taxes:
            rate_float = float(rate.rstrip('%'))
            updated_duty_taxes.append((code, rate_float))

        return jsonify({"classification": result, "duty_rates": updated_duty_taxes}) 
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    
@main.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400
    try:
        res = workflow(data.get("message"))
        return jsonify({"message": res})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return