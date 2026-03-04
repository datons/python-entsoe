---
name: entsoe
description: Query European electricity market data (ENTSO-E Transparency Platform). Use when the user asks about electricity prices, load, generation, transmission, or balancing data for European countries.
version: 2.0.0
---

# ENTSO-E Data Assistant

You have access to the `python-entsoe` library and CLI for querying the ENTSO-E Transparency Platform (European electricity market data).

## When to use what

- **Python scripts** (default): reproducible, composable, saveable. Use for any data work the user will want to keep or iterate on.
- **CLI**: quick one-shot lookups, exploration, sanity checks. Use when the user wants a fast answer they won't need again.
- **If unsure**: ask the user whether they want a script or a quick CLI check.

## Python Library (default)

```python
from entsoe import Client

client = Client()  # reads config file, then ENTSOE_API_KEY env var

# --- Prices ---
df = client.prices.day_ahead("2024-06-01", "2024-06-08", country="FR")
df = client.prices.day_ahead("2024-06-01", "2024-06-08", country=["FR", "ES"])

# --- Load ---
df = client.load.actual("2024-06-01", "2024-06-08", country="FR")
df = client.load.forecast("2024-06-01", "2024-06-08", country="FR")

# --- Generation ---
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR")
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR", psr_type="solar")
df = client.generation.actual("2024-06-01", "2024-06-08", country="FR", psr_type=["solar", "wind_onshore"])
df = client.generation.forecast("2024-06-01", "2024-06-08", country="FR")
df = client.generation.installed_capacity("2024-06-01", "2024-06-08", country="FR")
df = client.generation.per_plant("2024-06-01", "2024-06-08", country="FR")

# --- Transmission ---
df = client.transmission.crossborder_flows("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")
df = client.transmission.scheduled_exchanges("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")
df = client.transmission.net_transfer_capacity("2024-06-01", "2024-06-08", country_from="FR", country_to="ES")

# --- Balancing ---
df = client.balancing.imbalance_prices("2024-06-01", "2024-06-08", country="FR")
df = client.balancing.imbalance_volumes("2024-06-01", "2024-06-08", country="FR")
```

### Key conventions

- **Timezone**: All string dates are interpreted in Europe/Brussels (CET) by default
- **Auto year-splitting**: Date ranges > 1 year are automatically split into yearly API requests
- **Rate limiting**: ENTSO-E has a 400-request/minute limit; the library handles retries
- **Multi-value support**: Pass lists for `country` or `psr_type` to get combined results with label columns
- **Transmission**: Uses `country_from`/`country_to`; multi-value adds a `border` column
- **No caching**: Data is fetched fresh on each request
- **Custom exceptions**: `ENTSOEError`, `AuthenticationError`, `APIResponseError`, `InvalidParameterError`, `NetworkError`

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

Use shorthands with `psr_type=` (Python) or `--psr` (CLI), e.g. `psr_type="solar"` or `--psr solar`.

## CLI Reference (quick lookups)

### Catalog (offline)

```bash
entsoe catalog list              # All data categories and endpoints
entsoe catalog show prices       # Detailed info for a category
entsoe catalog countries         # Country/bidding zone codes
entsoe catalog psr               # PSR (generation) types
entsoe catalog borders           # Border groups and interconnections
```

### Fetch data

```bash
# Prices
entsoe prices day-ahead -s 2024-06-01 -e 2024-06-08 -c FR
entsoe prices day-ahead -P week -c FR,ES          # Period shorthand

# Load
entsoe load actual -P month -c FR
entsoe load forecast -s 2024-06-01 -e 2024-06-08 -c FR

# Generation
entsoe generation actual -P week -c FR --psr solar --psr wind_onshore
entsoe generation forecast -P week -c FR
entsoe generation capacity -s 2024-01-01 -e 2024-12-31 -c FR
entsoe generation per-plant -P week -c FR

# Transmission
entsoe transmission flows -P week --from FR --to ES
entsoe transmission exchanges -P week --border ES-*,FR-*

# Balancing
entsoe balancing prices -P week -c FR
entsoe balancing volumes -P week -c FR
```

### Exec (ad-hoc pandas)

`exec` is a subcommand **within each namespace**:

```bash
entsoe prices exec day-ahead -P week -c FR -x "df.describe()"
entsoe load exec actual -P 7d -c FR -x "df.resample('D').mean()"
entsoe generation exec actual -P month -c FR --psr solar -x "df.head(20)"
entsoe transmission exec flows -P week --from FR --to ES -x "df.describe()"
entsoe balancing exec prices -P week -c NL -x "df.describe()"
```

### Period shorthand (`-P`)

All data commands support `-P` as an alternative to `--start`/`--end`:

```
-P today, -P yesterday, -P week, -P month, -P ytd, -P 14d
```

### Output options

```
--format table|csv|json   (default: table)
--output file.csv         (write to file instead of stdout)
```

## Configuration

```bash
entsoe config set api-key YOUR_KEY
entsoe config get api-key
```

Config file: `~/.config/entsoe/config.toml`. API key resolution: config file > `ENTSOE_API_KEY` env var.
