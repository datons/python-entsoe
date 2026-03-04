"""CLI command: evaluate Python expressions against ENTSO-E data.

Each namespace gets its own ``exec`` subcommand that reuses the same
flags as its sibling queries.  E.g.::

    entsoe prices exec day-ahead -P week -c ES,FR -x "df.describe()"
    entsoe transmission exec flows -P week --border ES-* -x "df.head()"
"""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import render_result
from entsoe.cli._resolve import resolve_dates, resolve_many, resolve_many_required


# ---------------------------------------------------------------------------
# Shared eval logic
# ---------------------------------------------------------------------------

def _eval_and_render(
    df,
    expr: str,
    format: str,
    output_path: str | None,
) -> None:
    """Evaluate *expr* against *df* and render the result."""
    import numpy as np
    import pandas as pd

    if df.empty:
        typer.echo("No data returned.")
        raise typer.Exit(0)

    namespace = {"df": df, "pd": pd, "np": np}
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)  # noqa: S307
    except Exception as exc:
        typer.echo(f"Error evaluating expression: {exc}", err=True)
        raise typer.Exit(1)

    render_result(result, format, output_path)


# ---------------------------------------------------------------------------
# prices exec <method>
# ---------------------------------------------------------------------------

_PRICES_METHODS = {"day-ahead": "day_ahead"}


def exec_prices(
    method: str = typer.Argument(..., help="Method: day-ahead"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated."),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression (df, pd, np available)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch price data and evaluate a Python expression.

    \b
    Examples:
        entsoe prices exec day-ahead -P week -c ES,FR -x "df.describe()"
    """
    from entsoe.cli.app import get_client

    method_name = _resolve_method(method, _PRICES_METHODS)
    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    fn = getattr(client.prices, method_name)
    df = fn(s, e, country=resolve_many_required(country))
    _eval_and_render(df, expr, format, output_path)


# ---------------------------------------------------------------------------
# load exec <method>
# ---------------------------------------------------------------------------

_LOAD_METHODS = {"actual": "actual", "forecast": "forecast"}


def exec_load(
    method: str = typer.Argument(..., help="Method: actual, forecast"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated."),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression (df, pd, np available)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch load data and evaluate a Python expression.

    \b
    Examples:
        entsoe load exec actual -P 7d -c FR -x "df.resample('D').mean()"
    """
    from entsoe.cli.app import get_client

    method_name = _resolve_method(method, _LOAD_METHODS)
    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    fn = getattr(client.load, method_name)
    df = fn(s, e, country=resolve_many_required(country))
    _eval_and_render(df, expr, format, output_path)


# ---------------------------------------------------------------------------
# generation exec <method>
# ---------------------------------------------------------------------------

_GENERATION_METHODS = {
    "actual": "actual",
    "forecast": "forecast",
    "capacity": "installed_capacity",
    "per-plant": "per_plant",
}


def exec_generation(
    method: str = typer.Argument(..., help="Method: actual, forecast, capacity, per-plant"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type(s), comma-separated or repeated."),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression (df, pd, np available)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch generation data and evaluate a Python expression.

    \b
    Examples:
        entsoe generation exec actual -P month -c FR --psr solar -x "df.head()"
    """
    from entsoe.cli.app import get_client

    method_name = _resolve_method(method, _GENERATION_METHODS)
    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    fn = getattr(client.generation, method_name)
    df = fn(s, e, country=resolve_many_required(country), psr_type=resolve_many(psr))
    _eval_and_render(df, expr, format, output_path)


# ---------------------------------------------------------------------------
# transmission exec <method>
# ---------------------------------------------------------------------------

_TRANSMISSION_METHODS = {
    "flows": "crossborder_flows",
    "exchanges": "scheduled_exchanges",
    "capacity": "net_transfer_capacity",
}


def exec_transmission(
    method: str = typer.Argument(..., help="Method: flows, exchanges, capacity"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country_from: Optional[list[str]] = typer.Option(None, "--from", help="Exporting country code(s), comma-separated or repeated."),
    country_to: Optional[list[str]] = typer.Option(None, "--to", help="Importing country code(s), comma-separated or repeated."),
    border: Optional[list[str]] = typer.Option(None, "--border", "-b", help="Border spec(s): ES-FR, ES-*, iberian. Comma-separated or repeated."),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression (df, pd, np available)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch transmission data and evaluate a Python expression.

    \b
    Examples:
        entsoe transmission exec flows -P week --from FR --to ES -x "df.describe()"
        entsoe transmission exec flows -P week --border ES-*,FR-* -x "df.head()"
    """
    from entsoe.cli.app import get_client

    method_name = _resolve_method(method, _TRANSMISSION_METHODS)
    s, e = resolve_dates(start, end, period)

    kwargs: dict = {}
    if border:
        flat = [v.strip() for raw in border for v in raw.split(",") if v.strip()]
        kwargs["borders"] = flat
    elif country_from and country_to:
        kwargs["country_from"] = resolve_many_required(country_from)
        kwargs["country_to"] = resolve_many_required(country_to)
    else:
        typer.echo("Error: Provide --from/--to or --border.", err=True)
        raise typer.Exit(1)

    client = get_client(api_key)
    fn = getattr(client.transmission, method_name)
    df = fn(s, e, **kwargs)
    _eval_and_render(df, expr, format, output_path)


# ---------------------------------------------------------------------------
# balancing exec <method>
# ---------------------------------------------------------------------------

_BALANCING_METHODS = {"prices": "imbalance_prices", "volumes": "imbalance_volumes"}


def exec_balancing(
    method: str = typer.Argument(..., help="Method: prices, volumes"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date (YYYY-MM-DD)"),
    period: Optional[str] = typer.Option(None, "--period", "-P", help="Period shorthand: today, yesterday, week, month, ytd, <N>d"),
    country: list[str] = typer.Option(..., "--country", "-c", help="Country code(s), comma-separated or repeated."),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression (df, pd, np available)"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch balancing data and evaluate a Python expression.

    \b
    Examples:
        entsoe balancing exec prices -P week -c NL -x "df.describe()"
    """
    from entsoe.cli.app import get_client

    method_name = _resolve_method(method, _BALANCING_METHODS)
    s, e = resolve_dates(start, end, period)
    client = get_client(api_key)
    fn = getattr(client.balancing, method_name)
    df = fn(s, e, country=resolve_many_required(country))
    _eval_and_render(df, expr, format, output_path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_method(method: str, mapping: dict[str, str]) -> str:
    """Resolve a CLI method name to the client method name."""
    if method not in mapping:
        typer.echo(
            f"Error: Unknown method '{method}'. "
            f"Available: {', '.join(sorted(mapping.keys()))}",
            err=True,
        )
        raise typer.Exit(1)
    return mapping[method]
