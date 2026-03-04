"""CLI subcommands for cache management."""

from __future__ import annotations

from typing import Optional

import typer

cache_app = typer.Typer(no_args_is_help=True)


@cache_app.command("status")
def cache_status():
    """Show cache statistics (files, size, domains)."""
    from entsoe.cache import CacheConfig, CacheStore

    store = CacheStore(CacheConfig())
    info = store.status()

    typer.echo(f"Cache path: {info['path']}")
    typer.echo(f"Total files: {info['files']}")
    typer.echo(f"Total size: {info['size_mb']} MB")

    if info.get("domains"):
        typer.echo("\nPer-domain breakdown:")
        for domain, count in sorted(info["domains"].items()):
            typer.echo(f"  {domain}: {count} files")
    elif info["files"] == 0:
        typer.echo("\nCache is empty.")


@cache_app.command("path")
def cache_path():
    """Print the cache directory path."""
    from entsoe.cache import CacheConfig

    typer.echo(CacheConfig().cache_dir)


@cache_app.command("clear")
def cache_clear(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain to clear (e.g. prices, load, generation)"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Topic to clear (e.g. day_ahead, actual)"),
    country: Optional[str] = typer.Option(None, "--country", "-c", help="Country/partition to clear (e.g. ES, FR)"),
    force: bool = typer.Option(False, "--force", "-y", help="Skip confirmation prompt"),
):
    """Clear cached data.

    Without options, clears the entire cache.
    Use --domain, --topic, --country to target specific partitions.
    """
    from entsoe.cache import CacheConfig, CacheStore

    store = CacheStore(CacheConfig())

    # Build description
    parts = []
    if domain:
        parts.append(f"domain={domain}")
    if topic:
        parts.append(f"topic={topic}")
    if country:
        parts.append(f"country={country}")
    scope = ", ".join(parts) if parts else "entire cache"

    if not force:
        confirm = typer.confirm(f"Clear {scope}?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    count = store.clear(domain=domain, topic=topic, partition=country)
    typer.echo(f"Removed {count} cached file(s).")
