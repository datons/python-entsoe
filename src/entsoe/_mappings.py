"""ENTSO-E area codes, document types, and PSR type mappings."""

# Country code (ISO 3166-1 alpha-2) → ENTSO-E EIC area code
AREA_CODES: dict[str, str] = {
    "AL": "10YAL-KESH-----5",
    "AT": "10YAT-APG------L",
    "BA": "10YBA-JPCC-----D",
    "BE": "10YBE----------2",
    "BG": "10YCA-BULGARIA-R",
    "CH": "10YCH-SWISSGRIDZ",
    "CZ": "10YCZ-CEPS-----N",
    "DE": "10Y1001A1001A83F",
    "DE_LU": "10Y1001A1001A82H",
    "DE_AT_LU": "10Y1001A1001A63L",
    "DK": "10Y1001A1001A65H",
    "DK_1": "10YDK-1--------W",
    "DK_2": "10YDK-2--------M",
    "EE": "10Y1001A1001A39I",
    "ES": "10YES-REE------0",
    "FI": "10YFI-1--------U",
    "FR": "10YFR-RTE------C",
    "GB": "10YGB----------A",
    "GR": "10YGR-HTSO-----Y",
    "HR": "10YHR-HEP------M",
    "HU": "10YHU-MAVIR----U",
    "IE": "10YIE-1001A00010",
    "IE_SEM": "10Y1001A1001A59C",
    "IT": "10YIT-GRTN-----B",
    "IT_NORTH": "10Y1001A1001A73I",
    "IT_CNOR": "10Y1001A1001A70O",
    "IT_CSUD": "10Y1001A1001A71M",
    "IT_SUD": "10Y1001A1001A788",
    "IT_SICI": "10Y1001A1001A74G",
    "IT_SARD": "10Y1001A1001A75E",
    "LT": "10YLT-1001A0008Q",
    "LU": "10YLU-CEGEDEL-NQ",
    "LV": "10YLV-1001A00074",
    "ME": "10YCS-CG-TSO---S",
    "MK": "10YMK-MEPSO----8",
    "MT": "10Y1001A1001A93C",
    "NL": "10YNL----------L",
    "NO": "10YNO-0--------C",
    "NO_1": "10YNO-1--------2",
    "NO_2": "10YNO-2--------T",
    "NO_3": "10YNO-3--------J",
    "NO_4": "10YNO-4--------9",
    "NO_5": "10Y1001A1001A48H",
    "PL": "10YPL-AREA-----S",
    "PT": "10YPT-REN------W",
    "RO": "10YRO-TEL------P",
    "RS": "10YCS-SERBIATSOV",
    "SE": "10YSE-1--------K",
    "SE_1": "10Y1001A1001A44P",
    "SE_2": "10Y1001A1001A45N",
    "SE_3": "10Y1001A1001A46L",
    "SE_4": "10Y1001A1001A47J",
    "SI": "10YSI-ELES-----O",
    "SK": "10YSK-SEPS-----K",
    "TR": "10YTR-TEIAS----W",
    "UA": "10Y1001C--00003F",
    "UK": "10Y1001A1001A92E",
    "XK": "10Y1001C--00100H",
}

