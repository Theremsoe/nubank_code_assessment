from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    """
    Operations types
    """

    BUY = "buy"
    SELL = "sell"


class TransactionSchema(BaseModel):
    """
    Describe a transaction schema
    """

    operation: OperationType
    unit_cost: Decimal = Field(alias="unit-cost", decimal_places=2)
    quantity: int = 0

    model_config = ConfigDict(
        populate_by_name=True,
    )
