from decimal import Decimal
from unittest import TestCase

from app.utils.decimals import quantize_decimal_places


class DecimalTest(TestCase):
    def test_quantize_decimal_places(self):
        self.assertEqual(quantize_decimal_places(Decimal(0.1 + 0.1 + 0.1)), Decimal('0.30'))
        self.assertEqual(quantize_decimal_places(Decimal(7 / 3)), Decimal('2.33'))
        self.assertEqual(quantize_decimal_places(Decimal('3.141516')), Decimal('3.14'))
