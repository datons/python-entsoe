"""Main Client class for the ENTSO-E Transparency Platform API."""

from __future__ import annotations

import os
from pathlib import Path

from ._http import HttpClient
from .cache import CacheConfig, CacheStore
from .namespaces import (
    BalancingNamespace,
    GenerationNamespace,
    LoadNamespace,
    PricesNamespace,
    TransmissionNamespace,
)


class ENTSOEClient:
    """ENTSO-E Transparency Platform API client.

    Provides typed, namespace-organized access to European electricity market data.

    Usage::

        from entsoe import ENTSOEClient

        client = ENTSOEClient()  # reads ENTSOE_API_KEY from env

        # Simple — just pass date strings (default tz: Europe/Brussels)
        df = client.load.actual("2024-01-01", "2024-01-07", country="FR")
        df = client.prices.day_ahead("2024-01-01", "2024-01-07", country="FR")

        # pd.Timestamp still works — its timezone takes priority
        import pandas as pd
        start = pd.Timestamp("2024-01-01", tz="Europe/Paris")
        df = client.generation.actual(start, "2024-01-07", country="FR")

        # Override default timezone
        client = ENTSOEClient(tz="UTC")

        # Disable cache
        client = ENTSOEClient(cache=False)

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
        *,
        cache: bool = True,
        cache_dir: str | Path | None = None,
        cache_recent_ttl: int = 48,
    ) -> None:
        """Initialize the client.

        Args:
            api_key: ENTSO-E API key. If not provided, reads from
                     the ``ENTSOE_API_KEY`` environment variable.
            tz: Default timezone for string timestamps. Defaults to
                ``Europe/Brussels`` (CET — the ENTSO-E standard).
            cache: Whether to enable local parquet caching. Defaults to True.
            cache_dir: Custom cache directory. Defaults to ``~/.cache/entsoe/``.
            cache_recent_ttl: Hours before data is considered final (default 48).

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

        # Set up cache
        cache_config = CacheConfig(
            enabled=cache,
            recent_ttl_hours=cache_recent_ttl,
        )
        if cache_dir is not None:
            cache_config.cache_dir = Path(cache_dir)

        cache_store = CacheStore(cache_config) if cache else None

        self.load = LoadNamespace(http, tz=tz, cache=cache_store)
        self.prices = PricesNamespace(http, tz=tz, cache=cache_store)
        self.generation = GenerationNamespace(http, tz=tz, cache=cache_store)
        self.transmission = TransmissionNamespace(http, tz=tz, cache=cache_store)
        self.balancing = BalancingNamespace(http, tz=tz, cache=cache_store)

        # Expose for CLI cache commands
        self._cache = cache_store


# Backward-compatible alias
Client = ENTSOEClient
