import re
from typing import List, Tuple

"""
Calculate the total landing cost of an item

Returns:
    float: landing cost
"""
def getLanding_MRN_rate(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, VAT_link, MRN: float, reciprocal_taxes: List[Tuple[float, str]]):
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    print("tax301:", type(tax301))
    print("MRN:", type(MRN))

    tax301_duty = ((tax301 / 100)) * subtotal
    mrn_duty = ((MRN / 100)) * subtotal

    total_reciprocal_taxes = 0.0
    for pair in reciprocal_taxes:
        total_reciprocal_taxes += pair[0]

    reciprocal_duty = (total_reciprocal_taxes / 100) * subtotal

    dutyTotal = tax301_duty + mrn_duty + reciprocal_duty

    print("dutytotal: ", dutyTotal)
          
    vatTotal = (VAT / 100) * (dutyTotal + subtotal)
    print("vatTotal ", vatTotal)

    landing_cost = subtotal + dutyTotal + vatTotal

    breakdown = (
        f"Subtotal = ({prod_value} × {quantity}) + {shipping} + {insurance} = {subtotal:.2f}",
        f"Base Duty = {subtotal:.2f} × {float(MRN/100):.2f} = {mrn_duty:.2f}",
        f"Section 301 Duty = {subtotal:.2f} × {float(tax301/100):.2f} = {tax301_duty:.2f}",
        f"Reciprocal Duties = {subtotal:.2f} × {float(total_reciprocal_taxes/100):.2f} = {reciprocal_duty:.2f}",
        f"Total Duties = {tax301_duty:.2f} + {mrn_duty:.2f} + {reciprocal_duty:.2f} = {dutyTotal:.2f}",
        f"VAT = {float(VAT/100):.2f} × ({subtotal:.2f} + {dutyTotal:.2f}) = {vatTotal:.2f}",
        f"Landed Cost = {subtotal:.2f} + {dutyTotal:.2f} + {vatTotal:.2f} = {landing_cost:.2f}",

    )

    return {
        "subtotal": round(subtotal, 2),
        "tax301_rate": tax301,
        "tax301_duty": round(tax301_duty, 2),
        "mrn_rate": MRN,
        "mrn_duty": round(mrn_duty, 2),
        "reciprocal_total_rate": total_reciprocal_taxes,
        "reciprocal_rates": reciprocal_taxes,
        "reciprocal_duty": round(reciprocal_duty, 2),
        "duty_total": round(dutyTotal, 2),
        "vat_rate": VAT,
        "vat_total": round(vatTotal, 2),
        "landing_cost": round(landing_cost, 2), 
        "regular": True,
        "breakdown": breakdown,
        "VAT_link": VAT_link,
        "htsus_code": "0"
    }

def getLanding_MRN_amt(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, VAT_link, MRN_rate, MRN_amt: float, cents, weight, weight_unit: str, reciprocal_taxes: List[Tuple[float, str]]):
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    print("tax301:", type(tax301))
    print("MRN:", type(MRN_amt))

    tax301_duty = ((tax301 / 100)) * subtotal

    total_reciprocal_taxes = 0.0
    for pair in reciprocal_taxes:
        total_reciprocal_taxes += pair[0]

    reciprocal_duty = (total_reciprocal_taxes / 100) * subtotal

    dutyTotal = tax301_duty + MRN_amt + reciprocal_duty

    print("dutytotal: ", dutyTotal)
          
    vatTotal = (VAT / 100) * (dutyTotal + subtotal)
    print("vatTotal ", vatTotal)

    landing_cost = subtotal + dutyTotal + vatTotal

    float_weight = float(weight)
    float_quantity = float(quantity) 

    breakdown = (
        f"Subtotal = ({prod_value} × {quantity}) + {shipping} + {insurance} = {subtotal:.2f}",
        f"Base Duty = ({cents} / 100) × {float_weight: .2f} {weight_unit} × {float_quantity: .2f} = {MRN_amt:.2f}",
        f"Section 301 Duty = {subtotal:.2f} × {float(tax301/100):.2f} = {tax301_duty:.2f}",
        f"Reciprocal Duties = {subtotal:.2f} × {float(total_reciprocal_taxes/100):.2f} = {reciprocal_duty:.2f}",
        f"Total Duties = {tax301_duty:.2f} + {MRN_amt:.2f} + {reciprocal_duty:.2f} = {dutyTotal:.2f}",
        f"VAT = {float(VAT/100):.2f} × ({subtotal:.2f} + {dutyTotal:.2f}) = {vatTotal:.2f}",
        f"Landed Cost = {subtotal:.2f} + {dutyTotal:.2f} + {vatTotal:.2f} = {landing_cost:.2f}"
    )

    print("returning output")

    return {
        "subtotal": round(subtotal, 2),
        "tax301_rate": tax301,
        "tax301_duty": round(tax301_duty, 2),
        "mrn_rate": MRN_rate,
        "mrn_duty": round(MRN_amt, 2),
        "reciprocal_total_rate": total_reciprocal_taxes,
        "reciprocal_rates": reciprocal_taxes,
        "reciprocal_duty": round(reciprocal_duty, 2),
        "duty_total": round(dutyTotal, 2),
        "vat_rate": VAT,
        "vat_total": round(vatTotal, 2),
        "landing_cost": round(landing_cost, 2),
        "regular": False,
        "breakdown": breakdown,
        "VAT_link": VAT_link,
        "htsus_code": "0"
    }
