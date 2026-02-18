"""ENTSO-E code registries and lookup functions.

Each code list is a ``{code: {name, slug, description}}`` dict:

- **name**: User-facing label that appears in DataFrame columns.
- **slug**: Programmatic identifier (lowercase, underscore-separated).
- **description**: Full ENTSO-E description.

Helper functions:

- ``_resolve(registry, identifier)`` — resolve a slug, name, or code to its
  canonical ENTSO-E code.
- ``_name(registry, code, *, fallback)`` — get the *name* for a code,
  with optional fallback for unknown codes.
"""

from __future__ import annotations

from typing import TypedDict

# ── Type definitions ───────────────────────────────────────────────────────


class CodeEntry(TypedDict):
    name: str
    slug: str
    description: str


class AreaEntry(TypedDict):
    eic: str
    name: str
    tz: str


# ── Helper functions ───────────────────────────────────────────────────────


def _resolve(registry: dict[str, CodeEntry], identifier: str) -> str:
    """Resolve a slug, name, or ENTSO-E code to its canonical code.

    Lookup order:
    1. Exact code match (e.g. ``"A47"``).
    2. Slug match (e.g. ``"mfrr"``).
    3. Case-insensitive name match (e.g. ``"mFRR"``).

    Args:
        registry: A code registry dict.
        identifier: Code, slug, or name.

    Returns:
        The canonical ENTSO-E code string.

    Raises:
        KeyError: If the identifier is not found.
    """
    # 1. Exact code
    if identifier in registry:
        return identifier

    # 2. Slug (lowercase comparison)
    id_lower = identifier.lower().strip()
    for code, entry in registry.items():
        if entry["slug"] == id_lower:
            return code

    # 3. Case-insensitive name
    for code, entry in registry.items():
        if entry["name"].lower() == id_lower:
            return code

    available = ", ".join(
        f"{e['slug']} ({code})" for code, e in sorted(registry.items())
    )
    raise KeyError(
        f"Unknown identifier: '{identifier}'. Available: {available}"
    )


def _name(
    registry: dict[str, CodeEntry],
    code: str,
    *,
    fallback: str | None = None,
) -> str:
    """Get the display name for an ENTSO-E code.

    Args:
        registry: A code registry dict.
        code: The ENTSO-E code (e.g. ``"A47"``).
        fallback: Value to return if the code is unknown.
            If ``None``, raises ``KeyError``.

    Returns:
        The name string.
    """
    entry = registry.get(code)
    if entry is not None:
        return entry["name"]
    if fallback is not None:
        return fallback
    raise KeyError(f"Unknown code: '{code}' in registry")


# ── Areas ──────────────────────────────────────────────────────────────────

