from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request

from app import crud, models
from app.utils import get_ip_from_request, get_user_agent


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        details: str,
        request: Optional[Request] = None,
        access_request_id: Optional[int] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> models.AuditLog:
        """Log user action to audit log"""
        ip_address = get_ip_from_request(request) if request else "unknown"
        user_agent = get_user_agent(request) if request else "unknown"
        
        return crud.AuditLogCRUD.create(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            access_request_id=access_request_id,
            old_value=old_value,
            new_value=new_value
        )
    
    @staticmethod
    def log_request_created(
        db: Session,
        user_id: int,
        request_id: int,
        request_number: str,
        http_request: Optional[Request] = None
    ):
        """Log request creation"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="created",
            resource_type="access_request",
            resource_id=request_number,
            details=f"Created access request",
            request=http_request,
            access_request_id=request_id
        )
    
    @staticmethod
    def log_request_approved(
        db: Session,
        user_id: int,
        request_id: int,
        request_number: str,
        http_request: Optional[Request] = None
    ):
        """Log request approval"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="approved",
            resource_type="access_request",
            resource_id=request_number,
            details=f"Approved access request",
            request=http_request,
            access_request_id=request_id
        )
    
    @staticmethod
    def log_request_rejected(
        db: Session,
        user_id: int,
        request_id: int,
        request_number: str,
        reason: str,
        http_request: Optional[Request] = None
    ):
        """Log request rejection"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="rejected",
            resource_type="access_request",
            resource_id=request_number,
            details=f"Rejected access request: {reason}",
            request=http_request,
            access_request_id=request_id
        )
