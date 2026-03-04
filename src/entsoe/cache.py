"""Local parquet cache for ENTSO-E time-series data.

Caches query results as parquet files, fetching only missing date ranges
on subsequent requests. Historical electricity data is immutable once
published (~48h), so caching is safe and enabled by default.

Storage layout::

    {cache_dir}/
    ├── prices/day_ahead/{ES,FR,...}/data.parquet
    ├── load/{actual,forecast}/{ES,FR,...}/data.parquet
    ├── generation/{actual,forecast,capacity}/{ES,...}/data.parquet
    ├── generation/per_plant/{ES,...}/data.parquet
    ├── transmission/{crossborder_flows,...}/{ES,...}/data.parquet
    └── balancing/{imbalance_prices,...}/{ES,...}/data.parquet

Each partition stores a single wide-format parquet file: the DatetimeIndex
holds timestamps, and columns are values (e.g. "value", or per-type
columns like "solar", "wind_onshore").

Gap detection works per-column: requesting specific columns checks whether
those columns have data for the requested range, not whether any column does.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger("entsoe")

# Default cache location — respects XDG_CACHE_HOME
_DEFAULT_CACHE_DIR = Path(
    os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
) / "entsoe"

# Data older than this (hours) is considered final and won't be re-fetched
_DEFAULT_RECENT_TTL_HOURS = 48


@dataclass
class CacheConfig:
    """Cache configuration."""

    enabled: bool = True
    cache_dir: Path = field(default_factory=lambda: _DEFAULT_CACHE_DIR)
    recent_ttl_hours: int = _DEFAULT_RECENT_TTL_HOURS

    def __post_init__(self) -> None:
        self.cache_dir = Path(self.cache_dir)


@dataclass(frozen=True)
class DateRange:
    """A contiguous date range [start, end] inclusive."""

    start: pd.Timestamp
    end: pd.Timestamp


class CacheStore:
    """Read, write, and merge parquet files for cached ENTSO-E data."""

    def __init__(self, config: CacheConfig):
        self.config = config

    # -- Path resolution -------------------------------------------------------

    def _parquet_path(self, domain: str, topic: str, partition: str) -> Path:
        """Data file: {cache_dir}/{domain}/{topic}/{partition}/data.parquet"""
        return self.config.cache_dir / domain / topic / partition / "data.parquet"

    def _meta_path(self, domain: str, topic: str, partition: str) -> Path:
        """Metadata file: {cache_dir}/{domain}/{topic}/{partition}/meta.json"""
        return self.config.cache_dir / domain / topic / partition / "meta.json"

    # -- Data Read / Write -----------------------------------------------------

    def read(
        self,
        domain: str,
        topic: str,
        partition: str,
        start: pd.Timestamp,
        end: pd.Timestamp,
        *,
        columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """Read cached data for a date range.

        The file is in wide format (columns = values or pivoted types).
        When *columns* is given, only those columns are returned.
        Returns empty DataFrame on cache miss.
        """
        path = self._parquet_path(domain, topic, partition)
        if not path.exists():
            return pd.DataFrame()

        try:
            df = pd.read_parquet(path)
        except Exception as exc:
            logger.warning("Corrupted cache file %s: %s — removing.", path, exc)
            path.unlink(missing_ok=True)
            return pd.DataFrame()

        if df.empty or not isinstance(df.index, pd.DatetimeIndex):
            return pd.DataFrame()

        df = self._slice(df, start, end)

        if columns:
            existing = [c for c in columns if c in df.columns]
            if not existing:
                return pd.DataFrame()
            df = df[existing]

        return df

    def _slice(
        self, df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
    ) -> pd.DataFrame:
        """Slice a DataFrame by [start, end], handling timezone alignment."""
        if df.index.tz is not None:
            if start.tz is None:
                start = start.tz_localize(df.index.tz)
            if end.tz is None:
                end = end.tz_localize(df.index.tz)

        # When end is a date-level timestamp (midnight), extend to end of day
        if end.hour == 0 and end.minute == 0 and end.second == 0:
            end = end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        return df[start:end]

    def write(
        self,
        domain: str,
        topic: str,
        partition: str,
        df: pd.DataFrame,
    ) -> None:
        """Merge new wide-format data with existing cache and persist.

        *df* should already be in wide format (columns = values,
        index = DatetimeIndex). New data is merged with existing using
        ``combine_first`` so that new values fill in NaN cells without
        overwriting existing data, then overlapping rows use the new values.
        """
        if df.empty:
            return

        path = self._parquet_path(domain, topic, partition)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing and merge
        existing = pd.DataFrame()
        if path.exists():
            try:
                existing = pd.read_parquet(path)
            except Exception:
                logger.warning("Corrupted cache at %s — overwriting.", path)

        if not existing.empty:
            merged = df.combine_first(existing)
            merged = merged.sort_index()
        else:
            merged = df.sort_index()

        _atomic_write_parquet(path, merged)

    def write_meta(
        self,
        domain: str,
        topic: str,
        partition: str,
        meta: dict,
    ) -> None:
        """Write metadata for a partition (extra columns, units, etc.)."""
        meta = {**meta, "cached_at": datetime.now().isoformat()}
        path = self._meta_path(domain, topic, partition)
        _atomic_write_json(path, meta)

    def read_meta(
        self,
        domain: str,
        topic: str,
        partition: str,
    ) -> dict | None:
        """Read cached metadata for a partition."""
        path = self._meta_path(domain, topic, partition)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    # -- Gap detection ---------------------------------------------------------

    def find_gaps(
        self,
        cached_df: pd.DataFrame,
        start: pd.Timestamp,
        end: pd.Timestamp,
        *,
        columns: list[str] | None = None,
        recent_ttl_hours: int | None = None,
    ) -> list[DateRange]:
        """Find date ranges not covered by cached data.

        When *columns* is given, checks coverage for those specific columns.
        A row counts as "covered" only if all requested columns have non-NaN
        values.

        Also marks data within ``recent_ttl_hours`` of now as a gap
        (needs re-fetch since it may have been updated).
        """
        ttl = recent_ttl_hours if recent_ttl_hours is not None else self.config.recent_ttl_hours
        cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=ttl)

        if cached_df.empty:
            return [DateRange(start, end)]

        # If specific columns requested, check only those (per-column gap detection)
        if columns:
            missing = [c for c in columns if c not in cached_df.columns]
            if missing:
                return [DateRange(start, end)]
            mask = cached_df[columns].notna().all(axis=1)
            effective_df = cached_df[mask]
            if effective_df.empty:
                return [DateRange(start, end)]
        else:
            effective_df = cached_df

        # Normalize to UTC for comparison
        idx = effective_df.index
        if idx.tz is None:
            idx = idx.tz_localize("UTC")
        else:
            idx = idx.tz_convert("UTC")

        start_utc = start.tz_localize("UTC") if start.tz is None else start.tz_convert("UTC")
        end_utc = end.tz_localize("UTC") if end.tz is None else end.tz_convert("UTC")

        cached_start = idx.min()
        cached_end = idx.max()

        gaps: list[DateRange] = []

        if start_utc < cached_start:
            gap_end = min(cached_start - pd.Timedelta(hours=1), end_utc)
            if gap_end >= start_utc:
                gaps.append(DateRange(start, _to_tz_aware(gap_end, start)))

        if end_utc > cached_end:
            gap_start = max(cached_end + pd.Timedelta(hours=1), start_utc)
            if gap_start <= end_utc:
                gaps.append(DateRange(_to_tz_aware(gap_start, end), end))

        if cached_end > cutoff and end_utc > cutoff:
            recent_start = max(cutoff, start_utc)
            if recent_start <= end_utc:
                gaps.append(DateRange(_to_tz_aware(recent_start, end), end))

        return _merge_overlapping(gaps)

    # -- Maintenance -----------------------------------------------------------

    def clear(
        self,
        domain: str | None = None,
        topic: str | None = None,
        partition: str | None = None,
    ) -> int:
        """Remove cached files. Returns number of files removed.

        - No args: clear everything
        - domain only: clear all data for that domain
        - domain + topic: clear one topic
        - domain + topic + partition: clear one partition
        """
        count = 0

        if domain and topic and partition:
            target = self.config.cache_dir / domain / topic / partition
        elif domain and topic:
            target = self.config.cache_dir / domain / topic
        elif domain:
            target = self.config.cache_dir / domain
        else:
            target = self.config.cache_dir

        if target.exists():
            count = sum(1 for f in target.rglob("*") if f.is_file())
            shutil.rmtree(target)

        return count

    def status(self) -> dict:
        """Return cache statistics."""
        cache_dir = self.config.cache_dir
        if not cache_dir.exists():
            return {"path": str(cache_dir), "files": 0, "size_mb": 0.0, "domains": {}}

        all_files = [f for f in cache_dir.rglob("*") if f.is_file()]
        total_size = sum(f.stat().st_size for f in all_files)

        # Per-domain breakdown
        domains: dict[str, int] = {}
        for f in all_files:
            try:
                rel = f.relative_to(cache_dir)
                if len(rel.parts) > 1:
                    d = rel.parts[0]
                    domains[d] = domains.get(d, 0) + 1
            except ValueError:
                pass

        return {
            "path": str(cache_dir),
            "files": len(all_files),
            "size_mb": round(total_size / (1024 * 1024), 2),
            "domains": domains,
        }


# -- Helpers -------------------------------------------------------------------


def _to_tz_aware(ts: pd.Timestamp, reference: pd.Timestamp) -> pd.Timestamp:
    """Convert a UTC timestamp to match the reference timestamp's timezone.

    This ensures gap boundaries have the same tz as the original request
    timestamps, avoiding tz-naive/tz-aware comparison errors.
    """
    if reference.tz is not None:
        return ts.tz_convert(reference.tz) if ts.tz is not None else ts.tz_localize(reference.tz)
    return ts.tz_localize(None) if ts.tz is not None else ts


def _merge_overlapping(gaps: list[DateRange]) -> list[DateRange]:
    """Merge overlapping or adjacent date ranges."""
    if not gaps:
        return []

    sorted_gaps = sorted(gaps, key=lambda g: g.start)
    merged = [sorted_gaps[0]]

    for gap in sorted_gaps[1:]:
        prev = merged[-1]
        if gap.start <= prev.end + pd.Timedelta(days=1):
            merged[-1] = DateRange(prev.start, max(prev.end, gap.end))
        else:
            merged.append(gap)

    return merged


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically via temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=path.parent)
        os.close(fd)
        Path(tmp_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        Path(tmp_path).rename(path)
    except OSError as exc:
        logger.warning("Failed to write %s: %s", path, exc)
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def _atomic_write_parquet(path: Path, df: pd.DataFrame) -> None:
    """Write parquet atomically via temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".parquet", dir=path.parent)
        os.close(fd)
        df.to_parquet(tmp_path)
        Path(tmp_path).rename(path)
    except OSError as exc:
        logger.warning("Failed to write cache %s: %s — continuing without cache.", path, exc)
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
