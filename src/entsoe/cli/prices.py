"""CLI subcommands for prices namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output
from entsoe.cli._resolve import resolve_dates, resolve_many_required

prices_app = typer.Typer(no_args_is_help=True)


@prices_app.command("day-ahead")
def day_ahead(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead electricity prices."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    countries = resolve_many_required(country)
    df = client.prices.day_ahead(s, e, country=countries)
    output(df, format, title="Day-Ahead Prices", output_path=output_path)


# Register exec under prices
from entsoe.cli.exec_cmd import exec_prices  # noqa: E402

prices_app.command("exec", help="Fetch price data and evaluate a Python expression")(exec_prices)
