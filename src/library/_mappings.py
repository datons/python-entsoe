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

# PSR (Power System Resource) type codes
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


def lookup_area(country: str) -> str:
    """Resolve a country code to its ENTSO-E EIC area code.

    Args:
        country: ISO country code (e.g., "FR", "DE_LU").

    Returns:
        The EIC area code string.

    Raises:
        InvalidParameterError: If the country code is not recognized.
    """
    from .exceptions import InvalidParameterError

    code = country.upper().strip()
    if code not in AREA_CODES:
        raise InvalidParameterError(
            f"Unknown country code: '{country}'. "
            f"Available: {', '.join(sorted(AREA_CODES.keys()))}"
        )
    return AREA_CODES[code]
