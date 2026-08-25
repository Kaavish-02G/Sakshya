from storage.evidence_store import EvidenceStore


def get_evidence_or_raise(store: EvidenceStore, evidence_id: str) -> dict:
    return store.get(evidence_id)
