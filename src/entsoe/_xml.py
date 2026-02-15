"""XML parsing utilities for ENTSO-E API responses.

Parses TimeSeries XML documents into pandas DataFrames.
Handles the various document types returned by the API:
- GL_MarketDocument (load, generation)
- Publication_MarketDocument (prices)
- TransmissionNetwork_MarketDocument (transmission)
- Balancing_MarketDocument (balancing)

All share the TimeSeries > Period > Point structure.
"""

import re
import xml.etree.ElementTree as ET
from datetime import timedelta

import pandas as pd

from .exceptions import NoDataError


def _strip_ns(tag: str) -> str:
    """Remove XML namespace prefix from a tag name."""
    return re.sub(r"\{[^}]+\}", "", tag)


def _find(element: ET.Element, local_name: str) -> ET.Element | None:
    """Find a child element by local name, ignoring namespace."""
    for child in element:
        if _strip_ns(child.tag) == local_name:
            return child
    return None


def _findall(element: ET.Element, local_name: str) -> list[ET.Element]:
    """Find all child elements by local name, ignoring namespace."""
    return [child for child in element if _strip_ns(child.tag) == local_name]


def _find_text(element: ET.Element, local_name: str) -> str | None:
    """Find a child element's text by local name, ignoring namespace."""
    child = _find(element, local_name)
    return child.text if child is not None else None


def _parse_resolution(resolution: str) -> timedelta:
    """Parse ISO 8601 duration to timedelta.

    Common values: PT15M, PT30M, PT60M, P1Y
    """
    match = re.match(r"PT?(\d+)([MHDY])", resolution)
    if not match:
        raise ValueError(f"Cannot parse resolution: {resolution}")
    value, unit = int(match.group(1)), match.group(2)
    if unit == "M":
        return timedelta(minutes=value)
    if unit == "H":
        return timedelta(hours=value)
    if unit == "D":
        return timedelta(days=value)
    if unit == "Y":
        return timedelta(days=365 * value)
    raise ValueError(f"Unknown resolution unit: {unit}")


def _extract_point_value(point: ET.Element) -> float | None:
    """Extract the numeric value from a Point element.

    Handles <quantity> (load/generation), <price.amount> (day-ahead prices),
    and <imbalance_Price.amount> (balancing).
    """
    for tag in ("quantity", "price.amount", "imbalance_Price.amount"):
        text = _find_text(point, tag)
        if text is not None:
            return float(text)
    return None


def parse_timeseries(xml_text: str) -> pd.DataFrame:
    """Parse an ENTSO-E XML response into a DataFrame.

    Handles multiple TimeSeries (e.g., generation per type) and multiple
    Periods within each TimeSeries (e.g., multi-day responses).

    Returns a DataFrame with columns:
    - timestamp: tz-aware UTC datetime
    - value: numeric value (MW or EUR/MWh depending on query)
    - Plus any metadata columns (psr_type, etc.) if multiple TimeSeries present.

    Raises:
        NoDataError: If the response contains no TimeSeries data.
    """
    root = ET.fromstring(xml_text)
    timeseries_list = _findall(root, "TimeSeries")

    if not timeseries_list:
        # Check for reason/text in error responses
        reason = _find(root, "Reason")
        if reason is not None:
            reason_text = _find_text(reason, "text")
            raise NoDataError(reason_text or "No data available.")
        raise NoDataError()

    rows: list[dict] = []

    for ts in timeseries_list:
        # Extract TimeSeries metadata
        ts_meta: dict = {}

        # PSR type (generation fuel type)
        mkt_psr = _find(ts, "MktPSRType")
        if mkt_psr is not None:
            psr_code = _find_text(mkt_psr, "psrType")
            if psr_code:
                ts_meta["psr_type"] = psr_code

            # Generation unit identifiers (per-plant responses)
            psr = _find(mkt_psr, "PowerSystemResources")
            if psr is not None:
                unit_mrid = _find_text(psr, "mRID")
                unit_name = _find_text(psr, "name")
                if unit_mrid:
                    ts_meta["unit_eic"] = unit_mrid
                if unit_name:
                    ts_meta["unit_name"] = unit_name

        # In/Out domain (useful for transmission)
        in_domain = _find(ts, "in_Domain.mRID")
        if in_domain is not None and in_domain.text:
            ts_meta["in_domain"] = in_domain.text
        out_domain = _find(ts, "out_Domain.mRID")
        if out_domain is not None and out_domain.text:
            ts_meta["out_domain"] = out_domain.text

        # Currency and unit
        currency = _find_text(ts, "currency_Unit.name")
        if currency:
            ts_meta["currency"] = currency
        price_unit = _find_text(ts, "price_Measure_Unit.name")
        if price_unit:
            ts_meta["price_unit"] = price_unit
        quantity_unit = _find_text(ts, "quantity_Measure_Unit.name")
        if quantity_unit:
            ts_meta["quantity_unit"] = quantity_unit

        # Process each Period
        for period in _findall(ts, "Period"):
            time_interval = _find(period, "timeInterval")
            if time_interval is None:
                continue

            start_text = _find_text(time_interval, "start")
            if start_text is None:
                continue

            resolution_text = _find_text(period, "resolution")
            if resolution_text is None:
                continue

            period_start = pd.Timestamp(start_text)
            resolution = _parse_resolution(resolution_text)

            for point in _findall(period, "Point"):
                position_text = _find_text(point, "position")
                if position_text is None:
                    continue

                position = int(position_text)
                value = _extract_point_value(point)

                timestamp = period_start + resolution * (position - 1)

                row = {"timestamp": timestamp, "value": value, **ts_meta}
                rows.append(row)

    if not rows:
        raise NoDataError()

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df
