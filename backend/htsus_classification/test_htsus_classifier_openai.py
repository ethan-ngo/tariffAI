import os
import re
from htsus_classifier_openai import classify_htsus

test_cases = [
    ("Men 100 cotton denim jeans", ["6203.42.4011", "6203.42.07.11"]),
    ("cotton plushie", ["9503.00.0073", "9503.00.00.71"]),
    ("Frozen Alaskan Salmon fillets, 1kg pack", ["0304.87.0000"]),
    ("Polyester camping tent, 4-person capacity, waterproof", ["6306.22.9030"]),
    ("grand piano", ["9201.10.0000"]),
    ("Electric bicycle with 500W motor and 48V battery", ["8711.60.0090"]),
    ("LED TV", ["8528.72.6400"]),
    ("Leather handbag", ["4202.21.9000", "4202.21.6000", "4202.21.8090"]),
    ("Porcelain plate", ["6911.10.5200", "6911.10.8000"]),
    ("Cordless drill", ["8467.21.0010", "8467.21.0030"]),
    ("Queen-sized bed sheet set made from 100% cotton", ["6302.21.9020"]),
    ("Dark chocolate bars with 85 cocoa, no filling", ["1806.32.9000"]),
    ("Office chair with adjustable height and wheels", ["9401.30.8030"]),
    ("Industrial-grade ethyl alcohol (denatured), for cleaning", ["2207.20.0000"]),
    ("Women's athletic shoes with rubber soles and textile uppers", ["6404.11.9030"]),
    ("women's leather sandals", ["6403.59.9060"]),
    ("Men's wool suit jacket", ["6203.31.0010"]),
    ("Children's plastic toy blocks", ["9503.00.0090"]),
    ("Stainless steel kitchen knife", ["8211.92.9030"]),
    ("Bluetooth wireless headphones", ["8518.30.2000"]),
    ("Ceramic coffee mug", ["6912.00.4810"]),
    ("Men's cotton t-shirt", ["6109.10.0012"]),
    ("Women's silk scarf", ["6214.10.2000"]),
    ("Plastic water bottle, 1 liter", ["3924.10.4000"]),
    ("Aluminum camping cookware set", ["7615.10.9100"]),
    ("Children's picture book", ["4903.00.0000"]),
    ("Smartphone with 128GB storage, OLED screen, and 5G support", ["8517.13.0000"]),
    ("Men's leather wallet", ["4202.31.6000"]),
    ("Women's wool sweater", ["6110.11.0030"]),
    ("Men's cotton socks", ["6115.95.9000"]),
    ("Plastic garden hose, 25 feet", ["3917.32.0050"]),
    ("Electric hair dryer", ["8516.31.0000"]),
    ("Children's wooden rocking horse", ["9503.00.0080"]),
    ("Men's polyester necktie", ["6215.20.0000"]),
    ("Women's cotton dress", ["6204.42.4056"]),
    ("Men's leather belt", ["4203.30.0000"]),
    ("Ceramic floor tile", ["6907.90.0050"]),
    ("Men's wool overcoat", ["6201.11.0010"]),
    ("Plastic food storage container", ["3924.10.4000"]),
    ("Men's cotton boxer shorts", ["6207.11.0000"]),
    ("Women's leather boots", ["6403.91.9041"]),
    ("Children's cotton pajamas", ["6207.21.0000"]),
    ("Men's silk tie", ["6215.10.0000"]),
    ("Women's polyester blouse", ["6206.40.3030"]),
    ("Men's wool hat", ["6505.90.4090"]),
    ("Plastic toy action figure", ["9503.00.0073"]),
    ("Men's cotton shorts", ["6203.42.4056"]),
    ("Women's leather purse", ["4202.22.1500"]),
    ("Men's cotton handkerchief", ["6213.20.1000"]),
    ("Women's wool skirt", ["6104.51.0000"]),
]

def extract_htsus_codes(text):
    # Extract all codes in the format NNNN.NN.NNNN or NNNN.NN.NN.NN
    return re.findall(r"\b\d{4}\.\d{2}(?:\.\d{2,4})?\b", text)

def run_tests():
    results = []
    passed = 0
    for idx, (desc, expected_codes) in enumerate(test_cases, 1):
        print(f"Test {idx}: {desc}")
        try:
            # classify_htsus prints and writes output, but we want to capture the return value
            # We'll assume it writes to 'final_output.txt' as in your code
            classify_htsus(desc)
            with open("final_output.txt", "r", encoding="utf-8") as f:
                output = f.read()
            found_codes = extract_htsus_codes(output)
            found = any(code in found_codes for code in expected_codes)
            if found:
                passed += 1
            results.append({
                "desc": desc,
                "expected": expected_codes,
                "found": found_codes,
                "pass": found
            })
        except Exception as e:
            results.append({
                "desc": desc,
                "expected": expected_codes,
                "found": [],
                "pass": False,
                "error": str(e)
            })
    # Write results to file
    with open("htsus_test_results.txt", "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"Description: {r['desc']}\n")
            f.write(f"Expected: {r['expected']}\n")
            f.write(f"Found: {r['found']}\n")
            f.write(f"Pass: {r['pass']}\n")
            if 'error' in r:
                f.write(f"Error: {r['error']}\n")
            f.write("-"*40 + "\n")
        f.write(f"\nTotal Passed: {passed} / {len(test_cases)}\n")
    print(f"\nTotal Passed: {passed} / {len(test_cases)} (see htsus_test_results.txt)")

if __name__ == "__main__":
    run_tests()
