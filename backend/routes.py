import re
from flask import Blueprint, jsonify, request
from tariffs.scraper301 import get301Percent, get301Desc
from tariffs.scraperVAT import getVAT, getVAT_AI 
from tariffs.landingCost import getLanding_MRN_rate, getLanding_MRN_amt
from htsus_classification.get_hts import get_final_HTS_duty
from htsus_classification.chatbot import workflow
from htsus_classification.chapter99 import getReciprocal
from flask import Flask, request, jsonify

from htsus_classification.htsus_classifier_openai import classify_htsus, get_final_duty_hts_rates

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
    # get data from the tariff form
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

        # base duty (MRN) calculation
        try:
            # get the base duty based on the htsus and country
            MRN = get_final_HTS_duty(hts_code, country)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # process the base duty (formatted as xx% or xx cents/kg)
        MRN = MRN.strip().lower()
        MRN_rate = -1.0
        MRN_irregular_rate = -1.0
        MRN_total = -1.0

        # process the base duty rate
        if MRN == 'free':
            print("MRN is free, turning it to 0.0")
            MRN_rate = 0.0

        if "%" in MRN:
            print("mrn is regular: has percentage, extracting float")
            percent = float(MRN.replace("%", ""))
            MRN_rate = percent # return rate multipier

        # ¢ per kg
        match_cent_per_kg = re.match(r'([\d.]+)¢/kg', MRN)
        cents = 0
        if match_cent_per_kg:
            # print("MRN is cents per kg")
            cents = float(match_cent_per_kg.group(1))
            print("cents: ", cents)
            MRN_irregular_rate = round(cents/100, 5)
            print("MRN_irregular_rate: ", MRN_irregular_rate, " and type ", type(MRN_irregular_rate))
            
            # weight unit conversion
            converted_weight = 0
            if weight_unit == "kg":
                converted_weight = weight
            elif weight_unit == "lb":
                converted_weight = weight * 0.453592      # 1 lb = 0.453592 kg
            elif weight_unit == "g":
                converted_weight = weight / 1000          # 1 g = 0.001 kg
            elif weight_unit == "oz":
                converted_weight = weight * 0.0283495     # 1 oz = 0.0283495 kg
            elif weight_unit == "ton":
                converted_weight = weight * 1000          # 1 metric ton = 1000 kg
            else:
                raise ValueError(f"Unsupported weight unit: {weight_unit}")
        
            print("weight is ", converted_weight, " and qty is ", quantity)
            float_weight = float(converted_weight)
            float_quantity = float(quantity)
            MRN_total = (cents / 100) * float_weight * float_quantity # return dollar amt
            print("MRN_total: ", MRN_total, " and type ", type(MRN_total))

        # ¢ per liter
        match_cent_per_liter = re.search(r'([\d.]+)¢\s*/\s*L\b', MRN, re.IGNORECASE)
        cents = 0
        if match_cent_per_liter:
            cents = float(match_cent_per_liter.group(1))
            print("cents: ", cents)
            MRN_irregular_rate = round(cents / 100, 5)
            print("MRN_irregular_rate: ", MRN_irregular_rate, " and type ", type(MRN_irregular_rate))
            
            # volume unit conversion
            converted_volume = 0
            if weight_unit == "kg":
                converted_volume = weight  # treat as liters
            elif weight_unit == "lb":
                converted_volume = weight * 0.453592  # 1 lb → ~0.453 L (assume 1:1 density approx)
            elif weight_unit == "g":
                converted_volume = weight / 1000      # 1 g = 0.001 L
            elif weight_unit == "oz":
                converted_volume = weight * 0.0295735 # 1 oz ≈ 29.57 mL = 0.02957 L
            elif weight_unit == "ton":
                converted_volume = weight * 1000      # 1 metric ton = 1000 L (approximation)
            else:
                raise ValueError(f"Unsupported volume unit: {weight_unit}")
            
            print("volume is ", converted_volume, " and qty is ", quantity)
            float_volume = float(converted_volume)
            float_quantity = float(quantity)
            MRN_total = (cents / 100) * float_volume * float_quantity  # return dollar amt
            print("MRN_total: ", MRN_total, " and type ", type(MRN_total))

        
        # get the tax301 if the country is China
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
        
        # get the VAT tax based on the country and prod description
        taxVAT = getVAT_AI(country, prod_desc)
        if not taxVAT:
            taxVAT = 0

        print("VAT", taxVAT)

        # VAT source
        res = getVAT(country)
        print("res is ", res)
        VAT_link = res[1]

        print("VAT_link is", VAT_link)

        # get reciprocal taxes
        taxes_date = getReciprocal(prod_desc, country)
        taxes_float_date = []

        for pair in taxes_date:
            tax_float = float(pair[0].strip('%'))
            if tax_float != 0.0:
                taxes_float_date.append((tax_float,pair[1]))
        print(taxes_float_date)

        # convert other values to float
        prod_value = float(data.get('prod_value', 0))
        quantity = int(data.get('quantity', 1))
        shipping = float(data.get('shipping', 0))
        insurance = float(data.get('insurance', 0))

        print("tax301 type in calcLanding", type(tax301))
        # print("tax301:", tax301)

        print("MRN_rate is ", MRN_rate, " and irreg rate is ", MRN_irregular_rate, " and MRN_total is ", MRN_total)
        if MRN_rate == -1 and MRN_irregular_rate == -1 and MRN_total == -1:
            MRN_rate = 0

        # get the total landed cost
        # all of these floats should not be divided by 100 yet
        if MRN_rate != -1.0: # the duty tax is a rate
            landing_cost = getLanding_MRN_rate(prod_value, quantity, shipping, insurance, tax301, float(taxVAT), VAT_link, MRN_rate, taxes_float_date)
        elif MRN_total != -1.0: # the duty tax is an amount
            landing_cost = getLanding_MRN_amt(prod_value, quantity, shipping, insurance, tax301, float(taxVAT), VAT_link, MRN, MRN_total, cents, converted_weight, weight_unit, taxes_float_date)
        
        print("returning landed cost")
        
        # return landed cost
        return jsonify(landing_cost), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        
        result = classify_htsus(product_description, origin_country, weight, weight_unit, quantity)

        if not result:
            return jsonify({"error": "Classification failed"}), 500 
        
        duty_taxes = get_final_duty_hts_rates(result)
        updated_duty_taxes = []

        for code, rate in duty_taxes:
            if rate == "Free" or rate == "free":
                rate_float = 0.0
            else:
                rate_float = float(rate.rstrip('%'))

            print("appending code ", code, " and rate ", rate_float)
            updated_duty_taxes.append((code, rate_float))

        print("updated duty taxes are ", updated_duty_taxes)

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