# Data Dimensions Reference

This document lists all ENTSO-E codes and their meanings as returned by the library.

## Power System Resource (PSR) Types

Used in generation endpoints to identify fuel/technology type.

| Code | Name |
|------|------|
| B01 | Biomass |
| B02 | Fossil Brown coal/Lignite |
| B03 | Fossil Coal-derived gas |
| B04 | Fossil Gas |
| B05 | Fossil Hard coal |
| B06 | Fossil Oil |
| B07 | Fossil Oil shale |
| B08 | Fossil Peat |
| B09 | Geothermal |
| B10 | Hydro Pumped Storage |
| B11 | Hydro Run-of-river and poundage |
| B12 | Hydro Water Reservoir |
| B13 | Marine |
| B14 | Nuclear |
| B15 | Other renewable |
| B16 | Solar |
| B17 | Waste |
| B18 | Wind Offshore |
| B19 | Wind Onshore |
| B20 | Other |

**Example:**
```python
df = client.generation.actual_per_type("2024-01-01", "2024-01-07", country="FR")
# df['psr_type'] contains values like "Solar", "Wind Onshore", "Nuclear", etc.
```

---

## Process Types

Indicates the market process or forecast horizon.

| Code | Name | Endpoint(s) |
|------|------|-------------|
| A01 | Day-ahead | `prices.day_ahead()` |
| A16 | Realised | Load/generation actual values |
| A18 | Intraday total | Intraday forecasts |
| A31 | Week-ahead | Week-ahead forecasts |
| A32 | Month-ahead | Month-ahead forecasts |
| A33 | Year-ahead | Year-ahead forecasts |

**Example:**
```python
df = client.load.actual_load("2024-01-01", "2024-01-07", country="FR")
# Implicit processType = A16 (realised/actual)

df = client.load.load_forecast("2024-01-01", "2024-01-07", country="FR")
# Implicit processType = A01 (day-ahead forecast)
```

---

## Price Categories

Indicates the price category type (used across balancing endpoints).

| Code | Name | Used in |
|------|------|---------|
| A04 | Long | Imbalance prices — system has excess (long position) |
| A05 | Short | Imbalance prices — system has deficit (short position) |
| A06 | Average bid price | Contracted reserves, activation prices |
| A07 | Marginal bid price | Activated balancing energy prices |

**Important:** For imbalance prices, the same timestamps appear twice — once for each direction (Long and Short).

**Example:**
```python
df = client.balancing.imbalance_prices("2024-06-01", "2024-06-02", country="FR")

# Each timestamp has two rows:
#                   timestamp  value price_category
# 0  2024-06-01 00:00:00+00:00    0.44           Long
# 1  2024-06-01 00:00:00+00:00    0.50          Short

# Filter by direction:
df_long = df[df['price_category'] == 'Long']
df_short = df[df['price_category'] == 'Short']
```

---

## Reserve Types

For balancing reserve queries (e.g., `balancing.contracted_reserve_prices()`).

| Code | Name | Abbreviation |
|------|------|--------------|
| A52 | Frequency Containment Reserve | FCR |
| A51 | Automatic Frequency Restoration Reserve | aFRR |
| A47 | Manual Frequency Restoration Reserve | mFRR |

**Example:**
```python
df_fcr = client.balancing.contracted_reserve_prices(
    "2024-06-01", "2024-06-08", 
    country="NL", 
    reserve_type="fcr"  # A52
)
# df['reserve_type'] = "FCR"
```

---

## Area/Country Codes

ISO 3166-1 alpha-2 codes are used for the `country` parameter.

**Common countries:**
- `FR` — France
- `DE` — Germany
- `NL` — Netherlands
- `BE` — Belgium
- `ES` — Spain
- `IT` — Italy
- `GB` — Great Britain
- `CH` — Switzerland
- `NO` — Norway
- `SE` — Sweden
- `PL` — Poland

**Special cases:**
- `DE_LU` — Germany/Luxembourg market zone
- `IT_NORTH`, `IT_CNOR`, `IT_CSUD`, `IT_SUD`, `IT_SICI`, `IT_SARD` — Italy regional zones
- `DK_1`, `DK_2` — Denmark regional zones
- `NO_1`, `NO_2`, `NO_3`, `NO_4`, `NO_5` — Norway regional zones
- `SE_1`, `SE_2`, `SE_3`, `SE_4` — Sweden regional zones

For a complete list, see the `AREA_CODES` dictionary in `src/entsoe/_mappings.py`.

---

## Tips for Working with Dimensions

### 1. Filtering by category
```python
# Get only solar generation
df_solar = df[df['psr_type'] == 'Solar']

# Get only long (excess) imbalance prices
df_long = df[df['price_category'] == 'Long']
```

### 2. Unique values
```python
# See all psr_types in the result
print(df['psr_type'].unique())

# See all reserve types
print(df['reserve_type'].unique())
```

### 3. Grouping and aggregation
```python
# Sum generation by fuel type
df.groupby('psr_type')['value'].sum()

# Average imbalance price by direction
df.groupby('price_category')['value'].mean()
```

---

## References

- ENTSO-E Transparency Platform: https://transparency.entsoe.eu/
- ENTSO-E GL Codes: https://www.entsoe.eu/data/data-portal/
