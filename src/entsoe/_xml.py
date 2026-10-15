"""XML parsing utilities for ENTSO-E API responses.

Parses TimeSeries XML documents into pandas DataFrames.
Handles the various document types returned by the API:
- GL_MarketDocument (load, generation)
- Publication_MarketDocument (prices)
- TransmissionNetwork_MarketDocument (transmission)
- Balancing_MarketDocument (balancing)

All share the TimeSeries > Period > Point structure.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import Callable

import pandas as pd

from .exceptions import NoDataError
from ._mappings import EIC_TO_ISO, PSR_TYPES


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


#: Element holding the sequence of a TimeSeries within a document, e.g. the
#: SDAC (1) and EXAA (2) day-ahead auctions both published for DE_LU and AT.
SEQUENCE_TAG = "classificationSequence_AttributeInstanceComponent.position"


def timeseries_sequence(ts: ET.Element) -> int | None:
    """Return the classification sequence of a TimeSeries, or None if absent."""
    for el in ts.iter():
        if _strip_ns(el.tag) == SEQUENCE_TAG and el.text:
            return int(el.text)
    return None


def timeseries_contract_type(ts: ET.Element) -> str | None:
    """Return the contract_MarketAgreement.type of a TimeSeries (A01 daily, A07 intraday)."""
    return _find_text(ts, "contract_MarketAgreement.type")


def parse_timeseries(
    xml_text: str,
    ts_filter: Callable[[ET.Element], bool] | None = None,
) -> pd.DataFrame:
    """Parse an ENTSO-E XML response into a DataFrame.

    Handles multiple TimeSeries (e.g., generation per type) and multiple
    Periods within each TimeSeries (e.g., multi-day responses).

    Points omitted from a curveType A03 (variable-sized block) Period carry
    the previous point's value, so they are filled in. TimeSeries the API
    repeats verbatim produce duplicate rows, which are dropped.

    Args:
        xml_text: Raw XML response.
        ts_filter: Optional predicate on each TimeSeries element; series for
            which it returns False are skipped.

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
        if ts_filter is not None and not ts_filter(ts):
            continue

        # Extract TimeSeries metadata
        ts_meta: dict = {}

        # PSR type (generation fuel type)
        mkt_psr = _find(ts, "MktPSRType")
        if mkt_psr is not None:
            psr_code = _find_text(mkt_psr, "psrType")
            if psr_code:
                ts_meta["psr_type"] = PSR_TYPES.get(psr_code, psr_code)

            # Generation unit identifiers (per-plant responses)
            psr = _find(mkt_psr, "PowerSystemResources")
            if psr is not None:
                unit_mrid = _find_text(psr, "mRID")
                unit_name = _find_text(psr, "name")
                if unit_mrid:
                    ts_meta["unit_eic"] = unit_mrid
                if unit_name:
                    ts_meta["unit_name"] = unit_name

        # In/Out domain (useful for transmission) — resolve EIC → ISO
        in_domain = _find(ts, "in_Domain.mRID")
        if in_domain is not None and in_domain.text:
            ts_meta["in_domain"] = EIC_TO_ISO.get(in_domain.text, in_domain.text)
        out_domain = _find(ts, "out_Domain.mRID")
        if out_domain is not None and out_domain.text:
            ts_meta["out_domain"] = EIC_TO_ISO.get(out_domain.text, out_domain.text)

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

            values: dict[int, float | None] = {}
            for point in _findall(period, "Point"):
                position_text = _find_text(point, "position")
                if position_text is None:
                    continue
                values[int(position_text)] = _extract_point_value(point)

            if not values:
                continue

            positions = sorted(values)
            if _find_text(ts, "curveType") == "A03":
                end_text = _find_text(time_interval, "end")
                if end_text is not None:
                    n_slots = int((pd.Timestamp(end_text) - period_start) / resolution)
                else:
                    n_slots = positions[-1]
                filled: dict[int, float | None] = {}
                last = None
                for pos in range(positions[0], max(n_slots, positions[-1]) + 1):
                    last = values.get(pos, last)
                    filled[pos] = last
                values, positions = filled, list(filled)

            for position in positions:
                timestamp = period_start + resolution * (position - 1)
                rows.append({"timestamp": timestamp, "value": values[position], **ts_meta})

    if not rows:
        raise NoDataError()

    df = pd.DataFrame(rows).drop_duplicates()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df
