"""ENTSO-E CLI — main Typer application."""

from __future__ import annotations

from typing import Optional

import typer

from entsoe.cli.config import get_api_key

app = typer.Typer(
    name="entsoe",
    help="CLI for the ENTSO-E Transparency Platform (European electricity market data).",
    no_args_is_help=True,
)


def get_client(api_key: str | None = None):
    """Lazy import + construct client."""
    from entsoe.client import Client

    resolved = api_key or get_api_key()
    if not resolved:
        typer.echo(
            "Error: No API key. Set ENTSOE_API_KEY or run: entsoe config set api-key <KEY>",
            err=True,
        )
        raise typer.Exit(1)
    return Client(api_key=resolved)


# -- Register sub-commands ---------------------------------------------------

from entsoe.cli.prices import prices_app  # noqa: E402
from entsoe.cli.load import load_app  # noqa: E402
from entsoe.cli.generation import generation_app  # noqa: E402
from entsoe.cli.transmission import transmission_app  # noqa: E402
from entsoe.cli.balancing import balancing_app  # noqa: E402
from entsoe.cli.exec_cmd import exec_app  # noqa: E402
from entsoe.cli.config_cmd import config_app  # noqa: E402

app.add_typer(prices_app, name="prices", help="Day-ahead electricity prices")
app.add_typer(load_app, name="load", help="Actual load and load forecasts")
app.add_typer(generation_app, name="generation", help="Generation data (actual, forecast, capacity, per-plant)")
app.add_typer(transmission_app, name="transmission", help="Cross-border flows and exchanges")
app.add_typer(balancing_app, name="balancing", help="Imbalance prices and volumes")
app.add_typer(exec_app, name="exec", help="Fetch data and evaluate a pandas expression")
app.add_typer(config_app, name="config", help="Configuration management")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
