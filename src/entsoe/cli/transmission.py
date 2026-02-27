"""CLI subcommands for transmission namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output

transmission_app = typer.Typer(no_args_is_help=True)


def _resolve(values: list[str]) -> str | list[str]:
    return values[0] if len(values) == 1 else values


@transmission_app.command("flows")
def flows(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country_from: list[str] = typer.Option(..., "--from", help="Exporting country code. Repeat for multiple."),
    country_to: list[str] = typer.Option(..., "--to", help="Importing country code. Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query physical cross-border flows."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.transmission.crossborder_flows(
        start, end, country_from=_resolve(country_from), country_to=_resolve(country_to),
    )
    output(df, format, title="Cross-Border Flows", output_path=output_path)


@transmission_app.command("exchanges")
def exchanges(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country_from: list[str] = typer.Option(..., "--from", help="Exporting country code. Repeat for multiple."),
    country_to: list[str] = typer.Option(..., "--to", help="Importing country code. Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query scheduled commercial exchanges (day-ahead)."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.transmission.scheduled_exchanges(
        start, end, country_from=_resolve(country_from), country_to=_resolve(country_to),
    )
    output(df, format, title="Scheduled Exchanges", output_path=output_path)


@transmission_app.command("capacity")
def capacity(
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    country_from: list[str] = typer.Option(..., "--from", help="Exporting country code. Repeat for multiple."),
    country_to: list[str] = typer.Option(..., "--to", help="Importing country code. Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead net transfer capacity."""
    from entsoe.cli.app import get_client

    client = get_client(api_key)
    df = client.transmission.net_transfer_capacity(
        start, end, country_from=_resolve(country_from), country_to=_resolve(country_to),
    )
    output(df, format, title="Net Transfer Capacity", output_path=output_path)
