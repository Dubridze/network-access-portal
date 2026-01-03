from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.auth import get_admin_user, get_current_user

router = APIRouter()


@router.get("/public")
async def get_public_config():
    """Get public configuration (theme, title, etc)"""
    from app.config import settings
    
    return {
        "app_title": settings.APP_TITLE,
        "app_logo_url": settings.APP_LOGO_URL,
        "app_theme_color": settings.APP_THEME_COLOR,
        "keycloak_url": settings.KEYCLOAK_SERVER_URL,
        "keycloak_realm": settings.KEYCLOAK_REALM,
        "keycloak_client_id": settings.KEYCLOAK_CLIENT_ID
    }


@router.get("/admin")
async def get_admin_config(
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user())
):
    """Get admin configuration (admin only)"""
    # Implementation for admin config
    return {"message": "Admin config endpoint"}
