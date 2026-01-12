"""Authentication routes for OAuth2 code-to-token exchange.

This module provides a secure backend endpoint for exchanging Keycloak
authorization codes for access tokens. This is safer than having the
frontend JavaScript application exchange codes directly, as the client
secret never leaves the backend server.
"""

from fastapi import APIRouter, HTTPException, status
import httpx
import logging
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class TokenExchangeRequest(BaseModel):
    """Request body for code-to-token exchange."""
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str
    scope: str
    refresh_token: str | None = None


@router.post(
    "/auth/token",
    response_model=TokenResponse,
    tags=["Auth"],
    summary="Exchange authorization code for access token",
    description="""Securely exchange Keycloak authorization code for JWT access token.
    
    This endpoint acts as a backend proxy for OAuth2 code-to-token exchange.
    The client secret is kept secure on the backend and never exposed to the
    frontend JavaScript application.
    """,
)
async def exchange_code_for_token(request: TokenExchangeRequest):
    """Exchange Keycloak authorization code for JWT access token.
    
    Args:
        request: Contains authorization code and redirect URI
        
    Returns:
        Token response with access_token, refresh_token, and metadata
        
    Raises:
        HTTPException: If token exchange fails (invalid code, expired, etc.)
    """
    
    token_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        "/protocol/openid-connect/token"
    )
    
    logger.info(
        f"Attempting token exchange for redirect_uri: {request.redirect_uri}"
    )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": request.code,
                    "client_id": settings.KEYCLOAK_CLIENT_ID,
                    "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                    "redirect_uri": request.redirect_uri,
                },
            )
        
        logger.debug(f"Token exchange response status: {response.status_code}")
        
        if response.status_code != 200:
            error_data = response.json()
            logger.warning(
                f"Token exchange failed: {error_data.get('error', 'unknown_error')}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token exchange failed: {error_data.get('error_description', 'Unknown error')}",
            )
        
        token_data = response.json()
        logger.info("Token exchange successful")
        
        return TokenResponse(**token_data)
        
    except httpx.TimeoutException:
        logger.error("Token exchange timeout - Keycloak server not responding")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Keycloak server not responding. Please try again later.",
        )
    except httpx.RequestError as e:
        logger.error(f"Token exchange request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to authentication server",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )


@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    tags=["Auth"],
    summary="Refresh access token",
    description="Use refresh token to obtain new access token",
)
async def refresh_token(refresh_token: str):
    """Refresh an expired access token using refresh token.
    
    Args:
        refresh_token: The refresh token from previous authentication
        
    Returns:
        New token response with updated access_token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    
    token_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        "/protocol/openid-connect/token"
    )
    
    logger.info("Attempting token refresh")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.KEYCLOAK_CLIENT_ID,
                    "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                },
            )
        
        if response.status_code != 200:
            error_data = response.json()
            logger.warning(
                f"Token refresh failed: {error_data.get('error', 'unknown_error')}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid",
            )
        
        token_data = response.json()
        logger.info("Token refresh successful")
        
        return TokenResponse(**token_data)
        
    except httpx.TimeoutException:
        logger.error("Token refresh timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication server not responding",
        )
    except httpx.RequestError as e:
        logger.error(f"Token refresh request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to authentication server",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/auth/logout",
    tags=["Auth"],
    summary="Revoke refresh token",
    description="Logout by revoking refresh token on Keycloak",
)
async def logout(refresh_token: str):
    """Revoke refresh token to logout user.
    
    Args:
        refresh_token: The refresh token to revoke
        
    Returns:
        Success message
    """
    
    logout_url = (
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        "/protocol/openid-connect/revoke"
    )
    
    logger.info("Attempting token revocation for logout")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                logout_url,
                data={
                    "token": refresh_token,
                    "client_id": settings.KEYCLOAK_CLIENT_ID,
                    "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                },
            )
        
        if response.status_code in (200, 204):
            logger.info("Token revocation successful")
            return {"message": "Logged out successfully"}
        
        logger.warning(f"Token revocation returned status {response.status_code}")
        return {"message": "Logout request processed"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Don't raise exception for logout - client will handle it
        return {"message": "Logout processed"}