AREAS: dict[str, AreaEntry] = {
    "AL": {"eic": "10YAL-KESH-----5", "name": "Albania", "tz": "Europe/Tirane"},
    "AT": {"eic": "10YAT-APG------L", "name": "Austria", "tz": "Europe/Vienna"},
    "BA": {"eic": "10YBA-JPCC-----D", "name": "Bosnia and Herzegovina", "tz": "Europe/Sarajevo"},
    "BE": {"eic": "10YBE----------2", "name": "Belgium", "tz": "Europe/Brussels"},
    "BG": {"eic": "10YCA-BULGARIA-R", "name": "Bulgaria", "tz": "Europe/Sofia"},
    "CH": {"eic": "10YCH-SWISSGRIDZ", "name": "Switzerland", "tz": "Europe/Zurich"},
    "CZ": {"eic": "10YCZ-CEPS-----N", "name": "Czech Republic", "tz": "Europe/Prague"},
    "DE": {"eic": "10Y1001A1001A83F", "name": "Germany", "tz": "Europe/Berlin"},
    "DE_LU": {"eic": "10Y1001A1001A82H", "name": "Germany/Luxembourg", "tz": "Europe/Berlin"},
    "DE_AT_LU": {"eic": "10Y1001A1001A63L", "name": "Germany/Austria/Luxembourg", "tz": "Europe/Berlin"},
    "DK": {"eic": "10Y1001A1001A65H", "name": "Denmark", "tz": "Europe/Copenhagen"},
    "DK_1": {"eic": "10YDK-1--------W", "name": "Denmark (West)", "tz": "Europe/Copenhagen"},
    "DK_2": {"eic": "10YDK-2--------M", "name": "Denmark (East)", "tz": "Europe/Copenhagen"},
    "EE": {"eic": "10Y1001A1001A39I", "name": "Estonia", "tz": "Europe/Tallinn"},
    "ES": {"eic": "10YES-REE------0", "name": "Spain", "tz": "Europe/Madrid"},
    "FI": {"eic": "10YFI-1--------U", "name": "Finland", "tz": "Europe/Helsinki"},
    "FR": {"eic": "10YFR-RTE------C", "name": "France", "tz": "Europe/Paris"},
    "GB": {"eic": "10YGB----------A", "name": "Great Britain", "tz": "Europe/London"},
    "GR": {"eic": "10YGR-HTSO-----Y", "name": "Greece", "tz": "Europe/Athens"},
    "HR": {"eic": "10YHR-HEP------M", "name": "Croatia", "tz": "Europe/Zagreb"},
    "HU": {"eic": "10YHU-MAVIR----U", "name": "Hungary", "tz": "Europe/Budapest"},
    "IE": {"eic": "10YIE-1001A00010", "name": "Ireland", "tz": "Europe/Dublin"},
    "IE_SEM": {"eic": "10Y1001A1001A59C", "name": "Ireland (SEM)", "tz": "Europe/Dublin"},
    "IT": {"eic": "10YIT-GRTN-----B", "name": "Italy", "tz": "Europe/Rome"},
    "IT_NORTH": {"eic": "10Y1001A1001A73I", "name": "Italy (North)", "tz": "Europe/Rome"},
    "IT_CNOR": {"eic": "10Y1001A1001A70O", "name": "Italy (Central North)", "tz": "Europe/Rome"},
    "IT_CSUD": {"eic": "10Y1001A1001A71M", "name": "Italy (Central South)", "tz": "Europe/Rome"},
    "IT_SUD": {"eic": "10Y1001A1001A788", "name": "Italy (South)", "tz": "Europe/Rome"},
    "IT_SICI": {"eic": "10Y1001A1001A74G", "name": "Italy (Sicily)", "tz": "Europe/Rome"},
    "IT_SARD": {"eic": "10Y1001A1001A75E", "name": "Italy (Sardinia)", "tz": "Europe/Rome"},
    "LT": {"eic": "10YLT-1001A0008Q", "name": "Lithuania", "tz": "Europe/Vilnius"},
    "LU": {"eic": "10YLU-CEGEDEL-NQ", "name": "Luxembourg", "tz": "Europe/Luxembourg"},
    "LV": {"eic": "10YLV-1001A00074", "name": "Latvia", "tz": "Europe/Riga"},
    "ME": {"eic": "10YCS-CG-TSO---S", "name": "Montenegro", "tz": "Europe/Podgorica"},
    "MK": {"eic": "10YMK-MEPSO----8", "name": "North Macedonia", "tz": "Europe/Skopje"},
    "MT": {"eic": "10Y1001A1001A93C", "name": "Malta", "tz": "Europe/Malta"},
    "NL": {"eic": "10YNL----------L", "name": "Netherlands", "tz": "Europe/Amsterdam"},
    "NO": {"eic": "10YNO-0--------C", "name": "Norway", "tz": "Europe/Oslo"},
    "NO_1": {"eic": "10YNO-1--------2", "name": "Norway (South-East)", "tz": "Europe/Oslo"},
    "NO_2": {"eic": "10YNO-2--------T", "name": "Norway (South-West)", "tz": "Europe/Oslo"},
    "NO_3": {"eic": "10YNO-3--------J", "name": "Norway (Central)", "tz": "Europe/Oslo"},
    "NO_4": {"eic": "10YNO-4--------9", "name": "Norway (North)", "tz": "Europe/Oslo"},
    "NO_5": {"eic": "10Y1001A1001A48H", "name": "Norway (West)", "tz": "Europe/Oslo"},
    "PL": {"eic": "10YPL-AREA-----S", "name": "Poland", "tz": "Europe/Warsaw"},
    "PT": {"eic": "10YPT-REN------W", "name": "Portugal", "tz": "Europe/Lisbon"},
    "RO": {"eic": "10YRO-TEL------P", "name": "Romania", "tz": "Europe/Bucharest"},
    "RS": {"eic": "10YCS-SERBIATSOV", "name": "Serbia", "tz": "Europe/Belgrade"},
    "SE": {"eic": "10YSE-1--------K", "name": "Sweden", "tz": "Europe/Stockholm"},
    "SE_1": {"eic": "10Y1001A1001A44P", "name": "Sweden (Lule\u00e5)", "tz": "Europe/Stockholm"},
    "SE_2": {"eic": "10Y1001A1001A45N", "name": "Sweden (Sundsvall)", "tz": "Europe/Stockholm"},
    "SE_3": {"eic": "10Y1001A1001A46L", "name": "Sweden (Stockholm)", "tz": "Europe/Stockholm"},
    "SE_4": {"eic": "10Y1001A1001A47J", "name": "Sweden (Malm\u00f6)", "tz": "Europe/Stockholm"},
    "SI": {"eic": "10YSI-ELES-----O", "name": "Slovenia", "tz": "Europe/Ljubljana"},
    "SK": {"eic": "10YSK-SEPS-----K", "name": "Slovakia", "tz": "Europe/Bratislava"},
    "TR": {"eic": "10YTR-TEIAS----W", "name": "Turkey", "tz": "Europe/Istanbul"},
    "UA": {"eic": "10Y1001C--00003F", "name": "Ukraine", "tz": "Europe/Kiev"},
    "UK": {"eic": "10Y1001A1001A92E", "name": "United Kingdom", "tz": "Europe/London"},
    "XK": {"eic": "10Y1001C--00100H", "name": "Kosovo", "tz": "Europe/Belgrade"},
}

