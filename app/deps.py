from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_subject, get_current_token_payload
from app.db.session import get_db
from app import models

def get_current_admin(
    payload=Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> models.Admin:
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    admin = db.query(models.Admin).filter(models.Admin.id == sub).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return admin
