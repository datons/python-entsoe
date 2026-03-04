"""Shared CLI value-resolution utilities.

Centralizes comma-splitting, relative date resolution, and border spec
parsing so every command module stays DRY.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta


def resolve_many(values: list[str] | None) -> str | list[str] | None:
    """Split comma-separated values, flatten, and unwrap single items.

    Supports both repeated flags (``-c ES -c FR``) and comma-separated
    (``-c ES,FR,DE_LU``), or any mix of the two.

    Returns:
        ``None`` if *values* is empty/None, a single string if only one
        value after splitting, otherwise a list.
    """
    if not values:
        return None
    flat = [v.strip() for raw in values for v in raw.split(",") if v.strip()]
    if not flat:
        return None
    return flat[0] if len(flat) == 1 else flat


def resolve_many_required(values: list[str]) -> str | list[str]:
    """Like :func:`resolve_many` but for required (non-optional) lists."""
    flat = [v.strip() for raw in values for v in raw.split(",") if v.strip()]
    return flat[0] if len(flat) == 1 else flat


# ---------------------------------------------------------------------------
# Relative date resolution
# ---------------------------------------------------------------------------

_PERIOD_RE = re.compile(r"^(\d+)d$")

# ENTSO-E uses CET/CEST (Europe/Brussels) as its reference timezone.
_ENTSOE_TZ = "Europe/Brussels"


def _today() -> date:
    """Return today's date in the ENTSO-E reference timezone."""
    try:
        from zoneinfo import ZoneInfo
    except ImportError:  # Python < 3.9 fallback
        from backports.zoneinfo import ZoneInfo  # type: ignore[no-redef]
    return datetime.now(tz=ZoneInfo(_ENTSOE_TZ)).date()


def resolve_dates(
    start: str | None,
    end: str | None,
    period: str | None,
) -> tuple[str, str]:
    """Accept ``--start``/``--end`` OR ``--period``.

    Period shorthands:

    =========  ==============================
    Shorthand  Meaning
    =========  ==============================
    today      today only
    yesterday  yesterday only
    week       Monday of current week → today
    month      1st of current month → today
    ytd        Jan 1st of current year → today
    ``Nd``     last *N* days → today
    =========  ==============================

    Raises:
        typer.BadParameter: On invalid combinations or unknown shorthands.
    """
    import typer

    if period:
        if start or end:
            raise typer.BadParameter(
                "Cannot combine --period with --start/--end."
            )
        today = _today()
        s, e = _expand_period(period, today)
        return s.isoformat(), e.isoformat()

    if not start or not end:
        raise typer.BadParameter(
            "Provide --start and --end, or use --period."
        )
    return start, end


def _expand_period(period: str, today: date) -> tuple[date, date]:
    """Expand a period shorthand into (start, end) dates."""
    import typer

    p = period.lower().strip()

    if p == "today":
        return today, today
    if p == "yesterday":
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    if p == "week":
        monday = today - timedelta(days=today.weekday())
        return monday, today
    if p == "month":
        return today.replace(day=1), today
    if p == "ytd":
        return today.replace(month=1, day=1), today

    m = _PERIOD_RE.match(p)
    if m:
        days = int(m.group(1))
        return today - timedelta(days=days), today

    raise typer.BadParameter(
        f"Unknown period '{period}'. "
        "Use: today, yesterday, week, month, ytd, or <N>d (e.g. 7d, 30d)."
    )


# ---------------------------------------------------------------------------
# Border spec resolution (transmission) — thin CLI wrapper
# ---------------------------------------------------------------------------
# Core parsing lives in entsoe._mappings.parse_borders (no typer dependency).
# This wrapper converts InvalidParameterError → typer.BadParameter for CLI use.


def resolve_borders_cli(values: list[str]) -> list[tuple[str, str]]:
    """CLI wrapper around :func:`entsoe._mappings.parse_borders`.

    Comma-splits CLI repeated flags, delegates to the library-level parser,
    and re-raises errors as :class:`typer.BadParameter`.
    """
    import typer

    from entsoe._mappings import parse_borders
    from entsoe.exceptions import InvalidParameterError

    flat = [v.strip() for raw in values for v in raw.split(",") if v.strip()]
    try:
        return parse_borders(flat)
    except InvalidParameterError as exc:
        raise typer.BadParameter(str(exc)) from exc
