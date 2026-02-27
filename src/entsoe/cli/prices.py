"""CLI subcommands for prices namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output

prices_app = typer.Typer(no_args_is_help=True)


@prices_app.command("day-ahead")
def day_ahead(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead electricity prices."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    countries = country[0] if len(country) == 1 else country
    df = client.prices.day_ahead(start, end, country=countries)
    output(df, format, title="Day-Ahead Prices", output_path=output_path)
