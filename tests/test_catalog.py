"""Unit tests for the data catalog module."""

import pytest
from entsoe.catalog import CATEGORIES, get_category, summary, Category, Endpoint


class TestCategories:
    def test_has_five_categories(self):
        assert len(CATEGORIES) == 5

    def test_all_category_names(self):
        expected = {"prices", "load", "generation", "transmission", "balancing"}
        assert set(CATEGORIES.keys()) == expected

    def test_get_category_by_name(self):
        cat = get_category("prices")
        assert cat.name == "Prices"

    def test_get_category_case_insensitive(self):
        cat = get_category("PRICES")
        assert cat.name == "Prices"

    def test_get_category_unknown_raises(self):
        with pytest.raises(KeyError, match="Unknown category"):
            get_category("unknown")

    def test_each_category_has_endpoints(self):
        for key, cat in CATEGORIES.items():
            assert len(cat.endpoints) > 0, f"{key} has no endpoints"

    def test_endpoint_required_fields(self):
        for key, cat in CATEGORIES.items():
            for ep in cat.endpoints:
                assert ep.name, f"{key}: endpoint missing name"
                assert ep.cli, f"{key}/{ep.name}: missing cli"
                assert ep.method, f"{key}/{ep.name}: missing method"
                assert ep.units, f"{key}/{ep.name}: missing units"
                assert ep.resolution, f"{key}/{ep.name}: missing resolution"

    def test_summary_returns_nonempty_string(self):
        s = summary()
        assert isinstance(s, str)
        assert len(s) > 100
        assert "Prices" in s