# ISO code → human-readable country/area name
COUNTRY_NAMES: dict[str, str] = {
    "AL": "Albania",
    "AT": "Austria",
    "BA": "Bosnia and Herzegovina",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DE_LU": "Germany/Luxembourg",
    "DE_AT_LU": "Germany/Austria/Luxembourg",
    "DK": "Denmark",
    "DK_1": "Denmark (West)",
    "DK_2": "Denmark (East)",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "Great Britain",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IE_SEM": "Ireland (SEM)",
    "IT": "Italy",
    "IT_NORTH": "Italy (North)",
    "IT_CNOR": "Italy (Central North)",
    "IT_CSUD": "Italy (Central South)",
    "IT_SUD": "Italy (South)",
    "IT_SICI": "Italy (Sicily)",
    "IT_SARD": "Italy (Sardinia)",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "ME": "Montenegro",
    "MK": "North Macedonia",
    "MT": "Malta",
    "NL": "Netherlands",
    "NO": "Norway",
    "NO_1": "Norway (South-East)",
    "NO_2": "Norway (South-West)",
    "NO_3": "Norway (Central)",
    "NO_4": "Norway (North)",
    "NO_5": "Norway (West)",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RS": "Serbia",
    "SE": "Sweden",
    "SE_1": "Sweden (Luleå)",
    "SE_2": "Sweden (Sundsvall)",
    "SE_3": "Sweden (Stockholm)",
    "SE_4": "Sweden (Malmö)",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "TR": "Turkey",
    "UA": "Ukraine",
    "UK": "United Kingdom",
    "XK": "Kosovo",
}

# Document type codes used in API requests
DOCUMENT_TYPES: dict[str, str] = {
    # Load
    "actual_load": "A65",
    "load_forecast": "A65",
    # Prices
    "day_ahead_prices": "A44",
    # Generation
    "actual_generation_per_type": "A75",
    "actual_generation_per_plant": "A73",
    "generation_forecast_wind_solar": "A69",
    "generation_forecast": "A71",
    "installed_capacity": "A68",
    "installed_capacity_per_unit": "A71",
    # Transmission
    "physical_crossborder_flows": "A11",
    "scheduled_exchanges": "A09",
    "net_transfer_capacity": "A61",
    # Balancing
    "imbalance_prices": "A85",
    "imbalance_volumes": "A86",
    "contracted_reserve_prices": "A89",
    "activated_balancing_energy_prices": "A84",
}

# Process type codes
PROCESS_TYPES: dict[str, str] = {
    "realised": "A16",
    "day_ahead": "A01",
    "intraday_total": "A18",
    "week_ahead": "A31",
    "month_ahead": "A32",
    "year_ahead": "A33",
}

# PSR (Power System Resource) type codes — code → name
PSR_TYPES: dict[str, str] = {
    "B01": "Biomass",
    "B02": "Fossil Brown coal/Lignite",
    "B03": "Fossil Coal-derived gas",
    "B04": "Fossil Gas",
    "B05": "Fossil Hard coal",
    "B06": "Fossil Oil",
    "B07": "Fossil Oil shale",
    "B08": "Fossil Peat",
    "B09": "Geothermal",
    "B10": "Hydro Pumped Storage",
    "B11": "Hydro Run-of-river and poundage",
    "B12": "Hydro Water Reservoir",
    "B13": "Marine",
    "B14": "Nuclear",
    "B15": "Other renewable",
    "B16": "Solar",
    "B17": "Waste",
    "B18": "Wind Offshore",
    "B19": "Wind Onshore",
    "B20": "Other",
}

# ── Reverse lookups (built once at import time) ──────────────────────────

# EIC area code → ISO code
EIC_TO_ISO: dict[str, str] = {v: k for k, v in AREA_CODES.items()}

# Country name (lowercase) → ISO code
_NAME_TO_ISO: dict[str, str] = {v.lower(): k for k, v in COUNTRY_NAMES.items()}

# PSR name (lowercase) → ENTSO-E code
_PSR_NAME_TO_CODE: dict[str, str] = {v.lower(): k for k, v in PSR_TYPES.items()}


# ── Public lookup functions ──────────────────────────────────────────────


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
    - Name: ``"Solar"``, ``"Wind Onshore"``

    Args:
        identifier: PSR type code or name.

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

    # Try name
    if raw.lower() in _PSR_NAME_TO_CODE:
        return _PSR_NAME_TO_CODE[raw.lower()]

    raise InvalidParameterError(
        f"Unknown PSR type: '{identifier}'. "
        f"Available codes: {', '.join(sorted(PSR_TYPES.keys()))}. "
        f"Available names: {', '.join(sorted(PSR_TYPES.values()))}"
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
    return PSR_TYPES[code]
