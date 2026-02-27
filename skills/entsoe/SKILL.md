---
name: entsoe
description: Query European electricity market data (ENTSO-E Transparency Platform). Use when the user asks about electricity prices, load, generation, transmission, or balancing data for European countries.
version: 1.0.0
---

# ENTSO-E Data Assistant

You have access to the `python-entsoe` CLI and library for querying the ENTSO-E Transparency Platform (European electricity market data).

## CLI Reference

### Prices

```bash
# Day-ahead prices for one country
entsoe prices day-ahead -s 2024-06-01 -e 2024-06-08 --country FR

# Multi-country
entsoe prices day-ahead -s 2024-06-01 -e 2024-06-08 --country FR --country ES
```

### Load

```bash
# Actual total system load
entsoe load actual -s 2024-06-01 -e 2024-06-08 --country FR

# Day-ahead load forecast
entsoe load forecast -s 2024-06-01 -e 2024-06-08 --country FR
```

### Generation

```bash
# Actual generation per type (all types)
entsoe generation actual -s 2024-06-01 -e 2024-06-08 --country FR

# Filter by PSR type
entsoe generation actual -s 2024-06-01 -e 2024-06-08 --country FR --psr solar --psr wind_onshore

# Generation forecast (wind/solar)
entsoe generation forecast -s 2024-06-01 -e 2024-06-08 --country FR

# Installed capacity
entsoe generation capacity -s 2024-06-01 -e 2024-06-08 --country FR

# Per production unit
entsoe generation per-plant -s 2024-06-01 -e 2024-06-08 --country FR
```

### Transmission

```bash
# Physical cross-border flows
entsoe transmission flows -s 2024-06-01 -e 2024-06-08 --from FR --to ES

# Scheduled commercial exchanges
entsoe transmission exchanges -s 2024-06-01 -e 2024-06-08 --from FR --to ES

# Net transfer capacity
entsoe transmission capacity -s 2024-06-01 -e 2024-06-08 --from FR --to ES
```

### Balancing

```bash
# Imbalance prices
entsoe balancing prices -s 2024-06-01 -e 2024-06-08 --country FR

# Imbalance volumes
entsoe balancing volumes -s 2024-06-01 -e 2024-06-08 --country FR
```

### Exec (ad-hoc pandas expressions)

Run any pandas expression against fetched data:

```bash
# Descriptive statistics on prices
entsoe exec prices day-ahead -s 2024-06-01 -e 2024-06-08 -c FR -x "df.describe()"

# Daily mean load
entsoe exec load actual -s 2024-06-01 -e 2024-06-08 -c FR -x "df.resample('D').mean()"

# Generation with PSR filter
entsoe exec generation actual -s 2024-06-01 -e 2024-06-08 -c FR --psr solar -x "df.head(20)"

# Transmission analysis
entsoe exec transmission flows -s 2024-06-01 -e 2024-06-08 --from FR --to ES -x "df.describe()"
```

### Output formats

All commands support:

```bash
--format table       # Default: Rich table in terminal
--format csv         # CSV output
--format json        # JSON output
--output file.csv    # Write to file instead of stdout
```

## Country Codes

| Code | Country | Code | Country |
|------|---------|------|---------|
| AT | Austria | IT | Italy |
| BE | Belgium | LT | Lithuania |
| BG | Bulgaria | LU | Luxembourg |
| CH | Switzerland | LV | Latvia |
| CZ | Czech Republic | NL | Netherlands |
| DE_LU | Germany/Luxembourg | NO | Norway |
| DK | Denmark | PL | Poland |
| EE | Estonia | PT | Portugal |
| ES | Spain | RO | Romania |
| FI | Finland | RS | Serbia |
| FR | France | SE | Sweden |
| GB | Great Britain | SI | Slovenia |
| GR | Greece | SK | Slovakia |
| HR | Croatia | TR | Turkey |
| HU | Hungary | UA | Ukraine |

Bidding zones: `DK_1`, `DK_2`, `NO_1`–`NO_5`, `SE_1`–`SE_4`, `IT_NORTH`, `IT_CNOR`, `IT_CSUD`, `IT_SUD`, `IT_SICI`, `IT_SARD`, `DE_AT_LU`, `IE_SEM`.

## PSR Types (Generation)

| Shorthand | Full Name | Code |
|-----------|-----------|------|
| solar | Solar | B16 |
| wind_onshore | Wind Onshore | B19 |
| wind_offshore | Wind Offshore | B18 |
| nuclear | Nuclear | B14 |
| gas | Fossil Gas | B04 |
| hard_coal | Fossil Hard coal | B05 |
| lignite | Fossil Brown coal/Lignite | B02 |
| hydro_reservoir | Hydro Water Reservoir | B12 |
| run_of_river | Hydro Run-of-river | B11 |
| pumped_storage | Hydro Pumped Storage | B10 |
| biomass | Biomass | B01 |
| oil | Fossil Oil | B06 |
| geothermal | Geothermal | B09 |
| waste | Waste | B17 |
| other | Other | B20 |

Use shorthands with `--psr` (e.g. `--psr solar --psr wind_onshore`), or ENTSO-E codes (e.g. `--psr B16`).

## Python Library

```python
from entsoe import Client

client = Client()  # reads config file, then ENTSOE_API_KEY env var

# Prices
df = client.prices.day_ahead("2024-06-01", "2024-06-08", country="FR")
df = client.prices.day_ahead("2024-06-01", "2024-06-08", country=["FR", "ES"])

# Load
df = client.load.actual("2024-06-01", "2024-06-08", country="FR")
df = client.load.forecast("2024-06-01", "2024-06-08", country="FR")

# Generation
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR")
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR", psr_type="solar")
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR", psr_type=["solar", "wind_onshore"])
df = client.generation.forecast("2024-06-01", "2024-06-08", country="FR")
df = client.generation.installed_capacity("2024-06-01", "2024-06-08", country="FR")
df = client.generation.per_plant("2024-06-01", "2024-06-08", country="FR")

# Transmission
df = client.transmission.crossborder_flows("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")
df = client.transmission.scheduled_exchanges("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")
df = client.transmission.net_transfer_capacity("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")

# Balancing
df = client.balancing.imbalance_prices("2024-06-01", "2024-06-08", country="FR")
df = client.balancing.imbalance_volumes("2024-06-01", "2024-06-08", country="FR")
```

## Configuration

```bash
# Store your API key persistently (recommended)
entsoe config set api-key YOUR_KEY

# Verify it's stored
entsoe config get api-key
```

The config file is stored at `~/.config/entsoe/config.toml`.

## Key Conventions

- **Timezone**: All string dates are interpreted in Europe/Brussels (CET) by default
- **Auto year-splitting**: Date ranges exceeding 1 year are automatically split into yearly API requests
- **Rate limiting**: ENTSO-E has a 400-request/minute limit; the library handles retries
- **Multi-value support**: Pass lists for country or psr_type to get combined results with label columns
- **Transmission**: Uses `--from`/`--to` instead of `--country`; multi-value adds a `border` column
- **API key resolution**: config file (`~/.config/entsoe/config.toml`) > `ENTSOE_API_KEY` env var
- **No caching**: Data is fetched fresh on each request (unlike python-esios)
- **Custom exceptions**: `ENTSOEError`, `AuthenticationError`, `APIResponseError`, `InvalidParameterError`, `NetworkError`
