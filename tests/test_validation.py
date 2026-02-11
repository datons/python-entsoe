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

    def test_default_tz(self):
        c = Client(api_key="dummy")
        assert c.load._tz == "Europe/Brussels"

    def test_custom_tz(self):
        c = Client(api_key="dummy", tz="UTC")
        assert c.load._tz == "UTC"
        assert c.prices._tz == "UTC"
        assert c.generation._tz == "UTC"
        assert c.transmission._tz == "UTC"
        assert c.balancing._tz == "UTC"


class TestStringTimestampCoercion:
    """Test that plain strings are coerced to tz-aware Timestamps."""

    def test_resolve_ts_from_string(self, client):
        ts = client.load._resolve_ts("2024-06-01")
        assert isinstance(ts, pd.Timestamp)
        assert str(ts.tz) == "Europe/Brussels"
        assert ts == pd.Timestamp("2024-06-01", tz="Europe/Brussels")

    def test_resolve_ts_passthrough(self, client):
        original = pd.Timestamp("2024-06-01", tz="Asia/Tokyo")
        ts = client.load._resolve_ts(original)
        assert ts is original

    def test_resolve_ts_naive_passthrough(self, client):
        """Naive pd.Timestamp passes through _resolve_ts but fails in _validate_timestamps."""
        naive = pd.Timestamp("2024-06-01")
        ts = client.load._resolve_ts(naive)
        assert ts.tzinfo is None  # not coerced — will fail downstream

    def test_string_uses_client_tz(self):
        c = Client(api_key="dummy", tz="US/Eastern")
        ts = c.load._resolve_ts("2024-06-01")
        assert str(ts.tz) == "US/Eastern"

    def test_mixed_string_and_timestamp(self, client):
        """String start + pd.Timestamp end both resolve correctly."""
        start = client.load._resolve_ts("2024-06-01")
        end_ts = pd.Timestamp("2024-06-08", tz="Europe/Paris")
        end = client.load._resolve_ts(end_ts)
        assert str(start.tz) == "Europe/Brussels"
        assert str(end.tz) == "Europe/Paris"
        assert start < end
