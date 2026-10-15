"""Offline tests for CLI period shorthands."""

from datetime import date

from entsoe.cli._resolve import _expand_period

TODAY = date(2026, 10, 15)


def test_today_is_one_full_day():
    assert _expand_period("today", TODAY) == (date(2026, 10, 15), date(2026, 10, 16))


def test_yesterday_is_one_full_day():
    assert _expand_period("yesterday", TODAY) == (date(2026, 10, 14), date(2026, 10, 15))
