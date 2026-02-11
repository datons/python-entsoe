"""Tests for input validation (no API calls)."""

import pandas as pd
import pytest

from entsoe import Client, InvalidParameterError


@pytest.fixture
def client():
    """Client for validation tests (API key doesn't matter for these)."""
    return Client(api_key="dummy")


class TestTimestampValidation:
    def test_naive_start_raises(self, client):
        start = pd.Timestamp("2024-01-01")  # naive
        end = pd.Timestamp("2024-01-02", tz="UTC")
        with pytest.raises(InvalidParameterError, match="timezone-aware"):
            client.load.actual(start, end, country="FR")

    def test_naive_end_raises(self, client):
        start = pd.Timestamp("2024-01-01", tz="UTC")
        end = pd.Timestamp("2024-01-02")  # naive
        with pytest.raises(InvalidParameterError, match="timezone-aware"):
            client.load.actual(start, end, country="FR")

    def test_start_after_end_raises(self, client):
        start = pd.Timestamp("2024-01-02", tz="UTC")
        end = pd.Timestamp("2024-01-01", tz="UTC")
        with pytest.raises(InvalidParameterError, match="before"):
            client.load.actual(start, end, country="FR")


class TestCountryValidation:
    def test_invalid_country_raises(self, client):
        start = pd.Timestamp("2024-01-01", tz="UTC")
        end = pd.Timestamp("2024-01-02", tz="UTC")
        with pytest.raises(InvalidParameterError, match="Unknown country"):
            client.load.actual(start, end, country="XX")


class TestClientInit:
    def test_no_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("ENTSOE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key"):
            Client()
