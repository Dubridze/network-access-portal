from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()


@router.get("/profile", response_model=schemas.User)
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile"""
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/profile", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated = crud.UserCRUD.update(db, user.id, user_update)
    return updated
