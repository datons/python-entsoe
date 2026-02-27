"""CLI subcommands for balancing namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output

balancing_app = typer.Typer(no_args_is_help=True)


@balancing_app.command("prices")
def prices(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, NL). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query imbalance prices."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    countries = country[0] if len(country) == 1 else country
    df = client.balancing.imbalance_prices(start, end, country=countries)
    output(df, format, title="Imbalance Prices", output_path=output_path)


@balancing_app.command("volumes")
def volumes(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, NL). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query imbalance volumes."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    countries = country[0] if len(country) == 1 else country
    df = client.balancing.imbalance_volumes(start, end, country=countries)
    output(df, format, title="Imbalance Volumes", output_path=output_path)
