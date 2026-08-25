from fastapi import FastAPI

from api.analysis_routes import router as analysis_router
from api.custody_routes import router as custody_router
from api.evidence_routes import router as evidence_router

app = FastAPI(title="NYAYACHAIN API", version="1.1.0")
app.include_router(evidence_router)
app.include_router(analysis_router)
app.include_router(custody_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "NYAYACHAIN forensic API"}
