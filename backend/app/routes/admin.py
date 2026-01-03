from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.auth import get_admin_user

router = APIRouter()


@router.get("/users", response_model=list[schemas.User])
async def get_all_users(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user()),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all users (admin only)"""
    return crud.UserCRUD.get_all(db, skip, limit)


@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user())
):
    """Update user (admin only)"""
    user = crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated = crud.UserCRUD.update(db, user_id, user_update)
    return updated


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user())
):
    """Get portal statistics (admin only)"""
    total_users = db.query(models.User).count()
    total_requests = db.query(models.AccessRequest).count()
    pending_requests = db.query(models.AccessRequest).filter(
        models.AccessRequest.status == models.RequestStatus.PENDING_APPROVAL
    ).count()
    approved_requests = db.query(models.AccessRequest).filter(
        models.AccessRequest.status == models.RequestStatus.APPROVED
    ).count()
    rejected_requests = db.query(models.AccessRequest).filter(
        models.AccessRequest.status == models.RequestStatus.REJECTED
    ).count()
    
    return schemas.Stats(
        total_users=total_users,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests
    )
