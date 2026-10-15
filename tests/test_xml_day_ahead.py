"""Offline tests for day-ahead parsing: auction selection, A03 gaps, duplicates."""

import pandas as pd
import pytest

from entsoe._xml import parse_timeseries
from entsoe.namespaces.prices import PricesNamespace

NS = "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"


def _series(mrid, prices, *, contract="A01", sequence=None, start="2026-10-12T22:00Z",
            end="2026-10-12T23:00Z"):
    seq = (
        "<classificationSequence_AttributeInstanceComponent.position>"
        f"{sequence}</classificationSequence_AttributeInstanceComponent.position>"
        if sequence is not None else ""
    )
    points = "".join(
        f"<Point><position>{pos}</position><price.amount>{val}</price.amount></Point>"
        for pos, val in prices.items()
    )
    return (
        f"<TimeSeries><mRID>{mrid}</mRID><auction.type>A01</auction.type>"
        f"<contract_MarketAgreement.type>{contract}</contract_MarketAgreement.type>"
        "<currency_Unit.name>EUR</currency_Unit.name>"
        f"<price_Measure_Unit.name>MWH</price_Measure_Unit.name>{seq}"
        "<curveType>A03</curveType>"
        f"<Period><timeInterval><start>{start}</start><end>{end}</end></timeInterval>"
        f"<resolution>PT15M</resolution>{points}</Period></TimeSeries>"
    )


def _doc(*series):
    return f'<Publication_MarketDocument xmlns="{NS}">{"".join(series)}</Publication_MarketDocument>'


class _FakeHttp:
    def __init__(self, xml):
        self.xml = xml

    def query(self, params, start, end):
        return self.xml


def _day_ahead(xml, **kwargs):
    ns = PricesNamespace(_FakeHttp(xml), cache=None)
    return ns.day_ahead("2026-10-13", "2026-10-14", country="DE_LU", **kwargs)


# Shaped like the live DE_LU response: EXAA (sequence 2) listed before SDAC (1).
DE_LU = _doc(
    _series(1, {1: 189.61, 2: 180.0, 3: 175.0, 4: 170.0}, sequence=2),
    _series(2, {1: 191.89, 2: 185.0, 3: 178.0, 4: 172.0}, sequence=1),
)

# Shaped like the live ES response: unsequenced SDAC plus IDA intraday auctions.
ES = _doc(
    _series(1, {1: 220.0, 2: 210.0, 3: 205.0, 4: 200.0}),
    _series(2, {1: 220.49, 2: 211.0, 3: 206.0, 4: 201.0}, contract="A07", sequence=1),
    _series(3, {1: 219.0, 2: 209.0, 3: 204.0, 4: 199.0}, contract="A07", sequence=2),
)


def test_de_lu_defaults_to_sdac():
    df = _day_ahead(DE_LU)
    assert df["timestamp"].is_unique
    assert df["value"].tolist() == [191.89, 185.0, 178.0, 172.0]


def test_de_lu_sequence_2_is_exaa():
    df = _day_ahead(DE_LU, sequence=2)
    assert df["value"].tolist() == [189.61, 180.0, 175.0, 170.0]


def test_spain_drops_intraday_auctions():
    df = _day_ahead(ES)
    assert df["value"].tolist() == [220.0, 210.0, 205.0, 200.0]


def test_a03_omitted_point_repeats_previous_value():
    # Position 3 omitted: it carries position 2's value. Trailing slot 4 too.
    df = parse_timeseries(_doc(_series(1, {1: 10.0, 2: 20.0})))
    assert len(df) == 4
    assert df["value"].tolist() == [10.0, 20.0, 20.0, 20.0]
    assert df["timestamp"].iloc[-1] == pd.Timestamp("2026-10-12T22:45Z")


def test_verbatim_duplicate_series_dropped():
    s = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
    df = parse_timeseries(_doc(_series(1, s), _series(1, s)))
    assert len(df) == 4


def test_unknown_sequence_raises_no_data():
    from entsoe.exceptions import NoDataError

    with pytest.raises(NoDataError):
        _day_ahead(ES, sequence=2)