# ── Backward-compatible derived dicts ──────────────────────────────────────

AREA_CODES: dict[str, str] = {k: v["eic"] for k, v in AREAS.items()}
COUNTRY_NAMES: dict[str, str] = {k: v["name"] for k, v in AREAS.items()}
EIC_TO_ISO: dict[str, str] = {v["eic"]: k for k, v in AREAS.items()}

_NAME_TO_ISO: dict[str, str] = {v["name"].lower(): k for k, v in AREAS.items()}


# ── PSR types ──────────────────────────────────────────────────────────────

PSR_TYPES: dict[str, CodeEntry] = {
    "B01": {"name": "Biomass", "slug": "biomass", "description": "Biomass"},
    "B02": {"name": "Fossil Brown coal/Lignite", "slug": "lignite", "description": "Fossil brown coal/lignite"},
    "B03": {"name": "Fossil Coal-derived gas", "slug": "coal_gas", "description": "Fossil coal-derived gas"},
    "B04": {"name": "Fossil Gas", "slug": "gas", "description": "Fossil gas"},
    "B05": {"name": "Fossil Hard coal", "slug": "hard_coal", "description": "Fossil hard coal"},
    "B06": {"name": "Fossil Oil", "slug": "oil", "description": "Fossil oil"},
    "B07": {"name": "Fossil Oil shale", "slug": "oil_shale", "description": "Fossil oil shale"},
    "B08": {"name": "Fossil Peat", "slug": "peat", "description": "Fossil peat"},
    "B09": {"name": "Geothermal", "slug": "geothermal", "description": "Geothermal"},
    "B10": {"name": "Hydro Pumped Storage", "slug": "pumped_storage", "description": "Hydro pumped storage"},
    "B11": {"name": "Hydro Run-of-river and poundage", "slug": "run_of_river", "description": "Hydro run-of-river and poundage"},
    "B12": {"name": "Hydro Water Reservoir", "slug": "hydro_reservoir", "description": "Hydro water reservoir"},
    "B13": {"name": "Marine", "slug": "marine", "description": "Marine"},
    "B14": {"name": "Nuclear", "slug": "nuclear", "description": "Nuclear"},
    "B15": {"name": "Other renewable", "slug": "other_renewable", "description": "Other renewable"},
    "B16": {"name": "Solar", "slug": "solar", "description": "Solar"},
    "B17": {"name": "Waste", "slug": "waste", "description": "Waste"},
    "B18": {"name": "Wind Offshore", "slug": "wind_offshore", "description": "Wind offshore"},
    "B19": {"name": "Wind Onshore", "slug": "wind_onshore", "description": "Wind onshore"},
    "B20": {"name": "Other", "slug": "other", "description": "Other"},
}

