"""Generate example notebooks for each domain namespace.

Run: uv run python scripts/generate_notebooks.py

Overwrites examples/*.ipynb with the latest versions.
Edit this file to change notebook content, then re-run.
"""

import nbformat as nbf


def nb(cells: list[tuple[str, str]]) -> nbf.NotebookNode:
    """Create a notebook from a list of (type, source) tuples."""
    notebook = nbf.v4.new_notebook()
    notebook.metadata.update(
        {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
        }
    )
    for cell_type, source in cells:
        if cell_type == "md":
            notebook.cells.append(nbf.v4.new_markdown_cell(source.strip()))
        else:
            notebook.cells.append(nbf.v4.new_code_cell(source.strip()))
    return notebook


# ── Shared setup cell ────────────────────────────────────────────────────

SETUP = """\
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from entsoe import Client

client = Client()"""

SETUP_WITH_MAPPINGS = """\
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from entsoe import Client
from entsoe._mappings import PSR_TYPES

client = Client()"""


# ── Load ─────────────────────────────────────────────────────────────────

load_nb = nb(
    [
        (
            "md",
            """
# Load Data — ENTSO-E Examples

Querying actual electricity load and forecasts from the ENTSO-E Transparency Platform.
""",
        ),
        ("code", SETUP),
        (
            "md",
            """
## 1. Actual Load — France (1 week)
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_load = client.load.actual(start, end, country="FR")
df_load.head()""",
        ),
        (
            "code",
            """\
fig = px.line(
    df_load, x="timestamp", y="value",
    title="Actual Electricity Load — France",
    labels={"value": "Load (MW)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 2. Load Forecast vs Actual
""",
        ),
        (
            "code",
            """\
df_forecast = client.load.forecast(start, end, country="FR")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_load["timestamp"], y=df_load["value"],
    name="Actual", line=dict(color="#636EFA"),
))
fig.add_trace(go.Scatter(
    x=df_forecast["timestamp"], y=df_forecast["value"],
    name="Forecast", line=dict(color="#EF553B", dash="dash"),
))
fig.update_layout(
    title="Actual vs Forecast Load — France",
    yaxis_title="Load (MW)",
    xaxis_title="",
)
fig.show()""",
        ),
        (
            "md",
            """
## 3. Forecast Error
""",
        ),
        (
            "code",
            """\
merged = df_load.merge(df_forecast, on="timestamp", suffixes=("_actual", "_forecast"))
merged["error"] = merged["value_actual"] - merged["value_forecast"]
merged["error_pct"] = merged["error"] / merged["value_actual"] * 100

fig = px.bar(
    merged, x="timestamp", y="error_pct",
    title="Load Forecast Error — France",
    labels={"error_pct": "Error (%)", "timestamp": ""},
    color="error_pct",
    color_continuous_scale="RdBu_r",
    color_continuous_midpoint=0,
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Multi-Country Load Comparison
""",
        ),
        (
            "code",
            """\
start = "2024-06-03"
end = "2024-06-04"

countries = {"FR": "France", "DE_LU": "Germany", "ES": "Spain"}
frames = []
for code, name in countries.items():
    df = client.load.actual(start, end, country=code)
    df["country"] = name
    frames.append(df)

df_multi = pd.concat(frames, ignore_index=True)

fig = px.line(
    df_multi, x="timestamp", y="value", color="country",
    title="Daily Load Profile — 3 Jun 2024",
    labels={"value": "Load (MW)", "timestamp": ""},
)
fig.show()""",
        ),
    ]
)


# ── Prices ───────────────────────────────────────────────────────────────

