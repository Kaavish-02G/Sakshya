from fastapi import APIRouter, HTTPException

from forensic.report import analyze_evidence
from storage.evidence_store import EvidenceStore

router = APIRouter(prefix="/evidence", tags=["analysis"])
store = EvidenceStore()


@router.post("/{evidence_id}/analyze")
def analyze(evidence_id: str):
    try:
        return analyze_evidence(store, evidence_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Analysis could not complete: {error}")


@router.get("/{evidence_id}/report")
def report(evidence_id: str):
    return analyze(evidence_id)
