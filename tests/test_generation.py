"""Tests for the generation namespace."""

import pandas as pd
import pytest

from entsoe import Client


class TestGenerationActual:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.actual(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_psr_type(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.actual(start, end, country="FR")
        assert "psr_type" in df.columns

    def test_filter_by_solar(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.actual(start, end, country="FR", psr_type="B16")
        assert len(df) > 0
        assert (df["psr_type"] == "B16").all()

    def test_filter_by_wind_onshore(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.actual(start, end, country="FR", psr_type="B19")
        assert len(df) > 0
        assert (df["psr_type"] == "B19").all()


class TestGenerationForecast:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.forecast(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_psr_type(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.forecast(start, end, country="FR")
        assert "psr_type" in df.columns


class TestInstalledCapacity:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.installed_capacity(start, end, country="FR")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_psr_type(self, client: Client, short_range):
        start, end = short_range
        df = client.generation.installed_capacity(start, end, country="FR")
        assert "psr_type" in df.columns
