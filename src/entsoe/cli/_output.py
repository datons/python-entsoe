"""Shared output helpers for the ENTSO-E CLI."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _fmt(val) -> str:
    """Format a value for table display."""
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def output(df, format: str, title: str = "", output_path: str | None = None):
    """Render DataFrame in the requested format."""
    import pandas as pd

    if df.empty:
        typer.echo("No data.")
        return

    if format == "csv":
        text = df.to_csv()
        if output_path:
            with open(output_path, "w") as f:
                f.write(text)
            typer.echo(f"Written to {output_path}")
        else:
            typer.echo(text)

    elif format == "json":
        text = df.to_json(orient="records", indent=2, date_format="iso")
        if output_path:
            with open(output_path, "w") as f:
                f.write(text)
            typer.echo(f"Written to {output_path}")
        else:
            typer.echo(text)

    else:  # table
        table = Table(title=title)
        cols = list(df.columns)[:10]  # Limit columns for readability
        if df.index.name:
            table.add_column(df.index.name, style="cyan")
        for col in cols:
            table.add_column(str(col))

        for idx, row in df.head(50).iterrows():
            values = [str(idx)] if df.index.name else []
            values += [_fmt(row[c]) for c in cols]
            table.add_row(*values)

        if len(df) > 50:
            table.caption = f"Showing 50 of {len(df)} rows"

        console.print(table)


def render_result(result, format: str, output_path: str | None) -> None:
    """Render an eval result (DataFrame, Series, or scalar)."""
    import pandas as pd

    if isinstance(result, pd.Series):
        result = result.to_frame()

    if isinstance(result, pd.DataFrame):
        if format == "csv":
            text = result.to_csv()
        elif format == "json":
            text = result.to_json(orient="records", indent=2, date_format="iso")
        else:
            table = Table()
            idx_name = result.index.name or ""
            table.add_column(str(idx_name), style="cyan")
            for col in result.columns:
                table.add_column(str(col))

            for idx, row in result.head(100).iterrows():
                values = [str(idx)]
                values += [_fmt(row[c]) for c in result.columns]
                table.add_row(*values)

            if len(result) > 100:
                table.caption = f"Showing 100 of {len(result)} rows"
            console.print(table)
            return

        if output_path:
            with open(output_path, "w") as f:
                f.write(text)
            typer.echo(f"Written to {output_path}")
        else:
            typer.echo(text)
    else:
        typer.echo(result)
