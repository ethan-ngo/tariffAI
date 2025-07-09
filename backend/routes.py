from flask import Blueprint, jsonify, request
from tariffs.scraper301 import get301Percent, get301Desc
from tariffs.scraperVAT import getVAT, getVAT_AI 
from tariffs.landingCost import getLanding

from htsus_classification.htsus_classifier_openai import classify_htsus
import re
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
        hts_code = [str(data.get('hts_code'))]
        country = data.get('country')

        prod_desc = data.get('prod_desc')
        if not hts_code:
            prod_desc = data.get('prod_desc')
            hts_classification_output = classify_htsus(prod_desc, country) 

            # res is array of tuples in format: ("htsus_code", duty_tax float)
            res = get_final_duty_hts_rates(hts_classification_output)

        # MRN = getMRN(hts_code, country)
        MRN = 0
        tax301 = 0
        if country == "China":
            # Removes all the . period char and last two digits
            cleaned_code = hts_code.replace(".", "")[:-2]
            tax301 = get301Percent(cleaned_code)
        
        taxVAT = getVAT_AI(country, prod_desc)
        if not taxVAT:
            taxVAT = 0

        prod_value = float(data.get('prod_value', 0))
        quantity = int(data.get('quantity', 1))
        shipping = float(data.get('shipping', 0))
        insurance = float(data.get('insurance', 0))

        landing_cost = getLanding(prod_value, quantity, shipping, insurance, tax301, float(taxVAT), MRN)
        print("VAT", taxVAT)
        print("Landing:" , landing_cost)
        return jsonify({"landing_cost": landing_cost}), 200
        # return jsonify({"description": desc, "note": note})
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
    return