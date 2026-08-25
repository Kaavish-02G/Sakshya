from typing import Optional

from forensic.integrity import calculate_hash
from utils.file_utils import utc_now


def build_custody_event(file_path: str, custodian: str, action: str, notes: Optional[str] = None) -> dict:
    return {"custodian": custodian, "timestamp": utc_now(), "action": action, "notes": notes or "", "hash": calculate_hash(file_path)}
