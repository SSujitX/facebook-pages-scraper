import json
from pathlib import Path


def save_json(data, path: str | Path) -> Path:
    """Write data to path as UTF-8 JSON, creating parent folders. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def save_result(result, path: str | Path | None):
    """Save a scrape result when a path is given. A failed (None) result is not written."""
    if path is None:
        return result
    if result is None:
        print(f"Nothing saved to [{path}]: the scrape failed")
        return result
    print(f"Saved to [{save_json(result, path)}]")
    return result
