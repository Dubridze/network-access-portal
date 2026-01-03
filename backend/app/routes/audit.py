from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[schemas.AuditLog])
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get audit logs (admin only)"""
    if "admin" not in current_user.get("roles", []):
        # Users can only see their own audit logs
        user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
        return crud.AuditLogCRUD.get_by_user(db, user.id, skip, limit)
    
    return crud.AuditLogCRUD.get_all(db, skip, limit)
