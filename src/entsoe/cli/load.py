"""CLI subcommands for load namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output

load_app = typer.Typer(no_args_is_help=True)


@load_app.command("actual")
def actual(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual total system load."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    countries = country[0] if len(country) == 1 else country
    df = client.load.actual(start, end, country=countries)
    output(df, format, title="Actual Load", output_path=output_path)


@load_app.command("forecast")
def forecast(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead load forecast."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    countries = country[0] if len(country) == 1 else country
    df = client.load.forecast(start, end, country=countries)
    output(df, format, title="Load Forecast", output_path=output_path)
