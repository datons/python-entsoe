"""Tests for the transmission namespace."""

import pandas as pd
import pytest

from entsoe import Client


class TestCrossborderFlows:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="FR", country_to="DE_LU"
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_has_required_columns(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="FR", country_to="DE_LU"
        )
        assert "timestamp" in df.columns
        assert "value" in df.columns

    def test_reverse_direction(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="DE_LU", country_to="FR"
        )
        assert len(df) > 0

    def test_france_spain(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.crossborder_flows(
            start, end, country_from="FR", country_to="ES"
        )
        assert len(df) > 0


class TestScheduledExchanges:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.scheduled_exchanges(
            start, end, country_from="FR", country_to="ES"
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestNetTransferCapacity:
    def test_returns_dataframe(self, client: Client, short_range):
        start, end = short_range
        df = client.transmission.net_transfer_capacity(
            start, end, country_from="FR", country_to="ES"
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
