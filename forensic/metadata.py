import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from forensic.integrity import calculate_hash


def extract_metadata(file_path: str | Path) -> dict:
    path = Path(file_path)
    stat = path.stat()
    return {
        "filename": path.name,
        "extension": path.suffix.lower() or None,
        "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": calculate_hash(path),
    }
