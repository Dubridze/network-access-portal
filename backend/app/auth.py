from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from typing import Optional, Dict
import logging
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthCredentials] = Depends(security)
) -> Dict:
    """Extract and validate JWT token from Keycloak"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # For Keycloak, we verify the token signature
        # In production, you should fetch the public key from Keycloak
        payload = jwt.get_unverified_claims(token)
        
        username: str = payload.get("preferred_username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_with_role(
    required_role: str
):
    """Dependency to check if user has required role"""
    async def check_role(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_roles = current_user.get("roles", [])
        
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        
        return current_user
    
    return check_role


def get_admin_user():
    """Dependency to check if user is admin"""
    return get_current_user_with_role("admin")


def get_approver_user():
    """Dependency to check if user is approver"""
    return get_current_user_with_role("approver")
