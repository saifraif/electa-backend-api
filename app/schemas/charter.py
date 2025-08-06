import uuid
from pydantic import BaseModel, Json
from typing import Optional, Any
from datetime import datetime

# Schemas for CharterClause
class CharterClauseBase(BaseModel):
    clause_number: Optional[str] = None
    title: Optional[str] = None
    clause_text_json: Optional[Any] = None
    clause_group: Optional[str] = None

class CharterClauseCreate(CharterClauseBase):
    version_id: uuid.UUID
    title: str

class CharterClause(CharterClauseBase):
    id: uuid.UUID
    version_id: uuid.UUID

    class Config:
        from_attributes = True

# Schemas for CharterVersion
class CharterVersionBase(BaseModel):
    version_name: str
    effective_date: Optional[datetime] = None

class CharterVersionCreate(CharterVersionBase):
    pass

class CharterVersion(CharterVersionBase):
    id: uuid.UUID
    is_active: bool

    class Config:
        from_attributes = True