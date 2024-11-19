"""Cache module aimed to contain all the data storage and retrieval logic."""

import json
import os
from functools import wraps
from pathlib import Path

IS_GCP = (
    os.getenv("GAE_ENV") is not None or os.getenv("GOOGLE_CLOUD_PROJECT") is not None
)

if not IS_GCP:
    CACHE_DIR = Path("data_cache")
    CACHE_DIR.mkdir(exist_ok=True)
else:
    print("Running on Google Cloud Platform. Disabling cache.")


def load_json(file_path: Path) -> dict:
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf8") as file:
        return json.load(file)


def save_json(data: dict, file_path: Path) -> None:
    """Save JSON data to a file."""
    with open(file_path, "w", encoding="utf8") as file:
        json.dump(data, file)


def cache(func):
    """
    Cache the results of a function.
    JSON logic can be replaced with DB solutions (i.e. MongoDB)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if IS_GCP:  # Disable cache on GCP
            return func(*args, **kwargs)
        cache_key = f"{func.__name__}/{'_'.join(map(str, args))}.json"
        cache_path = CACHE_DIR / cache_key
        cache_path.parent.mkdir(exist_ok=True)

        if cache_path.exists():
            try:
                return load_json(cache_path)
            except json.JSONDecodeError:
                print(f"Error loading cache for {cache_path}. Recomputing...")

        if data := func(*args, **kwargs):
            save_json(data, cache_path)
            return data
        return None

    return wrapper


if __name__ == "__main__":
    raise NotImplementedError("This module is not meant to be executed directly.")
