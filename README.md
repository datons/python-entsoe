# python-entsoe

Python client for the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) API.

Typed, namespace-organized access to European electricity market data — load, prices, generation, transmission, and balancing.

```bash
pip install python-entsoe
```

## Quick Start

```python
from entsoe import Client

client = Client()  # reads ENTSOE_API_KEY from environment

df = client.load.actual("2024-06-01", "2024-06-08", country="FR")
```

Strings are interpreted as timestamps in `Europe/Brussels` (CET — the ENTSO-E standard). You can override this per-client or pass `pd.Timestamp` objects directly:

```python
client = Client(tz="UTC")  # override default timezone

# pd.Timestamp still works — its timezone takes priority
import pandas as pd
start = pd.Timestamp("2024-06-01", tz="Europe/Paris")
df = client.load.actual(start, "2024-06-08", country="FR")
```

Every method returns a `pandas.DataFrame` with a `timestamp` column (UTC) and a `value` column.

## Authentication

Get a free API key at https://transparency.entsoe.eu/ (register, then request a token via email).

Set it as an environment variable:

```bash
export ENTSOE_API_KEY=your-token-here
```

Or pass it directly:

```python
client = Client(api_key="your-token-here")
```

## API Reference

### `client.load`

| Method | Description | Parameters |
|--------|-------------|------------|
| `actual(start, end, country)` | Actual total system load | `country`: ISO code (e.g., `"FR"`) |
| `forecast(start, end, country)` | Day-ahead load forecast | `country`: ISO code |

```python
df = client.load.actual(start, end, country="FR")
df = client.load.forecast(start, end, country="FR")
```

### `client.prices`

| Method | Description | Parameters |
|--------|-------------|------------|
| `day_ahead(start, end, country)` | Day-ahead market prices (EUR/MWh) | `country`: ISO code |

```python
df = client.prices.day_ahead(start, end, country="FR")
# Returns: timestamp, value, currency, price_unit
```

### `client.generation`

| Method | Description | Parameters |
|--------|-------------|------------|
| `actual(start, end, country, psr_type=None)` | Actual generation per type | `psr_type`: filter by fuel (optional) |
| `forecast(start, end, country, psr_type=None)` | Wind & solar forecast | `psr_type`: filter by fuel (optional) |
| `installed_capacity(start, end, country, psr_type=None)` | Installed capacity per type | `psr_type`: filter by fuel (optional) |
| `per_plant(start, end, country, psr_type=None)` | Generation per production unit | `psr_type`: filter by fuel (optional) |

```python
# All generation types
df = client.generation.actual(start, end, country="FR")

# Solar only
df = client.generation.actual(start, end, country="FR", psr_type="B16")

# Installed capacity
df = client.generation.installed_capacity(start, end, country="FR")
```

### `client.transmission`

| Method | Description | Parameters |
|--------|-------------|------------|
| `crossborder_flows(start, end, country_from, country_to)` | Physical cross-border flows | Two country codes |
| `scheduled_exchanges(start, end, country_from, country_to)` | Scheduled commercial exchanges | Two country codes |
| `net_transfer_capacity(start, end, country_from, country_to)` | Day-ahead NTC | Two country codes |

```python
df = client.transmission.crossborder_flows(
    start, end, country_from="FR", country_to="ES"
)
```

### `client.balancing`

| Method | Description | Parameters |
|--------|-------------|------------|
| `imbalance_prices(start, end, country)` | System imbalance prices | `country`: ISO code |
| `imbalance_volumes(start, end, country)` | System imbalance volumes | `country`: ISO code |

```python
df = client.balancing.imbalance_prices(start, end, country="FR")
```

## Country Codes

Use standard ISO codes. Some bidding zones have specific codes:

