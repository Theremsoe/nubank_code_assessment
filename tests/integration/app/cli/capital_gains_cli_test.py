from click.testing import CliRunner
from unittest import TestCase

from app.cli.capital_gains import capital_gains_cli


class CapitalGainsCliTest(TestCase):
    def test_stdin_stream(self):
        runner = CliRunner()

        stdin_stream = '[{"operation":"buy", "unit-cost":10.00, "quantity": 100},{"operation":"sell", "unit-cost":15.00, "quantity": 50},{"operation":"sell", "unit-cost":15.00, "quantity": 50}]'

        stdout_stream = runner.invoke(capital_gains_cli, input=stdin_stream)

        self.assertIsNone(stdout_stream.exception)
        self.assertIn(
            '[{"amount":"0.00"},{"amount":"0.00"},{"amount":"0.00"}]',
            stdout_stream.output
        )