# Backward-compatible flat dict: slug → code
PSR_CODES: dict[str, str] = {e["slug"]: code for code, e in PSR_TYPES.items()}

# Reverse lookups for PSR
_PSR_NAME_TO_CODE: dict[str, str] = {e["name"].lower(): code for code, e in PSR_TYPES.items()}
_PSR_NAME_TO_CODE.update(PSR_CODES)


# ── Process types ──────────────────────────────────────────────────────────

PROCESS_TYPES: dict[str, CodeEntry] = {
    "A01": {"name": "Day ahead", "slug": "day_ahead", "description": "Day ahead forecast"},
    "A02": {"name": "Intraday incremental", "slug": "intraday_incremental", "description": "Intraday incremental"},
    "A16": {"name": "Realised", "slug": "realised", "description": "Realised/actual data"},
    "A18": {"name": "Intraday total", "slug": "intraday_total", "description": "Intraday total"},
    "A31": {"name": "Week ahead", "slug": "week_ahead", "description": "Week ahead forecast"},
    "A32": {"name": "Month ahead", "slug": "month_ahead", "description": "Month ahead forecast"},
    "A33": {"name": "Year ahead", "slug": "year_ahead", "description": "Year ahead forecast"},
    "A39": {"name": "Synchronisation process", "slug": "synchronisation", "description": "Synchronisation process"},
    "A40": {"name": "Intraday process", "slug": "intraday_process", "description": "Intraday process"},
    "A46": {"name": "Replacement reserve", "slug": "replacement_reserve", "description": "Replacement reserve (RR)"},
    "A47": {"name": "mFRR", "slug": "mfrr", "description": "Manual frequency restoration reserve"},
    "A51": {"name": "aFRR", "slug": "afrr", "description": "Automatic frequency restoration reserve"},
    "A52": {"name": "FCR", "slug": "fcr", "description": "Frequency containment reserve"},
    "A56": {"name": "Frequency netting", "slug": "frequency_netting", "description": "Frequency netting process"},
}


# ── Document types ─────────────────────────────────────────────────────────