| Code | Area |
|------|------|
| `FR` | France |
| `DE_LU` | Germany/Luxembourg (bidding zone) |
| `ES` | Spain |
| `NL` | Netherlands |
| `BE` | Belgium |
| `IT` | Italy |
| `IT_NORTH` | Italy North |
| `NO_1` .. `NO_5` | Norway zones |
| `SE_1` .. `SE_4` | Sweden zones |
| `DK_1`, `DK_2` | Denmark zones |

> **Note:** For day-ahead prices and balancing data, use `DE_LU` instead of `DE`. See [data availability notes](docs/data-availability.md) for details.

Full list of 60+ supported areas in [`_mappings.py`](src/entsoe/_mappings.py).

## PSR Types (Fuel Types)

Use PSR codes to filter generation by fuel type:

| Code | Fuel Type |
|------|-----------|
| `B01` | Biomass |
| `B04` | Fossil Gas |
| `B05` | Fossil Hard coal |
| `B06` | Fossil Oil |
| `B10` | Hydro Pumped Storage |
| `B11` | Hydro Run-of-river |
| `B12` | Hydro Water Reservoir |
| `B14` | Nuclear |
| `B16` | Solar |
| `B18` | Wind Offshore |
| `B19` | Wind Onshore |

Full list in [`_mappings.py`](src/entsoe/_mappings.py). Human-readable names available via:

```python
from entsoe._mappings import PSR_TYPES
print(PSR_TYPES["B16"])  # "Solar"
```

## Timestamps

All `start` and `end` parameters accept **date strings** or **tz-aware `pd.Timestamp`** objects:

```python
# Simple — just strings (uses client's default tz: Europe/Brussels)
df = client.load.actual("2024-01-01", "2024-01-07", country="FR")

# pd.Timestamp with explicit timezone — takes priority over default
df = client.load.actual(
    pd.Timestamp("2024-01-01", tz="Europe/Paris"),
    pd.Timestamp("2024-01-07", tz="Europe/Paris"),
    country="FR",
)

# Mixing is fine
df = client.load.actual("2024-01-01", pd.Timestamp("2024-01-07", tz="UTC"), country="FR")

# Naive pd.Timestamp (no tz) — still raises InvalidParameterError
start = pd.Timestamp("2024-01-01")  # ← no tz, will error
```

Returned timestamps are always in **UTC**.

## Features

- **Autocomplete-friendly** — type `client.` and see all domains, then drill into methods
- **Automatic year-splitting** — requests spanning more than 1 year are split transparently
- **ZIP handling** — endpoints returning compressed responses are decompressed automatically
- **Retry with backoff** — rate-limited requests (HTTP 429) are retried with exponential backoff
- **Clear errors** — `NoDataError`, `InvalidParameterError`, `RateLimitError` with descriptive messages

## Error Handling

```python
from entsoe import Client, NoDataError, InvalidParameterError

client = Client()

try:
    df = client.prices.day_ahead(start, end, country="FR")
except NoDataError:
    print("No data available for this period")
except InvalidParameterError as e:
    print(f"Bad parameters: {e}")
```

## Examples

See the [`examples/`](examples/) directory for Jupyter notebooks with plotly visualizations:

- [`load.ipynb`](examples/load.ipynb) — actual load, forecast comparison, multi-country profiles
- [`prices.ipynb`](examples/prices.ipynb) — day-ahead prices, distributions, hourly heatmap
- [`generation.ipynb`](examples/generation.ipynb) — generation mix, solar vs wind, installed capacity
- [`transmission.ipynb`](examples/transmission.ipynb) — cross-border flows, bidirectional charts, NTC
- [`balancing.ipynb`](examples/balancing.ipynb) — imbalance prices, multi-country, distribution

## Development

```bash
git clone https://github.com/jsulopzs/python-entsoe.git
cd python-entsoe
uv sync

# Run tests (requires ENTSOE_API_KEY in .env)
uv run pytest tests/ -v

# Regenerate example notebooks
uv run python scripts/generate_notebooks.py
```

## License

MIT
