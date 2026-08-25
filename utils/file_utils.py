from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def extension_for(file_path: str | Path) -> str:
    return Path(file_path).suffix.lower()
