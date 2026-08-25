import hashlib
from pathlib import Path


def calculate_hash(file_path: str | Path) -> str:
    """Calculate SHA-256 over the exact bytes of a file."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_hash(file_path: str | Path, original_hash: str) -> dict:
    current_hash = calculate_hash(file_path)
    matched = current_hash == original_hash
    return {
        "status": "VERIFIED" if matched else "INTEGRITY_MISMATCH",
        "tampered": not matched,
        "original_hash": original_hash,
        "current_hash": current_hash,
        "note": "A mismatch means current bytes differ from registered bytes; it does not prove malicious tampering.",
    }
