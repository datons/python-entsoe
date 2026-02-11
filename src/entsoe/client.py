"""Main Client class for the ENTSO-E Transparency Platform API."""

from __future__ import annotations

import os

from ._http import HttpClient
from .namespaces import (
    BalancingNamespace,
    GenerationNamespace,
    LoadNamespace,
    PricesNamespace,
    TransmissionNamespace,
)


class Client:
    """ENTSO-E Transparency Platform API client.

    Provides typed, namespace-organized access to European electricity market data.

    Usage::

        from entsoe import Client
        import pandas as pd

        client = Client()  # reads ENTSOE_API_KEY from env

        start = pd.Timestamp("2024-01-01", tz="Europe/Paris")
        end = pd.Timestamp("2024-01-07", tz="Europe/Paris")

        df = client.load.actual(start, end, country="FR")
        df = client.prices.day_ahead(start, end, country="FR")
        df = client.generation.actual(start, end, country="FR")

    Namespaces:
        load: Actual load and load forecast.
        prices: Day-ahead market prices.
        generation: Actual generation, forecasts, installed capacity.
        transmission: Cross-border flows and scheduled exchanges.
        balancing: Imbalance prices and volumes.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the client.

        Args:
            api_key: ENTSO-E API key. If not provided, reads from
                     the ``ENTSOE_API_KEY`` environment variable.

        Raises:
            ValueError: If no API key is found.
        """
        resolved_key = api_key or os.environ.get("ENTSOE_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API key required. Pass api_key= or set the ENTSOE_API_KEY "
                "environment variable."
            )

        http = HttpClient(api_key=resolved_key)

        self.load = LoadNamespace(http)
        self.prices = PricesNamespace(http)
        self.generation = GenerationNamespace(http)
        self.transmission = TransmissionNamespace(http)
        self.balancing = BalancingNamespace(http)
