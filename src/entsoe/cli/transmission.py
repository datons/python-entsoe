"""CLI subcommands for transmission namespace."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import output
from entsoe.cli._resolve import resolve_dates, resolve_many_required

transmission_app = typer.Typer(no_args_is_help=True)


def _resolve_borders_or_pairs(
    country_from: list[str] | None,
    country_to: list[str] | None,
    border: list[str] | None,
) -> dict:
    """Build kwargs for the library's transmission methods."""
    if border:
        # Comma-split and pass as list to the library's borders= parameter
        flat = [v.strip() for raw in border for v in raw.split(",") if v.strip()]
        return {"borders": flat}
    if not country_from or not country_to:
        raise typer.BadParameter(
            "Provide --from and --to, or use --border (e.g. ES-FR,ES-PT or ES-*)."
        )
    return {
        "country_from": resolve_many_required(country_from),
        "country_to": resolve_many_required(country_to),
    }


@transmission_app.command("flows")
def flows(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country_from: Optional[list[str]] = typer.Option(None, "--from", help="Exporting country code(s), comma-separated or repeated."),
    country_to: Optional[list[str]] = typer.Option(None, "--to", help="Importing country code(s), comma-separated or repeated."),
    border: Optional[list[str]] = typer.Option(None, "--border", "-b", help="Border spec(s): ES-FR, ES-*, iberian. Comma-separated or repeated."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query physical cross-border flows."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    kwargs = _resolve_borders_or_pairs(country_from, country_to, border)
    client = get_client(api_key)
    df = client.transmission.crossborder_flows(s, e, **kwargs)
    output(df, format, title="Cross-Border Flows", output_path=output_path)


@transmission_app.command("exchanges")
def exchanges(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country_from: Optional[list[str]] = typer.Option(None, "--from", help="Exporting country code(s), comma-separated or repeated."),
    country_to: Optional[list[str]] = typer.Option(None, "--to", help="Importing country code(s), comma-separated or repeated."),
    border: Optional[list[str]] = typer.Option(None, "--border", "-b", help="Border spec(s): ES-FR, ES-*, iberian. Comma-separated or repeated."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query scheduled commercial exchanges (day-ahead)."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    kwargs = _resolve_borders_or_pairs(country_from, country_to, border)
    client = get_client(api_key)
    df = client.transmission.scheduled_exchanges(s, e, **kwargs)
    output(df, format, title="Scheduled Exchanges", output_path=output_path)


@transmission_app.command("capacity")
def capacity(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country_from: Optional[list[str]] = typer.Option(None, "--from", help="Exporting country code(s), comma-separated or repeated."),
    country_to: Optional[list[str]] = typer.Option(None, "--to", help="Importing country code(s), comma-separated or repeated."),
    border: Optional[list[str]] = typer.Option(None, "--border", "-b", help="Border spec(s): ES-FR, ES-*, iberian. Comma-separated or repeated."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Query day-ahead net transfer capacity."""
    from entsoe.cli.app import get_client

    s, e = resolve_dates(start, end, period)
    kwargs = _resolve_borders_or_pairs(country_from, country_to, border)
    client = get_client(api_key)
    df = client.transmission.net_transfer_capacity(s, e, **kwargs)
    output(df, format, title="Net Transfer Capacity", output_path=output_path)


# Register exec under transmission
from entsoe.cli.exec_cmd import exec_transmission  # noqa: E402

transmission_app.command("exec", help="Fetch transmission data and evaluate a Python expression")(exec_transmission)