DOCUMENT_TYPES: dict[str, CodeEntry] = {
    "A09": {"name": "Finalised schedule", "slug": "scheduled_exchanges", "description": "Finalised schedule"},
    "A11": {"name": "Aggregated energy data report", "slug": "physical_crossborder_flows", "description": "Aggregated energy data report"},
    "A25": {"name": "Allocation result document", "slug": "allocation_result", "description": "Allocation result document"},
    "A26": {"name": "Capacity document", "slug": "capacity", "description": "Capacity document"},
    "A31": {"name": "Agreed capacity", "slug": "agreed_capacity", "description": "Agreed capacity"},
    "A44": {"name": "Price document", "slug": "day_ahead_prices", "description": "Price document"},
    "A61": {"name": "Estimated Net Transfer Capacity", "slug": "net_transfer_capacity", "description": "Estimated net transfer capacity"},
    "A63": {"name": "Redispatch notice", "slug": "redispatch_notice", "description": "Redispatch notice"},
    "A65": {"name": "System total load", "slug": "actual_load", "description": "System total load"},
    "A68": {"name": "Installed generation per type", "slug": "installed_capacity", "description": "Installed generation per type"},
    "A69": {"name": "Wind and solar forecast", "slug": "generation_forecast_wind_solar", "description": "Wind and solar generation forecast"},
    "A70": {"name": "Load forecast margin", "slug": "load_forecast_margin", "description": "Load forecast margin"},
    "A71": {"name": "Generation forecast", "slug": "generation_forecast", "description": "Generation forecast"},
    "A73": {"name": "Actual generation per unit", "slug": "actual_generation_per_plant", "description": "Actual generation per generating unit"},
    "A74": {"name": "Wind and solar generation", "slug": "wind_solar_generation", "description": "Wind and solar generation"},
    "A75": {"name": "Actual generation per type", "slug": "actual_generation_per_type", "description": "Actual generation per type"},
    "A76": {"name": "Load unavailability", "slug": "load_unavailability", "description": "Load unavailability"},
    "A77": {"name": "Production unavailability", "slug": "production_unavailability", "description": "Generation unavailability"},
    "A78": {"name": "Transmission unavailability", "slug": "transmission_unavailability", "description": "Transmission infrastructure unavailability"},
    "A79": {"name": "Offshore unavailability", "slug": "offshore_unavailability", "description": "Offshore grid infrastructure unavailability"},
    "A80": {"name": "Generation unavailability", "slug": "generation_unavailability", "description": "Generation unavailability"},
    "A81": {"name": "Contracted reserves", "slug": "contracted_reserve_prices", "description": "Contracted reserves"},
    "A82": {"name": "Accepted aggregated offers", "slug": "accepted_offers", "description": "Accepted aggregated offers"},
    "A83": {"name": "Activated balancing quantities", "slug": "activated_balancing_quantities", "description": "Activated balancing quantities"},
    "A84": {"name": "Activated balancing energy prices", "slug": "activated_balancing_energy_prices", "description": "Prices of activated balancing energy"},
    "A85": {"name": "Imbalance prices", "slug": "imbalance_prices", "description": "Imbalance prices"},
    "A86": {"name": "Imbalance volumes", "slug": "imbalance_volumes", "description": "Imbalance volume"},
    "A87": {"name": "Financial expenses", "slug": "financial_expenses", "description": "Financial expenses and income for balancing"},
    "A88": {"name": "Cross-border balancing", "slug": "cross_border_balancing", "description": "Cross-border balancing"},
    "A89": {"name": "Contracted reserve prices", "slug": "contracted_reserve_prices_detail", "description": "Contracted reserve prices — detailed"},
    "A90": {"name": "Interconnection NTC DA", "slug": "interconnection_ntc_da", "description": "Interconnection network expansion — day ahead"},
    "A91": {"name": "HVDC availability", "slug": "hvdc_availability", "description": "DC link capacity"},
    "A92": {"name": "HVDC planned unavailability", "slug": "hvdc_planned_unavailability", "description": "Planned unavailability of DC links"},
    "A93": {"name": "HVDC forced unavailability", "slug": "hvdc_forced_unavailability", "description": "Forced unavailability of DC links"},
    "A94": {"name": "Cross-border exchange forecast", "slug": "cross_border_forecast", "description": "Day-ahead commercial exchange"},
    "A95": {"name": "Expansion and dismantling", "slug": "expansion_dismantling", "description": "Expansion and dismantling projects"},
    "B11": {"name": "Aggregated filling rate", "slug": "aggregated_filling_rate", "description": "Aggregated filling rate of water reservoirs and hydro storage plants"},
}


