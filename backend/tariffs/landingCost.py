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
        "landing_cost": round(landing_cost, 2), 
        "regular": True
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
        "landing_cost": round(landing_cost, 2),
        "regular": False
    }