prices_nb = nb(
    [
        (
            "md",
            """
# Day-Ahead Prices — ENTSO-E Examples

Querying and visualizing day-ahead electricity market prices.
""",
        ),
        ("code", SETUP),
        (
            "md",
            """
## 1. Day-Ahead Prices — France (1 week)
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_prices = client.prices.day_ahead(start, end, country="FR")
df_prices.head()""",
        ),
        (
            "code",
            """\
fig = px.line(
    df_prices, x="timestamp", y="value",
    title="Day-Ahead Prices — France",
    labels={"value": "Price (EUR/MWh)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 2. Multi-Country Price Comparison
""",
        ),
        (
            "code",
            """\
countries = {"FR": "France", "DE_LU": "Germany/Luxembourg", "ES": "Spain", "NL": "Netherlands"}
frames = []
for code, name in countries.items():
    df = client.prices.day_ahead(start, end, country=code)
    df["country"] = name
    frames.append(df)

df_multi = pd.concat(frames, ignore_index=True)

fig = px.line(
    df_multi, x="timestamp", y="value", color="country",
    title="Day-Ahead Prices — Multi-Country Comparison",
    labels={"value": "Price (EUR/MWh)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 3. Price Distribution
""",
        ),
        (
            "code",
            """\
fig = px.box(
    df_multi, x="country", y="value", color="country",
    title="Price Distribution — Week of 1-8 Jun 2024",
    labels={"value": "Price (EUR/MWh)", "country": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Hourly Price Heatmap — France (1 month)
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-07-01"

df_month = client.prices.day_ahead(start, end, country="FR")
df_month["hour"] = df_month["timestamp"].dt.hour
df_month["date"] = df_month["timestamp"].dt.date

pivot = df_month.pivot_table(index="hour", columns="date", values="value")

fig = px.imshow(
    pivot,
    title="Hourly Day-Ahead Prices — France, June 2024",
    labels=dict(x="Date", y="Hour", color="EUR/MWh"),
    aspect="auto",
    color_continuous_scale="RdYlGn_r",
)
fig.show()""",
        ),
    ]
)


# ── Generation ───────────────────────────────────────────────────────────

generation_nb = nb(
    [
        (
            "md",
            """
# Generation Data — ENTSO-E Examples

Querying actual generation per type, renewable output, and installed capacity.
""",
        ),
        ("code", SETUP_WITH_MAPPINGS),
        (
            "md",
            """
## 1. Generation Mix — France (1 week)
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_gen = client.generation.actual(start, end, country="FR")
df_gen["fuel"] = df_gen["psr_type"].map(PSR_TYPES)
df_gen.head()""",
        ),
        (
            "code",
            """\
fig = px.area(
    df_gen, x="timestamp", y="value", color="fuel",
    title="Generation Mix — France",
    labels={"value": "Generation (MW)", "timestamp": ""},
)
fig.update_layout(legend_title_text="Fuel Type")
fig.show()""",
        ),
        (
            "md",
            """
## 2. Generation Share (Pie Chart)
""",
        ),
        (
            "code",
            """\
totals = df_gen.groupby("fuel")["value"].sum().reset_index()
totals = totals[totals["value"] > 0]

fig = px.pie(
    totals, names="fuel", values="value",
    title="Generation Share — France, 1-8 Jun 2024",
)
fig.show()""",
        ),
        (
            "md",
            """
## 3. Solar vs Wind — Daily Patterns
""",
        ),
        (
            "code",
            """\
start = "2024-06-03"
end = "2024-06-06"

df_solar = client.generation.actual(start, end, country="FR", psr_type="B16")
df_solar["fuel"] = "Solar"

df_wind = client.generation.actual(start, end, country="FR", psr_type="B19")
df_wind["fuel"] = "Wind Onshore"

df_ren = pd.concat([df_solar, df_wind], ignore_index=True)

fig = px.line(
    df_ren, x="timestamp", y="value", color="fuel",
    title="Solar vs Wind Onshore — France",
    labels={"value": "Generation (MW)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Wind & Solar Forecast vs Actual
""",
        ),
        (
            "code",
            """\
df_forecast = client.generation.forecast(start, end, country="FR")
df_forecast["fuel"] = df_forecast["psr_type"].map(PSR_TYPES)

# Compare solar
df_solar_fc = df_forecast[df_forecast["psr_type"] == "B16"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_solar["timestamp"], y=df_solar["value"],
    name="Actual", line=dict(color="#FFA15A"),
))
fig.add_trace(go.Scatter(
    x=df_solar_fc["timestamp"], y=df_solar_fc["value"],
    name="Forecast", line=dict(color="#FFA15A", dash="dash"),
))
fig.update_layout(
    title="Solar Generation — Forecast vs Actual (France)",
    yaxis_title="Generation (MW)",
    xaxis_title="",
)
fig.show()""",
        ),
        (
            "md",
            """
## 5. Installed Capacity by Type
""",
        ),
        (
            "code",
            """\
start = "2024-01-01"
end = "2024-12-31"

df_cap = client.generation.installed_capacity(start, end, country="FR")
df_cap["fuel"] = df_cap["psr_type"].map(PSR_TYPES)

latest = df_cap.sort_values("timestamp").groupby("fuel").last().reset_index()
latest = latest[latest["value"] > 0].sort_values("value", ascending=True)

fig = px.bar(
    latest, x="value", y="fuel", orientation="h",
    title="Installed Generation Capacity — France, 2024",
    labels={"value": "Capacity (MW)", "fuel": ""},
)
fig.show()""",
        ),
    ]
)


