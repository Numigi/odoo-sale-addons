# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from decimal import Decimal, ROUND_HALF_UP

ROUNDING_AMOUNTS = [
    '0.01',
    '0.05',
    '0.1',
    '0.5',
    '1',
    '5',
    '10',
    '50',
    '100',
    '500',
    '1000',
]


def round_price(price: float, rounding: str) -> str:
    """Round the given price using a rounding amount.

    The rounding amount can be any of the values of ROUNDING_AMOUNTS.

    :param price: the price to round
    :param rounding: the rounding amount to apply
    :return: the rounded price
    """
    factor = (Decimal(price) / Decimal(rounding)).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
    result_decimal = factor * Decimal(rounding)
    return float(result_decimal)
