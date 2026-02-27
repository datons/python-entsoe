"""CLI command: evaluate Python expressions against ENTSO-E data.

Unlike the single-namespace esios exec, this supports all 5 namespaces.
The first two positional arguments select the namespace and method,
then standard --start/--end/--country/--from/--to flags apply.
"""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli._output import render_result

exec_app = typer.Typer(no_args_is_help=True)

# Map CLI namespace+method to client calls
_NAMESPACE_METHODS = {
    ("prices", "day-ahead"): ("prices", "day_ahead"),
    ("load", "actual"): ("load", "actual"),
    ("load", "forecast"): ("load", "forecast"),
    ("generation", "actual"): ("generation", "actual"),
    ("generation", "forecast"): ("generation", "forecast"),
    ("generation", "capacity"): ("generation", "installed_capacity"),
    ("generation", "per-plant"): ("generation", "per_plant"),
    ("transmission", "flows"): ("transmission", "crossborder_flows"),
    ("transmission", "exchanges"): ("transmission", "scheduled_exchanges"),
    ("transmission", "capacity"): ("transmission", "net_transfer_capacity"),
    ("balancing", "prices"): ("balancing", "imbalance_prices"),
    ("balancing", "volumes"): ("balancing", "imbalance_volumes"),
}


@exec_app.callback(invoke_without_command=True)
def exec_command(
    ctx: typer.Context,
    namespace: str = typer.Argument(..., help="Namespace: prices, load, generation, transmission, balancing"),
    method: str = typer.Argument(..., help="Method: day-ahead, actual, forecast, capacity, per-plant, flows, exchanges, prices, volumes"),
    start: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    expr: str = typer.Option("df", "--expr", "-x", help="Python expression to evaluate (df, pd, np available)"),
    country: Optional[list[str]] = typer.Option(None, "--country", "-c", help="Country code. Repeat for multiple."),
    country_from: Optional[list[str]] = typer.Option(None, "--from", help="Exporting country (transmission only)."),
    country_to: Optional[list[str]] = typer.Option(None, "--to", help="Importing country (transmission only)."),
    psr: Optional[list[str]] = typer.Option(None, "--psr", "-p", help="PSR type (generation only). Repeat for multiple."),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="ENTSO-E API key"),
):
    """Fetch data from any namespace and evaluate a Python expression on it.

    The fetched data is available as `df` (pandas DataFrame).
    `pd` (pandas) and `np` (numpy) are also available.

    \b
    Examples:
        entsoe exec prices day-ahead -s 2024-06-01 -e 2024-06-08 -c FR -x "df.describe()"
        entsoe exec load actual -s 2024-06-01 -e 2024-06-08 -c FR -x "df.resample('D').mean()"
        entsoe exec generation actual -s 2024-06-01 -e 2024-06-08 -c FR --psr solar -x "df.head()"
        entsoe exec transmission flows -s 2024-06-01 -e 2024-06-08 --from FR --to ES -x "df.describe()"
    """
    import numpy as np
    import pandas as pd

    from entsoe.cli.app import get_client

    key = (namespace, method)
    if key not in _NAMESPACE_METHODS:
        typer.echo(
            f"Error: Unknown namespace/method '{namespace} {method}'.\n"
            f"Available: {', '.join(f'{n} {m}' for n, m in sorted(_NAMESPACE_METHODS.keys()))}",
            err=True,
        )
        raise typer.Exit(1)

    ns_name, method_name = _NAMESPACE_METHODS[key]
    client = get_client(api_key)
    ns = getattr(client, ns_name)
    fn = getattr(ns, method_name)

    # Build kwargs based on namespace
    kwargs: dict = {}
    if ns_name == "transmission":
        if not country_from or not country_to:
            typer.echo("Error: Transmission queries require --from and --to.", err=True)
            raise typer.Exit(1)
        kwargs["country_from"] = country_from[0] if len(country_from) == 1 else country_from
        kwargs["country_to"] = country_to[0] if len(country_to) == 1 else country_to
    else:
        if not country:
            typer.echo("Error: --country is required for this query.", err=True)
            raise typer.Exit(1)
        kwargs["country"] = country[0] if len(country) == 1 else country

    if ns_name == "generation" and psr:
        kwargs["psr_type"] = psr[0] if len(psr) == 1 else psr

    df = fn(start, end, **kwargs)

    if df.empty:
        typer.echo("No data returned.")
        raise typer.Exit(0)

    # Evaluate expression
    eval_namespace = {"df": df, "pd": pd, "np": np}
    try:
        result = eval(expr, {"__builtins__": {}}, eval_namespace)  # noqa: S307
    except Exception as exc:
        typer.echo(f"Error evaluating expression: {exc}", err=True)
        raise typer.Exit(1)

    render_result(result, format, output_path)
