from flask import Blueprint, jsonify, request
from tariffs.scraper301 import get301Percent, get301Desc
from tariffs.scraperVAT import getVAT 
from tariffs.landingCost import getLanding

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
        if not hts_code:
            prod_desc = data.get('prod_desc')
            # hts_code = getHTS(product_desc)

        country = data.get('country')

        # MRN = getMRN(hts_code, country)
        MRN = 0
        tax301 = 0
        if country == "China":
            # Removes all the . period char and last two digits
            cleaned_code = hts_code.replace(".", "")[:-2]
            tax301 = get301Percent(cleaned_code)
        
        taxVAT, link = getVAT(country)
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500