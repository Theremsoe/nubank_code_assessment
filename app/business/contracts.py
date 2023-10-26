from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Generic, TypeVar

TxnSchemaT = TypeVar("TxnSchemaT")
TaxSchemaT = TypeVar("TaxSchemaT")


class Tax(ABC, Generic[TxnSchemaT, TaxSchemaT]):
    """
    Tax Contract

    Implements a common contract to generate taxes amounts to pay
    based on transactions
    """

    @abstractmethod
    def __init__(self, txn: TxnSchemaT):
        raise NotImplementedError()

    @abstractmethod
    def tax_percentage(self) -> Decimal:
        """
        Return the tax percentage to usage
        """
        raise NotImplementedError()

    @abstractmethod
    def get_taxes(self) -> TaxSchemaT:
        """
        Process and resolved transactions and generate
        the respective taxes to pay
        """
        raise NotImplementedError()
