from decimal import Decimal
from pydantic import BaseModel


class TaxSchema(BaseModel):
    """
    Describe a Tax model
    """

    amount: Decimal
