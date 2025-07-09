"""
Calculate the total landing cost of an item

Returns:
    float: landing cost
"""
def getLanding(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, MRN: float) -> float:
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    print("tax301:", type(tax301))
    print("MRN:", type(MRN))

    dutyTotal = ((tax301 / 100) + (MRN / 100)) * subtotal
    print("dutytotal: ", dutyTotal)
          
    vatTotal = (VAT / 100) * dutyTotal
    print("vatTotal ", vatTotal)
    return subtotal + dutyTotal + vatTotal