# ── Generation per Plant ─────────────────────────────────────────────────

generation_per_plant_nb = nb(
    [
        (
            "md",
            """
# Generation per Plant — ENTSO-E Examples

Querying actual generation at individual generator level (document type A73).

**Note:** Only generation units with ≥100 MW installed capacity are required to report.
""",
        ),
        ("code", SETUP_WITH_MAPPINGS),
        (
            "md",
            """
## 1. All Generation Units — France (1 day)
""",
        ),
        (
            "code",
            """\
start = "2024-06-03"
end = "2024-06-04"

df = client.generation.per_plant(start, end, country="FR")
df["fuel"] = df["psr_type"].map(PSR_TYPES)
df.head(10)""",
        ),
        (
            "code",
            """\
print(f"Columns: {df.columns.tolist()}")
print(f"Unique units: {df['unit_name'].nunique()}")
print(f"Fuel types: {df['fuel'].nunique()}")
print(f"Time range: {df['timestamp'].min()} → {df['timestamp'].max()}")""",
        ),
        (
            "md",
            """
## 2. Top 10 Generators by Output
""",
        ),
        (
            "code",
            """\
totals = (
    df.groupby(["unit_name", "fuel"])["value"]
    .sum()
    .reset_index()
    .sort_values("value", ascending=False)
    .head(10)
)

fig = px.bar(
    totals, x="value", y="unit_name", color="fuel",
    orientation="h",
    title="Top 10 Generation Units by Total Output — France",
    labels={"value": "Total Generation (MWh)", "unit_name": ""},
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
fig.show()""",
        ),
        (
            "md",
            """
## 3. Nuclear Plants — Hourly Profiles
""",
        ),
        (
            "code",
            """\
df_nuclear = df[df["psr_type"] == "B14"].copy()

# Pick top 5 nuclear units by total output
top_nuclear = (
    df_nuclear.groupby("unit_name")["value"].sum()
    .nlargest(5).index
)
df_top = df_nuclear[df_nuclear["unit_name"].isin(top_nuclear)]

fig = px.line(
    df_top, x="timestamp", y="value", color="unit_name",
    title="Top 5 Nuclear Units — Hourly Generation (France)",
    labels={"value": "Generation (MW)", "timestamp": "", "unit_name": "Unit"},
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Gas Plants — France
""",
        ),
        (
            "code",
            """\
df_gas = df[df["psr_type"] == "B04"].copy()

fig = px.line(
    df_gas, x="timestamp", y="value", color="unit_name",
    title="Gas Plants — Individual Output (France)",
    labels={"value": "Generation (MW)", "timestamp": "", "unit_name": "Plant"},
)
fig.show()""",
        ),
        (
            "md",
            """
## 5. Unit Count by Fuel Type
""",
        ),
        (
            "code",
            """\
unit_counts = (
    df.groupby("fuel")["unit_name"]
    .nunique()
    .reset_index(name="units")
    .sort_values("units", ascending=True)
)

fig = px.bar(
    unit_counts, x="units", y="fuel", orientation="h",
    title="Number of Reporting Units by Fuel Type — France",
    labels={"units": "Generation Units (≥100 MW)", "fuel": ""},
)
fig.show()""",
        ),
    ]
)


