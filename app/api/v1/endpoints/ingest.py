from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from app.services.crawler import crawl_and_extract

router = APIRouter(prefix="/ingest")

STORE_DIR = Path("storage/ingest")
APPROVED_DIR = Path("storage/approved")
STORE_DIR.mkdir(parents=True, exist_ok=True)
APPROVED_DIR.mkdir(parents=True, exist_ok=True)


class CreateJobRequest(BaseModel):
    url: HttpUrl


class JobSummary(BaseModel):
    id: str
    url: HttpUrl
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class JobDetail(JobSummary):
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ApprovePayload(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


def _job_path(job_id: str) -> Path:
    return STORE_DIR / f"{job_id}.json"


def _load_job(job_id: str) -> Dict[str, Any]:
    p = _job_path(job_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(p.read_text(encoding="utf-8"))


def _save_job(job: Dict[str, Any]) -> None:
    p = _job_path(job["id"])
    job["updated_at"] = datetime.utcnow().isoformat()
    p.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")


async def _run_job(job_id: str, url: str) -> None:
    job = _load_job(job_id)
    job["status"] = "running"
    _save_job(job)
    try:
        result = await crawl_and_extract(url)
        job["status"] = "success"
        job["result"] = result
        _save_job(job)
    except Exception as e:
        job["status"] = "error"
        job["error"] = f"{type(e).__name__}: {e}"
        _save_job(job)


@router.post("/jobs", response_model=JobDetail, status_code=status.HTTP_202_ACCEPTED)
async def create_job(body: CreateJobRequest):
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    job = {
        "id": job_id,
        "url": str(body.url),
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "result": None,
        "error": None,
    }
    _save_job(job)
    # schedule the crawl (don't block the request)
    asyncio.create_task(_run_job(job_id, str(body.url)))
    return _load_job(job_id)


@router.get("/jobs", response_model=List[JobSummary])
async def list_jobs():
    out: List[JobSummary] = []
    for p in sorted(STORE_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        j = json.loads(p.read_text(encoding="utf-8"))
        out.append(JobSummary.model_validate(j))
    return out


@router.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job(job_id: str):
    return JobDetail.model_validate(_load_job(job_id))


@router.post("/extracted/{kind}/{index}/approve", status_code=status.HTTP_200_OK)
async def approve_extracted(kind: str, index: int, body: ApprovePayload, job_id: Optional[str] = None):
    kind = kind.lower()
    if kind not in ("party", "candidate"):
        raise HTTPException(status_code=400, detail="kind must be 'party' or 'candidate'")

    approved = body.payload or {}

    if job_id:
        job = _load_job(job_id)
        if job.get("status") != "success" or not job.get("result"):
            raise HTTPException(status_code=400, detail="Job has no successful result to approve from")

        entities: Dict[str, Any] = job["result"].get("entities", {})
        key = "parties" if kind == "party" else "candidates"
        items: List[Dict[str, Any]] = entities.get(key, [])
        if not (0 <= index < len(items)):
            raise HTTPException(status_code=404, detail="Index not found in extracted entities")

        base = items[index]
        base.update(approved)
        approved = base

    out_file = APPROVED_DIR / f"{kind}.jsonl"
    with out_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(approved, ensure_ascii=False) + "\n")

    return {"status": "ok", "approved": approved}
