from __future__ import annotations

from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class IdeologyOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None

# In-memory placeholder so the UI can load.
# Replace with real DB access (SQLAlchemy) later.
_FAKE_IDEOLOGIES: List[IdeologyOut] = []

@router.get("/ideologies", response_model=list[IdeologyOut])
def list_ideologies():
    return _FAKE_IDEOLOGIES

@router.post("/ideologies", response_model=IdeologyOut, status_code=201)
def create_ideology(item: IdeologyOut):
    # naive "create": if id already exists, replace; otherwise append
    for i, existing in enumerate(_FAKE_IDEOLOGIES):
        if existing.id == item.id:
            _FAKE_IDEOLOGIES[i] = item
            return item
    _FAKE_IDEOLOGIES.append(item)
    return item
