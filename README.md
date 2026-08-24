# Sakshya

**Sakshya** (साक्ष्य — Sanskrit for "evidence" / "witness") is a digital chain-of-custody
and case-intelligence system for legal evidence. It takes in raw evidence files
(PDFs, scans, WhatsApp screenshots, audio, video), extracts structured information
from them automatically, proves that the evidence has not been tampered with, and
gives a judge a single dashboard summarizing a case — instead of a folder of
unorganized files.

This README is written to be a complete brief: if you are an engineer (human or AI)
picking this up cold, you should be able to build the whole system from this document
alone.

---

## 1. What Sakshya actually does (plain language)

1. Someone (police, lawyer, or forensic lab) uploads a file.
2. Sakshya immediately fingerprints it (SHA-256 hash) before anything else touches it,
   and logs who uploaded it and when. This is the start of the custody chain.
3. The file is read: OCR for documents/scans, speech-to-text for audio, a tamper-risk
   score for video/images (deepfakes are flagged, not transcribed).
4. The extracted text is classified by case type (civil/property, matrimonial,
   corporate, criminal) and structured facts are pulled out (e.g. for a land deed:
   buyer, seller, date, survey number).
5. The text is stored twice, in parallel: as searchable full text in Postgres
   (source of truth), and as a vector embedding in pgvector (for semantic/"find similar
   meaning" search).
6. Every time evidence changes hands (Police → FSL → Court), that handoff is logged
   with a timestamp and a digital signature.
7. Periodically, a batch of these logs is bundled into a Merkle tree, and only the
   Merkle root is anchored on a private blockchain (Hyperledger Fabric). This is a
   checkpoint, not an inline dependency — Postgres keeps running normally in between.
8. On demand (e.g. a judge clicks "Integrity: Verified"), the system recomputes the
   Merkle root from current Postgres data and compares it to the anchored root. A
   mismatch flags exactly which time window was tampered with.
9. Separately, an agent continuously scans for *gaps* in custody — missing
   signatures, evidence with no handler for a suspicious stretch of time — which is a
   different failure mode from tampering (Step 8 catches "was this changed", this
   catches "is this trail complete").
10. A chronological case timeline is assembled automatically from already-extracted
    dates and custody events — no extra AI call, just a query and a sort.
11. On request, Sakshya finds similar past judgments (via embedding search + rerank by
    case type/statute/jurisdiction), verifies each retrieved case actually exists in
    the indexed judgment database (drops anything unverified), and summarizes the
    verified matches into a short brief.
12. All of the above resolves into one judge-facing dashboard: case summary, evidence
    list, timeline, integrity status, custody-gap status, similar judgments (if
    requested).

**Important design boundary:** Sakshya does **not** predict case outcomes or verdicts.
It retrieves and summarizes real, verified precedent — it never generates a
recommendation on how a case should be decided. Do not add verdict-prediction
features; see [Section 7](#7-things-this-project-deliberately-does-not-do).

---

## 2. Architecture at a glance

```text
Upload → Hash + metadata row (Postgres)
│
▼
Type-specific extraction
PDF/scan/screenshot → PaddleOCR → text
Audio → Whisper → transcript
Video/image → deepfake model → risk score (does NOT feed text pipeline)
│
▼
Case classification + entity extraction (Qwen 2.5 7B)
│
▼
┌─────┴─────┐
▼           ▼
Postgres    BGE-M3 → pgvector
(full text) (semantic index)
│
▼
Custody events (continuous, on every handover)
│
▼
Periodic Merkle anchoring → Hyperledger Fabric (background job)
│
▼
On-demand verification (recompute + compare Merkle root)
│
Continuous custody-gap audit agent (separate from verification)
│
▼
Timeline construction (pure query, no AI)
│
▼
Precedent retrieval (on demand) → verify against real corpus → Qwen summarizes
│
▼
Judge dashboard (assembled from Postgres queries only, no live computation)
```

---

## 3. Components / models used

| Purpose | Component | Notes |
|---|---|---|
| Document OCR | PaddleOCR | PDFs, scans, screenshots |
| Speech-to-text | Whisper | Audio evidence |
| Video/image tamper detection | Deepfake detection model | Outputs a risk score, not text |
| Case classification + extraction | Qwen 2.5 7B | Structured entity extraction per case type |
| Embeddings | BGE-M3 | Feeds pgvector for semantic search |
| Structured storage | PostgreSQL | Source of truth for everything |
| Semantic search index | pgvector | Derived index, not source of truth |
| Tamper-proof anchoring | Hyperledger Fabric (private ledger) | Stores only Merkle roots, not raw data |

---

## 4. Repository structure

```text
sakshya/
├── README.md
├── .env.example                 # demo values only — see Section 6
├── .gitignore                   # must ignore .env, *.pem, *.key, /uploads
├── docker-compose.yml           # Postgres + pgvector + Fabric dev network
├── services/
│   ├── intake/                  # upload API, hashing, metadata row
│   ├── extraction/              # PaddleOCR / Whisper / deepfake routing
│   ├── classification/          # Qwen entity extraction
│   ├── embedding/               # BGE-M3 → pgvector writer
│   ├── custody/                 # custody event logging
│   ├── anchoring/               # background Merkle batcher → Fabric
│   ├── verification/            # on-demand integrity check
│   ├── audit-agent/             # continuous custody-gap scanner
│   ├── timeline/                # query-only timeline builder
│   ├── precedent/               # retrieval + verification + summarization
│   └── dashboard-api/           # aggregates everything for the frontend
├── frontend/                    # judge dashboard UI
├── db/
│   ├── migrations/
│   └── schema.sql
└── scripts/
    └── seed-demo-data.sh
```

---

## 5. Open decisions before building

1. **Anchoring interval (Step 7):** every N minutes, or every N custody events?
   Shorter interval = smaller tamper window, more Fabric transactions, higher cost.
2. **Verification trigger (Step 8):** run on every dashboard load, or only on-demand?
   Every load is more reassuring but adds latency and Fabric read load.

---

## 6. Environment variables

**Rule: `.env.example` must only ever contain safe, fake, demo-only placeholder
values.** No real credentials, hostnames, API keys, or ledger endpoints should be
committed, ever. Real values live only in a local `.env`, which is git-ignored.

See `.env.example` and `.gitignore` in this repo.

| Variable | Required in prod | Committed to `.env.example`? |
|---|---|---|
| `DATABASE_URL` | Yes | Demo value only |
| `FABRIC_WALLET_PATH` | Yes | Demo path only, real wallet files git-ignored |
| `JWT_SECRET` / `SESSION_SECRET` | Yes | Demo value only, rotate per environment |
| `QWEN_ENDPOINT`, `BGE_M3_ENDPOINT`, etc. | Yes | Demo/local value only |

---

## 7. Things this project deliberately does not do

- **No verdict prediction.** Sakshya retrieves and summarizes real, verified past
  judgments. It never predicts or recommends how a case should be decided.
- **No unverified precedent citation.** Every retrieved case ID is checked against the
  real indexed judgment database before reaching a user; unconfirmed matches are
  dropped silently.
- **No inline blockchain writes.** Fabric is a periodic batch checkpoint only —
  Postgres performance never depends on ledger latency.

---

## 8. Getting started (dev)

```bash
cp .env.example .env
# edit .env with your real local model endpoints and DB credentials
docker-compose up -d postgres pgvector fabric-dev
npm run migrate
./scripts/seed-demo-data.sh
npm run dev
```

## 9. Contributing

- Keep Postgres as the single source of truth. pgvector and Fabric are derived and
  must be rebuildable from Postgres if lost.
- Add new case-type extraction fields via the extraction prompt/schema config, not
  hardcoded per case type in application logic.
- Never commit real credentials. See Section 6.
