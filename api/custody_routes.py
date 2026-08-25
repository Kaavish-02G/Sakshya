from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from custody.custody_audit import audit_custody
from storage.evidence_store import EvidenceStore

router = APIRouter(prefix="/evidence", tags=["custody"])
store = EvidenceStore()


class CustodyEventRequest(BaseModel):
    custodian: str
    action: str
    notes: Optional[str] = None


@router.post("/{evidence_id}/custody")
def add_custody_event(evidence_id: str, event: CustodyEventRequest):
    try:
        return store.add_custody_event(evidence_id, event.custodian, event.action, event.notes)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{evidence_id}/custody")
def get_custody(evidence_id: str):
    try:
        record = store.get(evidence_id)
        return {"evidence_id": evidence_id, "events": record["custody_events"], "audit": audit_custody(record["custody_events"])}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