# ── Price categories ───────────────────────────────────────────────────────

PRICE_CATEGORIES: dict[str, CodeEntry] = {
    "A04": {"name": "Long", "slug": "long", "description": "Excess balance (system long)"},
    "A05": {"name": "Short", "slug": "short", "description": "Insufficient balance (system short)"},
    "A06": {"name": "Average bid price", "slug": "average_bid_price", "description": "Average bid price"},
    "A07": {"name": "Marginal bid price", "slug": "marginal_bid_price", "description": "Marginal bid price"},
}


# ── Business types ─────────────────────────────────────────────────────────

BUSINESS_TYPES: dict[str, CodeEntry] = {
    "A25": {"name": "General capacity information", "slug": "general_capacity", "description": "General capacity information"},
    "A29": {"name": "Already allocated capacity (AAC)", "slug": "aac", "description": "Already allocated capacity"},
    "A43": {"name": "Requested capacity (without price)", "slug": "requested_capacity", "description": "Requested capacity without price"},
    "A46": {"name": "System Operator redispatching", "slug": "so_redispatching", "description": "System operator redispatching"},
    "A53": {"name": "Planned maintenance", "slug": "planned_maintenance", "description": "Planned maintenance"},
    "A54": {"name": "Unplanned outage", "slug": "unplanned_outage", "description": "Unplanned outage"},
    "A85": {"name": "Internal redispatch", "slug": "internal_redispatch", "description": "Internal redispatch"},
    "A95": {"name": "Frequency containment reserve", "slug": "fcr", "description": "Frequency containment reserve"},
    "A96": {"name": "Automatic frequency restoration reserve", "slug": "afrr", "description": "Automatic frequency restoration reserve"},
    "A97": {"name": "Manual frequency restoration reserve", "slug": "mfrr", "description": "Manual frequency restoration reserve"},
    "A98": {"name": "Replacement reserve", "slug": "rr", "description": "Replacement reserve"},
    "B95": {"name": "Procured capacity", "slug": "procured_capacity", "description": "Procured capacity"},
    "C22": {"name": "Shared balancing reserve capacity", "slug": "shared_reserve", "description": "Shared balancing reserve capacity"},
    "C23": {"name": "Share of reserve capacity", "slug": "share_reserve", "description": "Share of reserve capacity"},
    "C24": {"name": "Actual reserve capacity", "slug": "actual_reserve", "description": "Actual reserve capacity"},
}


# ── Market agreement types ─────────────────────────────────────────────────

MARKET_AGREEMENT_TYPES: dict[str, CodeEntry] = {
    "A01": {"name": "Daily", "slug": "daily", "description": "Daily"},
    "A02": {"name": "Weekly", "slug": "weekly", "description": "Weekly"},
    "A03": {"name": "Monthly", "slug": "monthly", "description": "Monthly"},
    "A04": {"name": "Yearly", "slug": "yearly", "description": "Yearly"},
    "A05": {"name": "Total", "slug": "total", "description": "Total"},
    "A06": {"name": "Long term", "slug": "long_term", "description": "Long term"},
    "A07": {"name": "Intraday", "slug": "intraday", "description": "Intraday"},
    "A13": {"name": "Hourly", "slug": "hourly", "description": "Hourly"},
}


# ── Document status ────────────────────────────────────────────────────────

DOC_STATUS: dict[str, CodeEntry] = {
    "A01": {"name": "Intermediate", "slug": "intermediate", "description": "Intermediate"},
    "A02": {"name": "Final", "slug": "final", "description": "Final"},
    "A05": {"name": "Active", "slug": "active", "description": "Active"},
    "A09": {"name": "Cancelled", "slug": "cancelled", "description": "Cancelled"},
    "A13": {"name": "Withdrawn", "slug": "withdrawn", "description": "Withdrawn"},
    "X01": {"name": "Estimated", "slug": "estimated", "description": "Estimated"},
}


