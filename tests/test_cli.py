"""CLI tests using Typer's test runner."""

import pytest
from typer.testing import CliRunner

from entsoe.cli.app import app

runner = CliRunner()


class TestCLIHelp:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_catalog_list(self):
        result = runner.invoke(app, ["catalog", "list"])
        assert result.exit_code == 0
        for name in ("Prices", "Load", "Generation", "Transmission", "Balancing"):
            assert name in result.output

    def test_catalog_countries(self):
        result = runner.invoke(app, ["catalog", "countries"])
        assert result.exit_code == 0
        assert "FR" in result.output

    def test_catalog_countries_filter(self):
        result = runner.invoke(app, ["catalog", "countries", "france"])
        assert result.exit_code == 0
        assert "FR" in result.output
        # Filtered output should NOT contain unrelated countries
        assert "Poland" not in result.output

    def test_catalog_psr(self):
        result = runner.invoke(app, ["catalog", "psr"])
        assert result.exit_code == 0
        assert "solar" in result.output

    def test_catalog_borders(self):
        result = runner.invoke(app, ["catalog", "borders"])
        assert result.exit_code == 0

    def test_catalog_borders_country(self):
        result = runner.invoke(app, ["catalog", "borders", "FR"])
        assert result.exit_code == 0
        # FR has neighbours — output should show them
        assert "ES" in result.output or "BE" in result.output

    def test_catalog_show(self):
        result = runner.invoke(app, ["catalog", "show", "transmission"])
        assert result.exit_code == 0
        assert "Transmission" in result.output

    def test_prices_help(self):
        result = runner.invoke(app, ["prices", "day-ahead", "--help"])
        assert result.exit_code == 0


@pytest.mark.integration
class TestCLIIntegration:
    def test_prices_day_ahead(self):
        result = runner.invoke(
            app,
            ["prices", "day-ahead", "-s", "2024-06-03", "-e", "2024-06-04", "-c", "FR"],
        )
        assert result.exit_code == 0, result.output
