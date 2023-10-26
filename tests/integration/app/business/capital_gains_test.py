
from decimal import Decimal
from typing import List
from unittest import TestCase

from pydantic import TypeAdapter

from app.business.capital_gains import CapitalGains, Traveler
from app.schemas.transaction import TransactionSchema


class CapitalGainsTest(TestCase):
    def test_weighted_average_with_empty_stock(self):
        """
        Validate that calculate_weighted_average returns unit_cost when stock is empty.
        """
        capital_gains = CapitalGains([])
        traveler = Traveler(
            stock=0,
        )
        txn = TransactionSchema(
            operation='buy',
            unit_cost=Decimal('89.99'),
        )

        self.assertEqual(capital_gains.calculate_weighted_average(txn, traveler), Decimal('89.99'))

    def test_weighted_average_with_irrational_value(self):
        """
        Validate that calculate_weighted_average strip decimal from irrational numbers
        """

        capital_gains = CapitalGains([])
        traveler = Traveler(
            stock=10,
            weighted_average=Decimal('20.00')
        )
        txn = TransactionSchema(
            operation='buy',
            unit_cost=Decimal('10.00'),
            quantity=5
        )

        self.assertEqual(capital_gains.calculate_weighted_average(txn, traveler), Decimal('16.67'))

    def test_can_pay_taxes(self):
        capital_gains = CapitalGains([])

        self.assertFalse(
            capital_gains.can_pay_taxes(
                TransactionSchema(operation='buy', unit_cost=Decimal('10.00'), quantity=5), Traveler(),
            )
        )

        self.assertFalse(
            capital_gains.can_pay_taxes(
                TransactionSchema(operation='sell', unit_cost=Decimal('10.00'), quantity=5), Traveler(profit=Decimal('-100.00')),
            )
        )

        self.assertFalse(
            capital_gains.can_pay_taxes(
                TransactionSchema(operation='sell', unit_cost=Decimal('10.00'), quantity=5), Traveler(profit=Decimal('100.00')),
            )
        )

        self.assertFalse(
            capital_gains.can_pay_taxes(
                TransactionSchema(operation='sell', unit_cost=Decimal('200000.00'), quantity=100), Traveler(profit=Decimal('100.00'), weighted_average=Decimal('200000.01')),
            )
        )

        self.assertTrue(
            capital_gains.can_pay_taxes(
                TransactionSchema(operation='sell', unit_cost=Decimal('200000.00'), quantity=100), Traveler(profit=Decimal('100.00'), weighted_average=Decimal('20000.00')),
            )
        )

    def test_case_1(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 100},
                {"operation":"sell", "unit-cost":15.00, "quantity": 50},
                {"operation":"sell", "unit-cost":15.00, "quantity": 50}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 3)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))

    def test_case_2(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":5.00, "quantity": 5000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 3)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('10000.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))

    def test_case_3(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":5.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 3000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 3)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('1000.00'))

    def test_case_4(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"buy", "unit-cost":25.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":15.00, "quantity": 10000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 3)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))

    def test_case_5(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"buy", "unit-cost":25.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":15.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":25.00, "quantity": 5000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 4)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))
        self.assertEqual(taxes[3].amount, Decimal('10000.00'))

    def test_case_6(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":2.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 2000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 2000},
                {"operation":"sell", "unit-cost":25.00, "quantity": 1000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 5)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))
        self.assertEqual(taxes[3].amount, Decimal('0.0'))
        self.assertEqual(taxes[4].amount, Decimal('3000.00'))

    def test_case_7(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
                {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":2.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 2000},
                {"operation":"sell", "unit-cost":20.00, "quantity": 2000},
                {"operation":"sell", "unit-cost":25.00, "quantity": 1000},
                {"operation":"buy", "unit-cost":20.00, "quantity": 10000},
                {"operation":"sell", "unit-cost":15.00, "quantity": 5000},
                {"operation":"sell", "unit-cost":30.00, "quantity": 4350},
                {"operation":"sell", "unit-cost":30.00, "quantity": 650}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 9)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))
        self.assertEqual(taxes[3].amount, Decimal('0.0'))
        self.assertEqual(taxes[4].amount, Decimal('3000.00'))
        self.assertEqual(taxes[5].amount, Decimal('0.0'))
        self.assertEqual(taxes[6].amount, Decimal('0.0'))
        self.assertEqual(taxes[7].amount, Decimal('3700.00'))
        self.assertEqual(taxes[8].amount, Decimal('0.0'))

    def test_case_8(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
               {"operation":"buy", "unit-cost":10.00, "quantity": 10000},
               {"operation":"sell", "unit-cost":50.00, "quantity": 10000},
               {"operation":"buy", "unit-cost":20.00, "quantity": 10000},
               {"operation":"sell", "unit-cost":50.00, "quantity": 10000}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 4)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('80000.00'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))
        self.assertEqual(taxes[3].amount, Decimal('60000.00'))

    def test_case_9(self):
        adapter = TypeAdapter(List[TransactionSchema])
        transactions: List[TransactionSchema] = adapter.validate_json(
            '''[
               {"operation":"buy", "unit-cost": 5000.00, "quantity": 10},
               {"operation":"sell", "unit-cost": 4000.00, "quantity": 5},
               {"operation":"buy", "unit-cost": 15000.00, "quantity": 5},
               {"operation":"buy", "unit-cost": 4000.00, "quantity": 2},
               {"operation":"buy", "unit-cost": 23000.00, "quantity": 2},
               {"operation":"sell", "unit-cost": 20000.00, "quantity": 1},
               {"operation":"sell", "unit-cost": 12000.00, "quantity": 10},
               {"operation":"sell", "unit-cost": 15000.00, "quantity": 3}
            ]'''
        )

        capital_gains = CapitalGains(transactions)

        taxes = capital_gains.get_taxes()

        self.assertEqual(len(taxes), 8)
        self.assertEqual(taxes[0].amount, Decimal('0.0'))
        self.assertEqual(taxes[1].amount, Decimal('0.0'))
        self.assertEqual(taxes[2].amount, Decimal('0.0'))
        self.assertEqual(taxes[3].amount, Decimal('0.0'))
        self.assertEqual(taxes[4].amount, Decimal('0.0'))
        self.assertEqual(taxes[5].amount, Decimal('0.0'))
        self.assertEqual(taxes[6].amount, Decimal('1000'))
