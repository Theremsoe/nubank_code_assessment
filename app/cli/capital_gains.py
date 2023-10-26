from typing import List
from click import command, get_text_stream, echo
from pydantic import TypeAdapter
from app.business.capital_gains import CapitalGains
from app.schemas.tax import TaxSchema

from app.schemas.transaction import TransactionSchema


@command()
def capital_gains_cli():
    """
    Reads transactions stored in STDIN buffer and generate the
    respective taxes payments in a JSON string (STDOUT)
    """

    stdin_adapter = TypeAdapter(List[TransactionSchema])
    stdout_adapter = TypeAdapter(List[TaxSchema])

    echo("", nl=True)

    for line in get_text_stream("stdin"):
        json = line.lstrip()

        if not json:
            continue

        transactions: List[TransactionSchema] = stdin_adapter.validate_json(json)
        capital_gains = CapitalGains(transactions)
        taxes = capital_gains.get_taxes()

        echo(stdout_adapter.dump_json(taxes), nl=True)
