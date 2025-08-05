from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.audit_log import AuditLog, ActionType

def log_admin_action(
    db: Session,
    *,
    admin_id: uuid.UUID,
    action: ActionType,
    table_name: str,
    entity_id: uuid.UUID
):
    """Logs an admin action to the audit table."""
    db_log = AuditLog(
        admin_id=admin_id,
        action=action,
        table_name=table_name,
        entity_id=entity_id,
        timestamp=datetime.utcnow()
    )
    db.add(db_log)
    db.commit() # In a more complex app, we might commit this with the main transaction