import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DATA_DIR, REGISTRY_PATH, UPLOADS_DIR
from custody.custody_manager import build_custody_event
from forensic.integrity import verify_hash
from forensic.metadata import extract_metadata


class EvidenceStore:
    """JSON-backed MVP store; its public methods can later be backed by PostgreSQL."""
    def __init__(self, registry_path: Path = REGISTRY_PATH, uploads_dir: Path = UPLOADS_DIR):
        self.registry_path, self.uploads_dir = registry_path, uploads_dir
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self._write({})

    def _read(self) -> dict:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _write(self, records: dict) -> None:
        self.registry_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def register(self, source_path: str | Path, custodian: str = "Police", original_filename: Optional[str] = None) -> dict:
        source = Path(source_path)
        evidence_id = f"NYC-{datetime.now():%Y}-{uuid.uuid4().hex[:6].upper()}"
        stored_path = self.uploads_dir / f"{evidence_id}{source.suffix.lower()}"
        shutil.copy2(source, stored_path)
        record = extract_metadata(stored_path)
        record.update({"evidence_id": evidence_id, "filename": original_filename or source.name, "stored_path": str(stored_path), "custody_events": []})
        record["custody_events"].append(build_custody_event(str(stored_path), custodian, "Evidence registered"))
        records = self._read(); records[evidence_id] = record; self._write(records)
        return record

    def get(self, evidence_id: str) -> dict:
        record = self._read().get(evidence_id)
        if not record:
            raise KeyError(f"Evidence ID not found: {evidence_id}")
        return record

    def verify(self, evidence_id: str, file_path: Optional[str] = None) -> dict:
        record = self.get(evidence_id)
        result = verify_hash(file_path or record["stored_path"], record["sha256"])
        result["evidence_id"] = evidence_id
        return result

    def add_custody_event(self, evidence_id: str, custodian: str, action: str, notes: Optional[str] = None) -> dict:
        records = self._read(); record = self.get(evidence_id)
        event = build_custody_event(record["stored_path"], custodian, action, notes)
        record["custody_events"].append(event); records[evidence_id] = record; self._write(records)
        return event
