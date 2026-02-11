"""Shared fixtures for ENTSO-E integration tests."""

import os

import pytest

from entsoe import Client


def _load_env():
    """Load .env file if present."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v)


_load_env()


@pytest.fixture(scope="session")
def client() -> Client:
    """Shared client instance for all tests."""
    return Client()


@pytest.fixture(scope="session")
def short_range() -> tuple[str, str]:
    """A 1-day range to minimize API calls."""
    return ("2024-06-03", "2024-06-04")
