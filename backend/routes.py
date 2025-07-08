from flask import Blueprint, jsonify
from tariffs.scraper301 import get301Percent, get301Desc
from tariffs.scraperVAT import getVAT 
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
        return jsonify({"tariff": tariff, "link": link})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/scraper/301/<code>', methods=['GET'])
def scraper_301(code):
    if not code:
        return jsonify({"error": "Missing 'code' parameter"}), 400
    try:
        percent = get301Percent(code)
        return jsonify({"percent": percent})
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
        return jsonify({"description": desc, "note": note})
    except Exception as e:
        return jsonify({"error": str(e)}), 500