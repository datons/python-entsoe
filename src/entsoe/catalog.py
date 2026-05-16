"""Built-in data catalog for ENTSO-E Transparency Platform.

Provides structured metadata about available data categories, endpoints,
country codes, PSR types, and border groups — so users don't need to
consult external documentation every time.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Endpoint:
    """A queryable data endpoint."""

    name: str
    description: str
    method: str  # Python client method name
    cli: str  # CLI command
    resolution: str  # e.g. "15min", "hourly", "daily"
    columns: tuple[str, ...]  # key columns returned
    units: str
    notes: str = ""


@dataclass(frozen=True)
class Category:
    """A top-level data category grouping related endpoints."""

    name: str
    description: str
    namespace: str  # Python client namespace (e.g. "prices")
    endpoints: tuple[Endpoint, ...]


# ── Prices ──────────────────────────────────────────────────────────────

PRICES = Category(
    name="Prices",
    description="Day-ahead electricity market prices",
    namespace="prices",
    endpoints=(
        Endpoint(
            name="Day-Ahead Prices",
            description="Hourly day-ahead market clearing prices per bidding zone",
            method="client.prices.day_ahead(start, end, country='FR')",
            cli="entsoe prices day-ahead -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="hourly",
            columns=("timestamp", "country", "value", "currency", "quantity_unit"),
            units="EUR/MWh",
        ),
    ),
)

# ── Load ────────────────────────────────────────────────────────────────

LOAD = Category(
    name="Load",
    description="Actual system load and day-ahead load forecasts",
    namespace="load",
    endpoints=(
        Endpoint(
            name="Actual Total Load",
            description="Actual total electricity consumption per control area",
            method="client.load.actual(start, end, country='FR')",
            cli="entsoe load actual -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly (varies by country)",
            columns=("timestamp", "country", "value", "quantity_unit"),
            units="MW",
        ),
        Endpoint(
            name="Day-Ahead Load Forecast",
            description="Day-ahead forecast of total electricity consumption",
            method="client.load.forecast(start, end, country='FR')",
            cli="entsoe load forecast -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly (varies by country)",
            columns=("timestamp", "country", "value", "quantity_unit"),
            units="MW",
        ),
    ),
)

# ── Generation ──────────────────────────────────────────────────────────

GENERATION = Category(
    name="Generation",
    description="Actual generation, forecasts, installed capacity, and per-plant output",
    namespace="generation",
    endpoints=(
        Endpoint(
            name="Actual Generation per Type",
            description="Actual electricity generation broken down by fuel/technology type (PSR)",
            method="client.generation.actual(start, end, country='FR')",
            cli="entsoe generation actual -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly",
            columns=("timestamp", "country", "psr_type", "value", "quantity_unit"),
            units="MW",
            notes="Filter by PSR type: --psr solar --psr wind_onshore",
        ),
        Endpoint(
            name="Generation Forecast (Wind/Solar)",
            description="Day-ahead forecast for wind and solar generation",
            method="client.generation.forecast(start, end, country='FR')",
            cli="entsoe generation forecast -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly",
            columns=("timestamp", "country", "psr_type", "value", "quantity_unit"),
            units="MW",
        ),
        Endpoint(
            name="Installed Generation Capacity",
            description="Installed generation capacity per type (updated annually or on change)",
            method="client.generation.installed_capacity(start, end, country='FR')",
            cli="entsoe generation capacity -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="yearly (point-in-time)",
            columns=("timestamp", "country", "psr_type", "value", "quantity_unit"),
            units="MW",
        ),
        Endpoint(
            name="Actual Generation per Plant",
            description="Generation output per individual production unit (>= 100 MW)",
            method="client.generation.per_plant(start, end, country='FR')",
            cli="entsoe generation per-plant -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly",
            columns=("timestamp", "country", "unit_name", "psr_type", "value", "quantity_unit"),
            units="MW",
        ),
    ),
)

# ── Transmission ────────────────────────────────────────────────────────

TRANSMISSION = Category(
    name="Transmission",
    description="Cross-border physical flows, scheduled exchanges, and transfer capacity",
    namespace="transmission",
    endpoints=(
        Endpoint(
            name="Physical Cross-Border Flows",
            description="Actual measured electricity flows between bidding zones",
            method="client.transmission.crossborder_flows(start, end, country_from='FR', country_to='DE_LU')",
            cli="entsoe transmission flows -s 2024-06-01 -e 2024-06-08 --from FR --to DE_LU",
            resolution="15min or hourly",
            columns=("timestamp", "in_domain", "value", "quantity_unit"),
            units="MW",
            notes="Use --border for multi-border queries: --border FR-*, --border iberian",
        ),
        Endpoint(
            name="Scheduled Commercial Exchanges",
            description="Day-ahead scheduled commercial power exchanges between zones",
            method="client.transmission.scheduled_exchanges(start, end, country_from='FR', country_to='ES')",
            cli="entsoe transmission exchanges -s 2024-06-01 -e 2024-06-08 --from FR --to ES",
            resolution="hourly",
            columns=("timestamp", "in_domain", "value", "quantity_unit"),
            units="MW",
        ),
        Endpoint(
            name="Net Transfer Capacity",
            description="Available transfer capacity (NTC) between bidding zones",
            method="client.transmission.net_transfer_capacity(start, end, country_from='FR', country_to='ES')",
            cli="entsoe transmission capacity -s 2024-06-01 -e 2024-06-08 --from FR --to ES",
            resolution="hourly",
            columns=("timestamp", "in_domain", "value", "quantity_unit"),
            units="MW",
        ),
    ),
)

# ── Balancing ───────────────────────────────────────────────────────────

BALANCING = Category(
    name="Balancing",
    description="System imbalance prices and volumes",
    namespace="balancing",
    endpoints=(
        Endpoint(
            name="Imbalance Prices",
            description="System imbalance settlement prices",
            method="client.balancing.imbalance_prices(start, end, country='FR')",
            cli="entsoe balancing prices -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly (varies by country)",
            columns=("timestamp", "country", "value", "quantity_unit"),
            units="EUR/MWh",
        ),
        Endpoint(
            name="Imbalance Volumes",
            description="Net system imbalance volumes",
            method="client.balancing.imbalance_volumes(start, end, country='FR')",
            cli="entsoe balancing volumes -s 2024-06-01 -e 2024-06-08 -c FR",
            resolution="15min or hourly (varies by country)",
            columns=("timestamp", "country", "value", "quantity_unit"),
            units="MW",
        ),
    ),
)

# ── Full catalog ────────────────────────────────────────────────────────

CATEGORIES: dict[str, Category] = {
    "prices": PRICES,
    "load": LOAD,
    "generation": GENERATION,
    "transmission": TRANSMISSION,
    "balancing": BALANCING,
}


def get_category(name: str) -> Category:
    """Look up a category by name (case-insensitive)."""
    key = name.lower().strip()
    if key not in CATEGORIES:
        raise KeyError(
            f"Unknown category '{name}'. Available: {', '.join(CATEGORIES.keys())}"
        )
    return CATEGORIES[key]


def summary() -> str:
    """Return a human-readable summary of all available data."""
    lines = ["ENTSO-E Data Catalog", "=" * 50, ""]
    for key, cat in CATEGORIES.items():
        lines.append(f"{cat.name} ({cat.namespace})")
        lines.append(f"  {cat.description}")
        for ep in cat.endpoints:
            lines.append(f"    - {ep.name}: {ep.description}")
            lines.append(f"      Resolution: {ep.resolution} | Units: {ep.units}")
        lines.append("")
    return "\n".join(lines)
