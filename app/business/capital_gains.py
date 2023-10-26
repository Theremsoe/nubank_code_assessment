from decimal import Decimal
from functools import reduce
from typing import List, Optional

from pydantic import BaseModel
from app.business.contracts import Tax
from app.schemas.tax import TaxSchema
from app.schemas.transaction import TransactionSchema, OperationType
from app.utils.decimals import quantize_decimal_places


class Traveler(BaseModel):
    """
    Traveler/State to use in an iterator/reducer and drag state information
    """

    stock: int = 0
    weighted_average: Decimal = Decimal("0.0")
    profit: Decimal = Decimal("0.0")
    taxes: List[TaxSchema] = []


class CapitalGains(Tax[List[TransactionSchema], List[TaxSchema]]):
    """
    calculates how much tax you should pay based on the
    profit or losses of a stock
    """

    transactions: List[TransactionSchema]

    def __init__(self, transactions: List[TransactionSchema]):
        self.transactions = transactions

    def tax_percentage(self) -> Decimal:
        return Decimal("0.2")

    def get_taxes(self) -> List[TaxSchema]:
        traveler = self.process_transactions()

        return traveler.taxes

    def process_transactions(self) -> Traveler:
        """
        Iterate and reduce a list of transaction
        """
        return reduce(self.resolve_transaction, self.transactions, Traveler())

    def resolve_transaction(
        self,
        traveler: Optional[Traveler],
        txn: TransactionSchema,
    ) -> Traveler:
        """
        Gives a transaction and using traveler information determine how many taxes
        should pay
        """
        tax = TaxSchema(amount=Decimal("0.00"))

        if txn.operation is OperationType.BUY:
            traveler.weighted_average = self.calculate_weighted_average(txn, traveler)
            traveler.profit = self.dump_or_keep_losses_profit(traveler)
            traveler.stock += txn.quantity

        if txn.operation is OperationType.SELL:
            traveler.profit += self.calculate_profit(txn, traveler)
            traveler.stock -= txn.quantity

        if self.can_pay_taxes(txn, traveler):
            tax.amount = quantize_decimal_places(
                traveler.profit * self.tax_percentage()
            )
            traveler.profit -= tax.amount

        traveler.taxes.append(tax)

        return traveler

    def calculate_weighted_average(
        self, txn: TransactionSchema, traveler: Traveler
    ) -> Decimal:
        """
        Generate the weighted average value using current and next transaction
        """
        if traveler.stock == 0:
            return txn.unit_cost

        weighted_average = (
            (traveler.stock * traveler.weighted_average)
            + (txn.quantity * txn.unit_cost)
        ) / (traveler.stock + txn.quantity)

        return quantize_decimal_places(weighted_average)

    def calculate_profit(self, txn: TransactionSchema, traveler: Traveler) -> Decimal:
        """
        Calculate current profit based on current state and next transaction
        """
        total_amount = txn.quantity * txn.unit_cost

        if total_amount <= Decimal("20000.00") and traveler.profit < 0:
            return Decimal("0.0")

        profit = txn.quantity * traveler.weighted_average

        return quantize_decimal_places(total_amount - profit)

    def dump_or_keep_losses_profit(self, traveler: Traveler) -> Decimal:
        """
        Keep losses or dump overall profit when stock is empty
        """
        if traveler.stock == 0 and traveler.profit > 0:
            return Decimal("0.0")

        return quantize_decimal_places(traveler.profit)

    def can_pay_taxes(self, txn: TransactionSchema, traveler: Traveler) -> bool:
        """
        Business rule to determine whether a transaction pays taxes
        """
        return (
            txn.operation is OperationType.SELL
            and traveler.profit > 0
            and (txn.unit_cost * txn.quantity) > Decimal("20000.00")
            and txn.unit_cost > traveler.weighted_average
        )
