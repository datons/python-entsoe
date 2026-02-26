"""Tests for multi-country / multi-value query support."""

import pandas as pd
import pytest

from entsoe import Client


class TestMultiCountryPrices:
    def test_list_returns_country_column(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country=["FR", "ES"])
        assert "country" in df.columns

    def test_single_string_no_country_column(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country="FR")
        assert "country" not in df.columns

    def test_multi_has_all_countries(self, client: Client, short_range):
        start, end = short_range
        df = client.prices.day_ahead(start, end, country=["FR", "ES", "NL"])
        countries = set(df["country"].unique())
        assert countries == {"France", "Spain", "Netherlands"}

    def test_multi_has_more_rows(self, client: Client, short_range):
        start, end = short_range
        df_single = client.prices.day_ahead(start, end, country="FR")
        df_multi = client.prices.day_ahead(start, end, country=["FR", "ES"])
        assert len(df_multi) > len(df_single)


class TestMultiCountryLoad:
    def test_list_returns_country_column(self, client: Client, short_range):
        start, end = short_range
        df = client.load.actual(start, end, country=["FR", "ES"])
        assert "country" in df.columns
        assert set(df["country"].unique()) == {"France", "Spain"}

    def test_forecast_multi(self, client: Client, short_range):
        start, end = short_range
        df = client.load.forecast(start, end, country=["FR", "DE_LU"])
        assert "country" in df.columns
        assert len(df["country"].unique()) == 2


class TestMultiCountryGeneration:
    def test_actual_multi(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.actual(start, end, country=["FR", "ES"])
        assert "country" in df.columns
        assert set(df["country"].unique()) == {"France", "Spain"}


class TestMultiPsrType:
    def test_list_psr_type(self, client: Client, short_range):
        """Multiple psr_types returns data for each type."""
        start, end = short_range
        df = client.generation.actual(
            start, end, country="FR", psr_type=["solar", "wind_onshore"]
        )
        psr_types = set(df["psr_type"].unique())
        assert "Solar" in psr_types
        assert "Wind Onshore" in psr_types

    def test_single_psr_type_unchanged(self, client: Client, short_range):
        """Single psr_type still works as before."""
        start, end = short_range
        df = client.generation.actual(start, end, country="FR", psr_type="solar")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_multi_country_and_multi_psr(self, client: Client, short_range):
        """Both country and psr_type as lists (cartesian)."""
        start, end = short_range
        df = client.generation.actual(
            start, end,
            country=["FR", "ES"],
            psr_type=["solar", "nuclear"],
        )
        assert "country" in df.columns
        countries = set(df["country"].unique())
        assert "France" in countries
        assert "Spain" in countries

    def test_none_psr_type_returns_all(self, client: Client, short_range):
        """psr_type=None returns all types (backward compat)."""
        start, end = short_range
        df = client.generation.actual(start, end, country="FR")
        assert len(df["psr_type"].unique()) > 1


class TestMultiBorderTransmission:
    def test_crossborder_multi_to(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="FR", country_to=["ES", "DE_LU"]
        )
        assert "border" in df.columns
        borders = set(df["border"].unique())
        assert "France → Spain" in borders
        assert "France → Germany/Luxembourg" in borders

    def test_crossborder_multi_from(self, client: Client, short_range):
        """Multiple country_from — flows into Spain from neighbors."""
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from=["FR", "PT"], country_to="ES"
        )
        assert "border" in df.columns
        borders = set(df["border"].unique())
        assert "France → Spain" in borders
        assert "Portugal → Spain" in borders

    def test_crossborder_single_no_border_column(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="FR", country_to="ES"
        )
        assert "border" not in df.columns


class TestMultiCountryBalancing:
    def test_imbalance_prices_multi(self, client: Client, short_range):
        start, end = short_range
        df = client.balancing.imbalance_prices(start, end, country=["FR", "NL"])
        assert "country" in df.columns
        assert len(df["country"].unique()) == 2
