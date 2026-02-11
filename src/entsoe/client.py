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

        client = Client()  # reads ENTSOE_API_KEY from env

        # Simple — just pass date strings (default tz: Europe/Brussels)
        df = client.load.actual("2024-01-01", "2024-01-07", country="FR")
        df = client.prices.day_ahead("2024-01-01", "2024-01-07", country="FR")

        # pd.Timestamp still works — its timezone takes priority
        import pandas as pd
        start = pd.Timestamp("2024-01-01", tz="Europe/Paris")
        df = client.generation.actual(start, "2024-01-07", country="FR")

        # Override default timezone
        client = Client(tz="UTC")

    Namespaces:
        load: Actual load and load forecast.
        prices: Day-ahead market prices.
        generation: Actual generation, forecasts, installed capacity.
        transmission: Cross-border flows and scheduled exchanges.
        balancing: Imbalance prices and volumes.
    """

    DEFAULT_TZ = "Europe/Brussels"

    def __init__(
        self,
        api_key: str | None = None,
        tz: str = DEFAULT_TZ,
    ) -> None:
        """Initialize the client.

        Args:
            api_key: ENTSO-E API key. If not provided, reads from
                     the ``ENTSOE_API_KEY`` environment variable.
            tz: Default timezone for string timestamps. Defaults to
                ``Europe/Brussels`` (CET — the ENTSO-E standard).

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

        self.load = LoadNamespace(http, tz=tz)
        self.prices = PricesNamespace(http, tz=tz)
        self.generation = GenerationNamespace(http, tz=tz)
        self.transmission = TransmissionNamespace(http, tz=tz)
        self.balancing = BalancingNamespace(http, tz=tz)
