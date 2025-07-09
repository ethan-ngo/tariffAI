import re

"""
Calculate the total landing cost of an item

Returns:
    float: landing cost
"""
def getLanding_MRN_rate(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, MRN: float) -> float:
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    print("tax301:", type(tax301))
    print("MRN:", type(MRN))

    tax301_duty = ((tax301 / 100)) * subtotal
    mrn_duty = ((MRN / 100)) * subtotal

    dutyTotal = tax301_duty + mrn_duty

    print("dutytotal: ", dutyTotal)
          
    vatTotal = (VAT / 100) * dutyTotal
    print("vatTotal ", vatTotal)

    landing_cost = subtotal + dutyTotal + vatTotal
    return {
        "subtotal": round(subtotal, 2),
        "tax301_rate": tax301,
        "tax301_duty": round(tax301_duty, 2),
        "mrn_rate": MRN,
        "mrn_duty": round(mrn_duty, 2),
        "duty_total": round(dutyTotal, 2),
        "vat_rate": VAT,
        "vat_total": round(vatTotal, 2),
        "landing_cost": round(landing_cost, 2)
    }

def getLanding_MRN_amt(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, MRN_rate, MRN_amt: float) -> float:
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    print("tax301:", type(tax301))
    print("MRN:", type(MRN_amt))

    tax301_duty = ((tax301 / 100)) * subtotal

    dutyTotal = tax301_duty + MRN_amt

    print("dutytotal: ", dutyTotal)
          
    vatTotal = (VAT / 100) * dutyTotal
    print("vatTotal ", vatTotal)

    landing_cost = subtotal + dutyTotal + vatTotal
    return {
        "subtotal": round(subtotal, 2),
        "tax301_rate": tax301,
        "tax301_duty": round(tax301_duty, 2),
        "mrn_rate": MRN_rate,
        "mrn_duty": round(MRN_amt, 2),
        "duty_total": round(dutyTotal, 2),
        "vat_rate": VAT,
        "vat_total": round(vatTotal, 2),
        "landing_cost": round(landing_cost, 2)
    }

# def parse_mrn_duty(mrn: str, weight: float, quantity: int) -> float:
#     """
#     Parses MRN and returns the duty as a flat dollar amount.
#     Handles percentage rates and specific duties (e.g. ¢/kg, $/each).
#     """
#     mrn = mrn.strip().lower()

#     if mrn == 'free':
#         return 0.0

#     if "%" in mrn:
#         try:
#             percent = float(mrn.replace("%", ""))
#             return (percent) # return rate multipier
#         except ValueError:
#             return 0.0

#     # ¢ per kg
#     match_cent_per_kg = re.match(r'([\d.]+)¢/kg', mrn)
#     if match_cent_per_kg:
#         cents = float(match_cent_per_kg.group(1))
#         return (cents / 100) * weight * quantity # return dollar amt

#     # $ per kg
#     match_dollar_per_kg = re.match(r'\$([\d.]+)/kg', mrn)
#     if match_dollar_per_kg:
#         rate = float(match_dollar_per_kg.group(1))
#         return rate * weight * quantity # return dollar amt

#     return 0.0



