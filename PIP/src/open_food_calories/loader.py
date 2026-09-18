import json
import time
from importlib import resources
from pathlib import Path

import requests

REMOTE_URL = (
    "https://raw.githubusercontent.com/chpalitom09-bot/"
    "Open-food-calories/main/data/Open-food-calories.json"
)

CACHE_DIR = Path.home() / ".cache" / "open-food-calories"
CACHE_FILE = CACHE_DIR / "data.json"
CACHE_TTL_SECONDS = 24 * 60 * 60


def _load_bundled_snapshot():
    with resources.files("open_food_calories.assets").joinpath("snapshot.json").open(
        "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def _cache_is_fresh():
    if not CACHE_FILE.exists():
        return False
    age = time.time() - CACHE_FILE.stat().st_mtime
    return age < CACHE_TTL_SECONDS


def _read_cache():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_cache(data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def _fetch_remote(timeout=6):
    response = requests.get(REMOTE_URL, timeout=timeout)
    response.raise_for_status()
    return response.json()


def cache_info():
    if not CACHE_FILE.exists():
        return None
    age = time.time() - CACHE_FILE.stat().st_mtime
    return {
        "path": str(CACHE_FILE),
        "size_bytes": CACHE_FILE.stat().st_size,
        "age_seconds": int(age),
        "fresh": age < CACHE_TTL_SECONDS,
    }


def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        return True
    return False


def load_data(refresh=False, offline=False):
    if offline:
        if CACHE_FILE.exists():
            return _read_cache()
        return _load_bundled_snapshot()

    if not refresh and _cache_is_fresh():
        return _read_cache()

    try:
        data = _fetch_remote()
        _write_cache(data)
        return data
    except Exception:
        if CACHE_FILE.exists():
            return _read_cache()
        return _load_bundled_snapshot()
