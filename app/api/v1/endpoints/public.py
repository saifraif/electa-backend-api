from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

APPROVED_DIR = Path("storage/approved")
APPROVED_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/public")


class Party(BaseModel):
    id: Optional[str] = None
    name: str
    abbrev: Optional[str] = None
    logoUrl: Optional[str] = None
    description: Optional[str] = None


class Candidate(BaseModel):
    id: Optional[str] = None
    fullName: str
    partyName: Optional[str] = None
    constituencyName: Optional[str] = None
    photoUrl: Optional[str] = None
    bio: Optional[str] = None


class Paged(BaseModel):
    items: List[Any]
    page: int
    size: int
    total: int


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


@router.get("/parties", response_model=Paged)
async def get_parties(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
):
    rows = _read_jsonl(APPROVED_DIR / "party.jsonl")

    if search:
        s = search.lower()
        rows = [r for r in rows if s in (r.get("name", "") or "").lower()]

    total = len(rows)
    start = (page - 1) * size
    end = start + size
    page_items = rows[start:end]

    # normalize keys → Party model-like
    def norm(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": r.get("id"),
            "name": r.get("name") or r.get("full_name") or r.get("title") or "Unknown",
            "abbrev": r.get("abbrev"),
            "logoUrl": r.get("logo_url") or r.get("logoUrl"),
            "description": r.get("description"),
        }

    return Paged(items=[norm(r) for r in page_items], page=page, size=size, total=total)


@router.get("/candidates", response_model=Paged)
async def get_candidates(
    party: Optional[str] = Query(None),
    constituency: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
):
    rows = _read_jsonl(APPROVED_DIR / "candidate.jsonl")

    def match(r: Dict[str, Any]) -> bool:
        ok = True
        if party:
            p = (r.get("party_guess") or r.get("partyName") or "").lower()
            ok = ok and (party.lower() in p)
        if constituency:
            c = (r.get("constituency_guess") or r.get("constituencyName") or "").lower()
            ok = ok and (constituency.lower() in c)
        if q:
            s = q.lower()
            ok = ok and (
                s in (r.get("full_name") or r.get("fullName") or "").lower()
                or s in (r.get("bio") or "").lower()
            )
        return ok

    rows = [r for r in rows if match(r)]

    total = len(rows)
    start = (page - 1) * size
    end = start + size
    page_items = rows[start:end]

    def norm(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": r.get("id"),
            "fullName": r.get("full_name") or r.get("fullName") or "Unknown",
            "partyName": r.get("party_guess") or r.get("partyName"),
            "constituencyName": r.get("constituency_guess") or r.get("constituencyName"),
            "photoUrl": r.get("photo_url") or r.get("photoUrl"),
            "bio": r.get("bio"),
        }

    return Paged(items=[norm(r) for r in page_items], page=page, size=size, total=total)
