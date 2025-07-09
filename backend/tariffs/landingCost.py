"""
Calculate the total landing cost of an item

Returns:
    float: landing cost
"""
def getLanding(prod_value: float, quantity: int, shipping: float, insurance: int, tax301: float, VAT: float, MRN: float) -> float:
    subtotal = prod_value * quantity + shipping + insurance
    print("subtotal", subtotal)

    dutyTotal = (tax301 + MRN) * subtotal
    print("dutytotal: ", dutyTotal)
          
    vatTotal = VAT * dutyTotal
    print("vatTotal ", vatTotal)
    return subtotal + dutyTotal + vatTotal

