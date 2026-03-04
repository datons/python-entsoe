"""CLI subcommands for generation namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output
from entsoe.cli._resolve import resolve_dates, resolve_many, resolve_many_required

generation_app = typer.Typer(no_args_is_help=True)


@generation_app.command("actual")
def actual(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type(s), comma-separated or repeated (e.g. solar,wind_onshore,B16)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual generation output per type."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    df = client.generation.actual(s, e, country=resolve_many_required(country), psr_type=resolve_many(psr))
    output(df, format, title="Actual Generation", output_path=output_path)


@generation_app.command("forecast")
def forecast(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type(s), comma-separated or repeated (e.g. solar,wind_onshore)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead generation forecast (wind/solar)."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    df = client.generation.forecast(s, e, country=resolve_many_required(country), psr_type=resolve_many(psr))
    output(df, format, title="Generation Forecast", output_path=output_path)


@generation_app.command("capacity")
def capacity(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type(s), comma-separated or repeated (e.g. solar,nuclear)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query installed generation capacity per type."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    df = client.generation.installed_capacity(s, e, country=resolve_many_required(country), psr_type=resolve_many(psr))
    output(df, format, title="Installed Capacity", output_path=output_path)


@generation_app.command("per-plant")
def per_plant(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated (e.g. ES,FR,DE_LU)"),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type(s), comma-separated or repeated (e.g. nuclear)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual generation per production unit."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    df = client.generation.per_plant(s, e, country=resolve_many_required(country), psr_type=resolve_many(psr))
    output(df, format, title="Generation Per Plant", output_path=output_path)


# Register exec under generation
from entsoe.cli.exec_cmd import exec_generation  # noqa: E402

generation_app.command("exec", help="Fetch generation data and evaluate a Python expression")(exec_generation)