# ── Transmission ─────────────────────────────────────────────────────────

transmission_nb = nb(
    [
        (
            "md",
            """
# Transmission Data — ENTSO-E Examples

Querying cross-border flows and scheduled exchanges between countries.
""",
        ),
        ("code", SETUP),
        (
            "md",
            """
## 1. Physical Cross-Border Flows — France → Germany
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_fr_de = client.transmission.crossborder_flows(
    start, end, country_from="FR", country_to="DE_LU"
)
df_fr_de.head()""",
        ),
        (
            "code",
            """\
fig = px.line(
    df_fr_de, x="timestamp", y="value",
    title="Physical Flows — France → Germany",
    labels={"value": "Flow (MW)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 2. Bidirectional Flows — France ↔ Germany
""",
        ),
        (
            "code",
            """\
df_de_fr = client.transmission.crossborder_flows(
    start, end, country_from="DE_LU", country_to="FR"
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_fr_de["timestamp"], y=df_fr_de["value"],
    name="FR → DE", fill="tozeroy", line=dict(color="#636EFA"),
))
fig.add_trace(go.Scatter(
    x=df_de_fr["timestamp"], y=-df_de_fr["value"],
    name="DE → FR", fill="tozeroy", line=dict(color="#EF553B"),
))
fig.update_layout(
    title="Bidirectional Flows — France ↔ Germany",
    yaxis_title="Flow (MW)  [positive = FR→DE]",
    xaxis_title="",
)
fig.show()""",
        ),
        (
            "md",
            """
## 3. Scheduled Exchanges — France → Spain
""",
        ),
        (
            "code",
            """\
df_sched = client.transmission.scheduled_exchanges(
    start, end, country_from="FR", country_to="ES"
)

fig = px.line(
    df_sched, x="timestamp", y="value",
    title="Scheduled Exchanges — France → Spain",
    labels={"value": "Scheduled (MW)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Multi-Border Comparison from France
""",
        ),
        (
            "code",
            """\
start = "2024-06-03"
end = "2024-06-04"

borders = {"DE_LU": "→ Germany", "ES": "→ Spain", "GB": "→ Great Britain", "IT_NORTH": "→ Italy (North)"}
frames = []
for code, label in borders.items():
    df = client.transmission.crossborder_flows(
        start, end, country_from="FR", country_to=code
    )
    df["border"] = f"FR {label}"
    frames.append(df)

df_borders = pd.concat(frames, ignore_index=True)

fig = px.line(
    df_borders, x="timestamp", y="value", color="border",
    title="Cross-Border Flows from France — 3 Jun 2024",
    labels={"value": "Flow (MW)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 5. Net Transfer Capacity — France → Spain
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_ntc = client.transmission.net_transfer_capacity(
    start, end, country_from="FR", country_to="ES"
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_ntc["timestamp"], y=df_ntc["value"],
    name="NTC", line=dict(color="#AB63FA"),
))
df_fr_es = client.transmission.crossborder_flows(
    start, end, country_from="FR", country_to="ES"
)
fig.add_trace(go.Scatter(
    x=df_fr_es["timestamp"], y=df_fr_es["value"],
    name="Actual Flow", line=dict(color="#636EFA"),
))
fig.update_layout(
    title="Net Transfer Capacity vs Actual Flow — FR → ES",
    yaxis_title="MW",
    xaxis_title="",
)
fig.show()""",
        ),
    ]
)


