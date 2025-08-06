import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base

class CharterClause(Base):
    __tablename__ = "charterclauses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("charterversions.id"))
    clause_number = Column(String)
    title = Column(String)
    clause_text_json = Column(JSONB)
    clause_group = Column(String) # e.g., "Judiciary", "Anti-Corruption"