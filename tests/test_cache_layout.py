"""Offline tests for cache layout versioning."""

from entsoe.cache import CACHE_LAYOUT_VERSION, CacheConfig, CacheStore


def test_outdated_layouts_are_purged(tmp_path):
    legacy = tmp_path / "prices" / "day_ahead" / "DE_LU"
    legacy.mkdir(parents=True)
    (legacy / "data.parquet").write_bytes(b"stale")
    old_version = tmp_path / "v1" / "load"
    old_version.mkdir(parents=True)
    current = tmp_path / f"v{CACHE_LAYOUT_VERSION}" / "prices"
    current.mkdir(parents=True)
    unrelated = tmp_path / "notes.txt"
    unrelated.write_text("keep")

    store = CacheStore(CacheConfig(cache_dir=tmp_path))

    assert not (tmp_path / "prices").exists()
    assert not (tmp_path / "v1").exists()
    assert current.exists()
    assert unrelated.exists()
    assert store.root == tmp_path / f"v{CACHE_LAYOUT_VERSION}"
