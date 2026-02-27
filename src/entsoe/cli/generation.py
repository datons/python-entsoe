"""CLI subcommands for generation namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output

generation_app = typer.Typer(no_args_is_help=True)


def _resolve_psr(psr: list[str] | None) -> str | list[str] | None:
    """Convert CLI --psr list to the format the library expects."""
    if not psr:
        return None
    return psr[0] if len(psr) == 1 else psr


def _resolve_country(country: list[str]) -> str | list[str]:
    return country[0] if len(country) == 1 else country


@generation_app.command("actual")
def actual(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type (e.g. solar, wind_onshore, B16). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual generation output per type."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.generation.actual(start, end, country=_resolve_country(country), psr_type=_resolve_psr(psr))
    output(df, format, title="Actual Generation", output_path=output_path)


@generation_app.command("forecast")
def forecast(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type (e.g. solar, wind_onshore). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead generation forecast (wind/solar)."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.generation.forecast(start, end, country=_resolve_country(country), psr_type=_resolve_psr(psr))
    output(df, format, title="Generation Forecast", output_path=output_path)


@generation_app.command("capacity")
def capacity(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type (e.g. solar, nuclear). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query installed generation capacity per type."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.generation.installed_capacity(start, end, country=_resolve_country(country), psr_type=_resolve_psr(psr))
    output(df, format, title="Installed Capacity", output_path=output_path)


@generation_app.command("per-plant")
def per_plant(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code (e.g. FR, ES). Repeat for multiple."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type (e.g. nuclear). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query actual generation per production unit."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.generation.per_plant(start, end, country=_resolve_country(country), psr_type=_resolve_psr(psr))
    output(df, format, title="Generation Per Plant", output_path=output_path)
