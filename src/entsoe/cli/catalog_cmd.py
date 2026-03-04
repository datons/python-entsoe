"""CLI command: browse the built-in data catalog."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from entsoe._mappings import AREA_CODES, COUNTRY_NAMES, PSR_CODES, PSR_TYPES, BORDER_GROUPS, NEIGHBOURS

catalog_app = typer.Typer(no_args_is_help=True)
console = Console()


@catalog_app.command("list")
def catalog_list():
    """List all available data categories and endpoints."""
    from entsoe.catalog import CATEGORIES

    for key, cat in CATEGORIES.items():
        console.print(f"\n[bold]{cat.name}[/bold] — {cat.description}")
        console.print(f"  Python: client.{cat.namespace}.*")
        console.print(f"  CLI:    entsoe {key} <command>")

        table = Table(show_header=True, padding=(0, 1))
        table.add_column("Endpoint", style="cyan")
        table.add_column("CLI Command", style="green")
        table.add_column("Resolution")
        table.add_column("Units")

        for ep in cat.endpoints:
            cli_short = ep.cli.split("entsoe ")[-1].split(" -")[0]
            table.add_row(ep.name, cli_short, ep.resolution, ep.units)

        console.print(table)


@catalog_app.command("countries")
def catalog_countries(
    query: Optional[str] = typer.Argument(None, help="Filter by country name or code"),
):
    """List available country and bidding zone codes."""
    table = Table(title="Country / Bidding Zone Codes", show_header=True, padding=(0, 1))
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    table.add_column("Neighbours", style="dim")

    for code in sorted(AREA_CODES.keys()):
        name = COUNTRY_NAMES.get(code, "")
        if query:
            q = query.lower()
            if q not in code.lower() and q not in name.lower():
                continue
        neighbours = ", ".join(sorted(NEIGHBOURS.get(code, set())))
        table.add_row(code, name, neighbours)

    console.print(table)


@catalog_app.command("psr")
def catalog_psr():
    """List available PSR (generation) types."""
    table = Table(title="PSR Types (Generation)", show_header=True, padding=(0, 1))
    table.add_column("Shorthand", style="cyan")
    table.add_column("ENTSO-E Code", style="green")
    table.add_column("Full Name")

    for shorthand, code in sorted(PSR_CODES.items()):
        full_name = PSR_TYPES.get(code, "")
        table.add_row(shorthand, code, full_name)

    console.print(table)


@catalog_app.command("borders")
def catalog_borders(
    country: Optional[str] = typer.Argument(None, help="Show borders for a specific country (e.g. FR, DE_LU)"),
):
    """List border groups and interconnections."""
    if country:
        code = country.upper().strip()
        if code not in NEIGHBOURS:
            console.print(f"[red]Unknown country '{country}'[/red]. Use 'entsoe catalog countries' to list.")
            raise typer.Exit(1)

        name = COUNTRY_NAMES.get(code, code)
        console.print(f"\n[bold]{name} ({code})[/bold] — {len(NEIGHBOURS[code])} interconnections:")

        table = Table(show_header=True, padding=(0, 1))
        table.add_column("Neighbour", style="cyan")
        table.add_column("Name")
        table.add_column("CLI (flows)")

        for n in sorted(NEIGHBOURS[code]):
            n_name = COUNTRY_NAMES.get(n, n)
            table.add_row(n, n_name, f"entsoe transmission flows --from {code} --to {n}")

        console.print(table)
        console.print(f"\n[dim]Shortcut: entsoe transmission flows --border {code}-*[/dim]")
    else:
        # Show named border groups
        console.print("\n[bold]Named Border Groups[/bold]")
        table = Table(show_header=True, padding=(0, 1))
        table.add_column("Group", style="cyan")
        table.add_column("Borders")

        for group_name, pairs in sorted(BORDER_GROUPS.items()):
            unique = set()
            for a, b in pairs:
                key = tuple(sorted([a, b]))
                unique.add(key)
            border_strs = [f"{a}-{b}" for a, b in sorted(unique)]
            table.add_row(group_name, ", ".join(border_strs[:8]) + ("..." if len(border_strs) > 8 else ""))

        console.print(table)
        console.print(f"\n[dim]Use 'entsoe catalog borders <COUNTRY>' for a specific country.[/dim]")


@catalog_app.command("show")
def catalog_show(
    category: str = typer.Argument(..., help="Category name: prices, load, generation, transmission, balancing"),
):
    """Show detailed info for a specific data category."""
    from entsoe.catalog import get_category

    try:
        cat = get_category(category)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]{cat.name}[/bold] — {cat.description}")
    console.print(f"  Python namespace: client.{cat.namespace}")
    console.print()

    for ep in cat.endpoints:
        console.print(f"  [cyan]{ep.name}[/cyan]")
        console.print(f"    {ep.description}")
        console.print(f"    Resolution: {ep.resolution}")
        console.print(f"    Units: {ep.units}")
        console.print(f"    Columns: {', '.join(ep.columns)}")
        console.print(f"    Python: {ep.method}")
        console.print(f"    CLI:    {ep.cli}")
        if ep.notes:
            console.print(f"    Notes:  {ep.notes}")
        console.print()
