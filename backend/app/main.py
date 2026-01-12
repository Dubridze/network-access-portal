from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional
import logging
from datetime import datetime

from app.config import settings
from app.database import engine, SessionLocal, Base
from app.routes import requests as request_routes
from app.routes import users as user_routes
from app.routes import audit as audit_routes
from app.routes import admin as admin_routes
from app.routes import config as config_routes
from app.routes import auth as auth_routes
from app.auth import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables (checkfirst=True prevents duplicate errors)
Base.metadata.create_all(bind=engine, checkfirst=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Network Access Portal")
    yield
    # Shutdown
    logger.info("Shutting down Network Access Portal")

app = FastAPI(
    title="Network Access Portal API",
    description="API for managing network access requests with role-based access control",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_routes.router, prefix="/api", tags=["Auth"])
app.include_router(request_routes.router, prefix="/api/requests", tags=["Requests"])
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(audit_routes.router, prefix="/api/audit", tags=["Audit"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(config_routes.router, prefix="/api/config", tags=["Configuration"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/me", tags=["Auth"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.get("sub"),
        "username": current_user.get("preferred_username"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "roles": current_user.get("roles", []),
        "created_at": current_user.get("iat")
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Network Access Portal API",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