# ── Balancing ────────────────────────────────────────────────────────────

balancing_nb = nb(
    [
        (
            "md",
            """
# Balancing Data — ENTSO-E Examples

Querying imbalance prices and volumes.
""",
        ),
        ("code", SETUP),
        (
            "md",
            """
## 1. Imbalance Prices — France (1 week)
""",
        ),
        (
            "code",
            """\
start = "2024-06-01"
end = "2024-06-08"

df_prices = client.balancing.imbalance_prices(start, end, country="FR")
df_prices.head()""",
        ),
        (
            "code",
            """\
fig = px.line(
    df_prices, x="timestamp", y="value",
    title="Imbalance Prices — France",
    labels={"value": "Price (EUR/MWh)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 2. Imbalance Prices — Multi-Country
""",
        ),
        (
            "code",
            """\
countries = {"FR": "France", "NL": "Netherlands", "BE": "Belgium"}
frames = []
for code, name in countries.items():
    df = client.balancing.imbalance_prices(start, end, country=code)
    df["country"] = name
    frames.append(df)

df_multi = pd.concat(frames, ignore_index=True)

fig = px.line(
    df_multi, x="timestamp", y="value", color="country",
    title="Imbalance Prices — Multi-Country Comparison",
    labels={"value": "Price (EUR/MWh)", "timestamp": ""},
)
fig.show()""",
        ),
        (
            "md",
            """
## 3. Price Distribution — Histogram
""",
        ),
        (
            "code",
            """\
fig = px.histogram(
    df_multi, x="value", color="country", barmode="overlay",
    nbins=50, opacity=0.7,
    title="Imbalance Price Distribution",
    labels={"value": "Price (EUR/MWh)"},
)
fig.show()""",
        ),
        (
            "md",
            """
## 4. Imbalance Prices vs Day-Ahead Prices
""",
        ),
        (
            "code",
            """\
df_da = client.prices.day_ahead(start, end, country="FR")
df_imb = client.balancing.imbalance_prices(start, end, country="FR")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_da["timestamp"], y=df_da["value"],
    name="Day-Ahead", line=dict(color="#636EFA"),
))
fig.add_trace(go.Scatter(
    x=df_imb["timestamp"], y=df_imb["value"],
    name="Imbalance", line=dict(color="#EF553B"),
))
fig.update_layout(
    title="Day-Ahead vs Imbalance Prices — France",
    yaxis_title="Price (EUR/MWh)",
    xaxis_title="",
)
fig.show()""",
        ),
    ]
)


# ── Write all notebooks ─────────────────────────────────────────────────

NOTEBOOKS = {
    "examples/load.ipynb": load_nb,
    "examples/prices.ipynb": prices_nb,
    "examples/generation.ipynb": generation_nb,
    "examples/generation_per_plant.ipynb": generation_per_plant_nb,
    "examples/transmission.ipynb": transmission_nb,
    "examples/balancing.ipynb": balancing_nb,
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate example notebooks.")
    parser.add_argument(
        "--execute", action="store_true",
        help="Execute notebooks and save with outputs (requires ENTSOE_API_KEY).",
    )
    args = parser.parse_args()

    for path, notebook in NOTEBOOKS.items():
        nbf.write(notebook, path)
        print(f"  {path} ({len(notebook.cells)} cells)")

    if args.execute:
        from nbclient import NotebookClient

        print("\nExecuting notebooks...")
        for path in NOTEBOOKS:
            print(f"  Executing {path}...", end=" ", flush=True)
            nb = nbf.read(path, as_version=4)
            client = NotebookClient(nb, timeout=120, kernel_name="python3")
            client.execute()
            nbf.write(nb, path)
            print("OK")

    print(f"\nGenerated {len(NOTEBOOKS)} notebooks.")
