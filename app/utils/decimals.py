from decimal import Decimal


def quantize_decimal_places(number: Decimal) -> Decimal:
    """
    Truncate decimal places
    """
    return number.quantize(Decimal(".01"))
