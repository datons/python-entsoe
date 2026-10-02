"""Unit tests for area, PSR, and border mappings."""

import pytest
from entsoe._mappings import (
    lookup_area,
    lookup_psr,
    parse_borders,
    AREA_CODES,
    COUNTRY_NAMES,
    PSR_TYPES,
    PSR_CODES,
    NEIGHBOURS,
    BORDER_GROUPS,
)
from entsoe.exceptions import InvalidParameterError


class TestLookupArea:
    def test_iso_code(self):
        assert lookup_area("FR") == "10YFR-RTE------C"

    def test_country_name(self):
        assert lookup_area("France") == "10YFR-RTE------C"

    def test_eic_code(self):
        assert lookup_area("10YFR-RTE------C") == "10YFR-RTE------C"

    def test_unknown_raises(self):
        with pytest.raises(InvalidParameterError, match="Unknown country"):
            lookup_area("ZZ_NOPE")


class TestLookupPsr:
    def test_code(self):
        assert lookup_psr("B16") == "B16"

    def test_shorthand(self):
        assert lookup_psr("solar") == "B16"

    def test_full_name(self):
        assert lookup_psr("Solar") == "B16"

    def test_unknown_raises(self):
        with pytest.raises(InvalidParameterError, match="Unknown PSR type"):
            lookup_psr("unobtanium")


class TestParseBorders:
    def test_single_pair(self):
        pairs = parse_borders("ES-FR")
        assert ("ES", "FR") in pairs

    def test_wildcard(self):
        pairs = parse_borders("FR-*")
        assert len(pairs) == len(NEIGHBOURS["FR"])

    def test_named_group(self):
        pairs = parse_borders("iberian")
        assert len(pairs) == len(BORDER_GROUPS["iberian"])

    def test_deduplication(self):
        pairs = parse_borders(["ES-FR", "ES-FR"])
        assert pairs.count(("ES", "FR")) == 1

    def test_comma_separated(self):
        pairs = parse_borders("ES-FR,ES-PT")
        assert ("ES", "FR") in pairs
        assert ("ES", "PT") in pairs


class TestNeighboursSymmetry:
    def test_symmetric(self):
        """If A has B as neighbour, B must have A as neighbour."""
        for country, neighbours in NEIGHBOURS.items():
            for neighbour in neighbours:
                assert neighbour in NEIGHBOURS, (
                    f"{neighbour} (neighbour of {country}) missing from NEIGHBOURS"
                )
                assert country in NEIGHBOURS[neighbour], (
                    f"{country} → {neighbour} but not {neighbour} → {country}"
                )
