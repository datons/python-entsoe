# ENTSO-E Data Availability — Known Issues & Gotchas

Lessons learned while building and testing the `python-entsoe` library against the ENTSO-E Transparency Platform API.

## 1. ZIP-compressed responses

**Affected endpoints:** `imbalance_prices` (A85), `imbalance_volumes` (A86), unavailability queries

**Problem:** These endpoints return ZIP archives instead of raw XML. The response starts with `PK` (ZIP magic bytes) and parsing it as XML fails with:

```
ParseError: not well-formed (invalid token): line 1, column 2
```

**Solution:** Detect ZIP responses by checking the first two bytes (`b"PK"`), extract the XML file(s) inside using `zipfile`, then parse normally. A single ZIP may contain multiple XML files.

## 2. Germany bidding zone (`DE` vs `DE_LU`)

**Affected endpoints:** `prices.day_ahead`, `balancing.imbalance_prices`, `transmission.net_transfer_capacity`

**Problem:** The country code `DE` maps to area `10Y1001A1001A83F` (Germany TSO area), but many data items are published under the `DE_LU` bidding zone (`10Y1001A1001A82H`). Using `DE` returns:

```
NoDataError: No matching data found for Data item ENERGY_PRICES [12.1.D]
(10Y1001A1001A83F, 10Y1001A1001A83F) and interval .
```

**Solution:** Use `DE_LU` (Germany/Luxembourg bidding zone) for:
- Day-ahead prices
- Cross-border flows and scheduled exchanges
- Net transfer capacity

Use `DE` only for load and generation data.

## 3. Imbalance prices — not available for all countries

**Affected endpoint:** `balancing.imbalance_prices` (A85)

**Problem:** `DE_LU` has no imbalance price data:

```
NoDataError: No matching data found for Data item IMBALANCE_PRICES_R3 [17.1.G]
(10Y1001A1001A82H) and interval .
```

**Confirmed working countries:** FR, BE, NL, ES

## 4. Net Transfer Capacity — route-specific availability

**Affected endpoint:** `transmission.net_transfer_capacity` (A61)

**Problem:** NTC data is not available for all country pairs. FR→DE_LU returns:

```
NoDataError: No matching data found for Data item
FORECASTED_TRANSFER_CAPACITIES_EXPLICIT [11.1]
(10Y1001A1001A82H, 10YFR-RTE------C) and interval .
```

**Confirmed working routes:** FR→ES, FR→GB, FR→IT_NORTH

## 5. Imbalance price value tag differs from other endpoints

**Affected endpoint:** `balancing.imbalance_prices` (A85)

**Problem:** Most endpoints use `<quantity>` or `<price.amount>` inside `<Point>` elements. Imbalance prices use a different tag:

```xml
<Point>
  <position>1</position>
  <imbalance_Price.amount>53.37</imbalance_Price.amount>
  <imbalance_Price.category>A04</imbalance_Price.category>
</Point>
```

Parsing with only `quantity` and `price.amount` returns `None` values for all rows.

**Solution:** The XML parser must check for `imbalance_Price.amount` in addition to `quantity` and `price.amount`.

## 6. API key not inherited by Jupyter kernels

**Problem:** When executing notebooks programmatically with `jupyter nbconvert --execute`, the spawned kernel process does not inherit `.env` file variables. All notebooks fail with:

```
ValueError: API key required. Pass api_key= or set the ENTSOE_API_KEY
environment variable.
```

**Solution:** Export the env vars before running nbconvert:

```bash
export $(cat .env | xargs) && uv run jupyter nbconvert --execute ...
```

## Summary table

| Issue | Endpoint | Symptom | Fix |
|-------|----------|---------|-----|
| ZIP responses | imbalance_prices, imbalance_volumes | `ParseError` on XML parse | Detect `PK` magic bytes, unzip first |
| DE vs DE_LU | prices, balancing, transmission | `NoDataError` | Use `DE_LU` for market/price data |
| Country availability | imbalance_prices | `NoDataError` for DE_LU | Use FR, BE, NL, ES instead |
| Route availability | net_transfer_capacity | `NoDataError` for FR→DE_LU | Use FR→ES, FR→GB, FR→IT_NORTH |
| Value tag name | imbalance_prices | All values are `None` | Parse `imbalance_Price.amount` tag |
| Env vars in notebooks | all (via nbconvert) | `ValueError: API key required` | Export env vars before execution |
