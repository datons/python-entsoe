"""Built-in data catalog for ENTSO-E Transparency Platform.

Provides structured metadata about available data categories, endpoints,
country codes, PSR types, and border groups — so users don't need to
consult external documentation every time.
"""

from __future__ import annotations

# Re-export dataclasses for backward compatibility
from entsoe._models import Category, Endpoint
from entsoe.catalog_manager import ENTSOECatalogManager as _Manager

__all__ = ["Category", "Endpoint", "CATEGORIES", "get_category", "summary"]

# ── Load categories from YAML ──────────────────────────────────────────

_mgr = _Manager()
_cats = {c.key: c for c in _mgr._load_categories()}

CATEGORIES: dict[str, Category] = _cats

# Individual constants for backward compatibility
PRICES = CATEGORIES["prices"]
LOAD = CATEGORIES["load"]
GENERATION = CATEGORIES["generation"]
TRANSMISSION = CATEGORIES["transmission"]
BALANCING = CATEGORIES["balancing"]


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
