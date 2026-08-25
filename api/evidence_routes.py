import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from storage.evidence_store import EvidenceStore

router = APIRouter(prefix="/evidence", tags=["evidence"])
store = EvidenceStore()


async def _save_upload(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "evidence.bin").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
        shutil.copyfileobj(upload.file, temporary)
        return temporary.name


@router.post("/register")
async def register_evidence(file: UploadFile = File(...), custodian: str = "Police"):
    temporary_path = await _save_upload(file)
    try:
        return store.register(temporary_path, custodian, file.filename)
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@router.get("/{evidence_id}")
def get_evidence(evidence_id: str):
    try:
        return store.get(evidence_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{evidence_id}/verify")
def verify_evidence(evidence_id: str):
    try:
        return store.verify(evidence_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