# ── Public lookup functions ────────────────────────────────────────────────


def lookup_area(identifier: str) -> str:
    """Resolve a country identifier to its ENTSO-E EIC area code.

    Accepts any of:
    - ISO code: ``"FR"``, ``"DE_LU"``
    - Country name: ``"France"``, ``"Germany/Luxembourg"``
    - EIC code: ``"10YFR-RTE------C"``

    Args:
        identifier: Country identifier in any supported format.

    Returns:
        The EIC area code string.

    Raises:
        InvalidParameterError: If the identifier is not recognized.
    """
    from .exceptions import InvalidParameterError

    raw = identifier.strip()
    key = raw.upper().replace(" ", "_")

    # Try ISO code
    if key in AREA_CODES:
        return AREA_CODES[key]

    # Try EIC code directly
    if raw in EIC_TO_ISO:
        return raw

    # Try country name
    if raw.lower() in _NAME_TO_ISO:
        return AREA_CODES[_NAME_TO_ISO[raw.lower()]]

    raise InvalidParameterError(
        f"Unknown country: '{identifier}'. "
        f"Available: {', '.join(sorted(AREA_CODES.keys()))}"
    )


def lookup_psr(identifier: str) -> str:
    """Resolve a PSR type identifier to its ENTSO-E code.

    Accepts any of:
    - ENTSO-E code: ``"B16"``
    - Full name: ``"Solar"``, ``"Wind Onshore"``
    - Shorthand: ``"solar"``, ``"wind_onshore"``, ``"gas"``

    Args:
        identifier: PSR type code, name, or shorthand.

    Returns:
        The ENTSO-E PSR type code (e.g., ``"B16"``).

    Raises:
        InvalidParameterError: If the identifier is not recognized.
    """
    from .exceptions import InvalidParameterError

    raw = identifier.strip()
    key = raw.upper()

    # Try code directly
    if key in PSR_TYPES:
        return key

    # Try name or shorthand
    if raw.lower() in _PSR_NAME_TO_CODE:
        return _PSR_NAME_TO_CODE[raw.lower()]

    raise InvalidParameterError(
        f"Unknown PSR type: '{identifier}'. "
        f"Available shorthands: {', '.join(sorted(PSR_CODES.keys()))}. "
        f"Available codes: {', '.join(sorted(PSR_TYPES.keys()))}"
    )


def country_name(identifier: str) -> str:
    """Get the human-readable name for a country/area.

    Accepts ISO code, EIC code, or name (returned as-is).

    Args:
        identifier: Country identifier in any supported format.

    Returns:
        Human-readable country name (e.g., ``"France"``).

    Raises:
        InvalidParameterError: If the identifier is not recognized.
    """
    from .exceptions import InvalidParameterError

    raw = identifier.strip()
    key = raw.upper().replace(" ", "_")

    # Try ISO code
    if key in COUNTRY_NAMES:
        return COUNTRY_NAMES[key]

    # Try EIC code
    if raw in EIC_TO_ISO:
        return COUNTRY_NAMES.get(EIC_TO_ISO[raw], EIC_TO_ISO[raw])

    # Try name (return as-is if it matches)
    if raw.lower() in _NAME_TO_ISO:
        return COUNTRY_NAMES[_NAME_TO_ISO[raw.lower()]]

    raise InvalidParameterError(
        f"Unknown country: '{identifier}'. "
        f"Available: {', '.join(sorted(AREA_CODES.keys()))}"
    )


def psr_name(identifier: str) -> str:
    """Get the human-readable name for a PSR type.

    Accepts code or name (returned as-is).

    Args:
        identifier: PSR type code (e.g., ``"B16"``) or name.

    Returns:
        Human-readable name (e.g., ``"Solar"``).
    """
    code = lookup_psr(identifier)
    return PSR_TYPES[code]["name"]
