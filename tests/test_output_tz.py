"""Offline tests for configurable result timezones."""

from zoneinfo import ZoneInfo

import pandas as pd
import pytest
from typer.testing import CliRunner

from entsoe import Client
from entsoe._mappings import AREA_CODES, AREA_TZ
from entsoe.cli.app import app
from entsoe.exceptions import InvalidParameterError


POINTS = "".join(f"<Point><position>{i}</position><price.amount>50</price.amount></Point>" for i in range(1, 25))
XML = f'''<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3">
<TimeSeries><mRID>1</mRID><auction.type>A01</auction.type><contract_MarketAgreement.type>A01</contract_MarketAgreement.type>
<currency_Unit.name>EUR</currency_Unit.name><price_Measure_Unit.name>MWH</price_Measure_Unit.name>
<Period><timeInterval><start>2024-06-02T22:00Z</start><end>2024-06-03T22:00Z</end></timeInterval>
<resolution>PT60M</resolution>{POINTS}</Period>
</TimeSeries></Publication_MarketDocument>'''


@pytest.fixture
def fake_http(monkeypatch):
    calls = []

    def query(self, params, start, end):
        calls.append(params)
        return XML

    monkeypatch.setattr("entsoe._http.HttpClient.query", query)
    return calls


def prices(client, country="DE_LU", **kwargs):
    return client.prices.day_ahead("2024-06-03", "2024-06-04", country=country, **kwargs)


def test_area_timezone_mapping_is_complete_and_valid():
    assert set(AREA_TZ) == set(AREA_CODES)
    for name in AREA_TZ.values():
        ZoneInfo(name)


def test_default_utc_and_local_summer_midnight(fake_http):
    assert str(prices(Client(api_key="test", cache=False))["timestamp"].dt.tz) == "UTC"
    local = prices(Client(api_key="test", cache=False, output_tz="local"))
    assert str(local["timestamp"].dt.tz) == "Europe/Berlin"
    assert local["timestamp"].iloc[0].isoformat() == "2024-06-03T00:00:00+02:00"


def test_fixed_zone_and_per_call_override(fake_http):
    client = Client(api_key="test", cache=False, output_tz="Europe/Lisbon")
    assert str(prices(client)["timestamp"].dt.tz) == "Europe/Lisbon"
    assert str(prices(client, output_tz="Europe/Madrid")["timestamp"].dt.tz) == "Europe/Madrid"


def test_local_multi_zone_compatibility(fake_http):
    client = Client(api_key="test", cache=False, output_tz="local")
    assert str(prices(client, country=["FR", "ES"])["timestamp"].dt.tz) == "Europe/Paris"
    with pytest.raises(InvalidParameterError, match="Europe/London.*Europe/Paris.*UTC"):
        prices(client, country=["FR", "GB"])


def test_cache_hit_retains_requested_zone_and_utc_storage(fake_http, tmp_path):
    client = Client(api_key="test", cache_dir=tmp_path, output_tz="local")
    first = prices(client)
    count = len(fake_http)
    second = prices(client)
    assert len(fake_http) == count
    assert str(second["timestamp"].dt.tz) == "Europe/Berlin"
    assert second["timestamp"].tolist() == first["timestamp"].tolist()
    cached = client._cache.read("prices", "day_ahead", "DE_LU", pd.Timestamp("2024-06-03", tz="UTC"), pd.Timestamp("2024-06-04", tz="UTC"))
    assert str(cached.index.tz) == "UTC"


def test_generation_list_filter_and_transmission_use_boundary_conversion(fake_http, monkeypatch):
    client = Client(api_key="test", cache=False, output_tz="local")
    generation = client.generation.actual("2024-06-03", "2024-06-04", country="DE_LU", psr_type=["solar"])
    assert str(generation["timestamp"].dt.tz) == "Europe/Berlin"

    utc_frame = pd.DataFrame({"timestamp": [pd.Timestamp("2024-06-02T22:00Z")], "value": [1.0]})
    monkeypatch.setattr(client.transmission, "_query_single_border", lambda *args: utc_frame)
    border = client.transmission.crossborder_flows("2024-06-03", "2024-06-04", country_from="FR", country_to="GB")
    assert str(border["timestamp"].dt.tz) == "Europe/London"
    assert str(utc_frame["timestamp"].dt.tz) == "UTC"


@pytest.mark.parametrize("value", ["Mars/Olympus", "", 42, "LOCAL"])
def test_invalid_output_timezone_raises(value):
    with pytest.raises(InvalidParameterError):
        Client(api_key="test", output_tz=value)


def test_cli_local_and_config_precedence(fake_http, monkeypatch, tmp_path):
    from entsoe.cli import config

    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.toml")
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
    runner = CliRunner()
    assert runner.invoke(app, ["config", "set", "output-tz", "UTC"]).exit_code == 0
    args = ["prices", "day-ahead", "--start", "2024-06-03", "--end", "2024-06-04", "--country", "DE_LU", "--api-key", "test", "--format", "json"]
    utc = runner.invoke(app, args)
    assert utc.exit_code == 0, utc.output
    assert "+00:00" in utc.output
    local = runner.invoke(app, args + ["--tz", "local"])
    assert local.exit_code == 0, local.output
    assert "2024-06-03T00:00:00+02:00" in local.output
