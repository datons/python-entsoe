"""CLI subcommands for load namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output
from entsoe.cli._resolve import resolve_dates, resolve_many_required

load_app = typer.Typer(no_args_is_help=True)


@load_app.command("actual")
def actual(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual total system load."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    countries = resolve_many_required(country)
    df = client.load.actual(s, e, country=countries)
    output(df, format, title="Actual Load", output_path=output_path)


@load_app.command("forecast")
def forecast(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead load forecast."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    countries = resolve_many_required(country)
    df = client.load.forecast(s, e, country=countries)
    output(df, format, title="Load Forecast", output_path=output_path)


# Register exec under load
from entsoe.cli.exec_cmd import exec_load  # noqa: E402

load_app.command("exec", help="Fetch load data and evaluate a Python expression")(exec_load)
