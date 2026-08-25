from pathlib import Path

from config import AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, TEXT_EXTENSIONS, VIDEO_EXTENSIONS
from custody.custody_audit import audit_custody
from detectors import detect_audio, detect_image, detect_text, detect_video
from storage.evidence_store import EvidenceStore


def analyze_evidence(store: EvidenceStore, evidence_id: str) -> dict:
    record = store.get(evidence_id)
    extension, path = Path(record["stored_path"]).suffix.lower(), record["stored_path"]
    if extension in IMAGE_EXTENSIONS:
        analysis = {"image": detect_image(path)}
    elif extension in VIDEO_EXTENSIONS:
        analysis = {"video": detect_video(path)}
    elif extension in AUDIO_EXTENSIONS:
        analysis = {"audio": detect_audio(path)}
    elif extension in TEXT_EXTENSIONS:
        analysis = {"text": detect_text(Path(path).read_text(encoding="utf-8", errors="replace"))}
    else:
        analysis = {"status": "No AI detector is configured for this file type; integrity and custody remain available."}
    result = next((value for value in analysis.values() if isinstance(value, dict) and "risk" in value), {})
    return build_report(record, store.verify(evidence_id), analysis, audit_custody(record["custody_events"]), result.get("risk", "INCONCLUSIVE"))


def build_report(evidence: dict, integrity: dict, analysis: dict, custody: dict, overall_risk: str) -> dict:
    metadata_keys = ("extension", "mime_type", "size_bytes", "created_at", "modified_at", "sha256")
    return {"report_title": "NYAYACHAIN FORENSIC REPORT", "evidence": {"evidence_id": evidence["evidence_id"], "filename": evidence["filename"]},
            "integrity": integrity, "metadata": {key: evidence[key] for key in metadata_keys}, "analysis": analysis,
            "custody": custody, "overall_risk": overall_risk,
            "legal_notice": "Automated outputs are forensic screening signals, not legal proof."}
