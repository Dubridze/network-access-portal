from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List
import logging

from app import models, schemas
from app.utils import generate_request_number

logger = logging.getLogger(__name__)


class UserCRUD:
    @staticmethod
    def get_or_create(db: Session, keycloak_id: str, user_data: schemas.UserCreate) -> models.User:
        """Get existing user or create new one"""
        user = db.query(models.User).filter(
            models.User.keycloak_id == keycloak_id
        ).first()
        
        if not user:
            user = models.User(
                keycloak_id=keycloak_id,
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.username}")
        
        return user
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.username == username).first()
    
    @staticmethod
    def get_by_keycloak_id(db: Session, keycloak_id: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.keycloak_id == keycloak_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        return db.query(models.User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            update_data = user_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            db.commit()
            db.refresh(user)
        return user


class AccessRequestCRUD:
    @staticmethod
    def create(db: Session, user_id: int, request_data: schemas.AccessRequestCreate) -> models.AccessRequest:
        """Create new access request"""
        request_number = generate_request_number()
        
        access_request = models.AccessRequest(
            request_number=request_number,
            user_id=user_id,
            source_ip=request_data.source_ip,
            destination_ip=request_data.destination_ip,
            destination_hostname=request_data.destination_hostname,
            port=request_data.port,
            protocol=request_data.protocol,
            description=request_data.description,
            business_justification=request_data.business_justification,
            status=models.RequestStatus.CREATED
        )
        db.add(access_request)
        db.commit()
        db.refresh(access_request)
        logger.info(f"Created access request: {access_request.request_number}")
        return access_request
    
    @staticmethod
    def get_by_id(db: Session, request_id: int) -> Optional[models.AccessRequest]:
        return db.query(models.AccessRequest).filter(
            models.AccessRequest.id == request_id
        ).first()
    
    @staticmethod
    def get_by_number(db: Session, request_number: str) -> Optional[models.AccessRequest]:
        return db.query(models.AccessRequest).filter(
            models.AccessRequest.request_number == request_number
        ).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.AccessRequest]:
        return db.query(models.AccessRequest).filter(
            models.AccessRequest.user_id == user_id
        ).order_by(models.AccessRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pending(db: Session, skip: int = 0, limit: int = 100) -> List[models.AccessRequest]:
        """Get all pending requests for approval"""
        return db.query(models.AccessRequest).filter(
            models.AccessRequest.status == models.RequestStatus.PENDING_APPROVAL
        ).order_by(models.AccessRequest.created_at.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.AccessRequest]:
        return db.query(models.AccessRequest).order_by(
            models.AccessRequest.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, request_id: int, request_update: schemas.AccessRequestUpdate) -> Optional[models.AccessRequest]:
        request = db.query(models.AccessRequest).filter(
            models.AccessRequest.id == request_id
        ).first()
        
        if request and request.status == models.RequestStatus.CREATED:
            update_data = request_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(request, field, value)
            db.commit()
            db.refresh(request)
            logger.info(f"Updated access request: {request.request_number}")
        
        return request
    
    @staticmethod
    def approve(db: Session, request_id: int, approver_id: int, comment: Optional[str] = None) -> Optional[models.AccessRequest]:
        """Approve access request"""
        request = db.query(models.AccessRequest).filter(
            models.AccessRequest.id == request_id
        ).first()
        
        if request:
            request.status = models.RequestStatus.APPROVED
            request.approver_id = approver_id
            request.approval_comment = comment
            request.approved_at = datetime.utcnow()
            db.commit()
            db.refresh(request)
            logger.info(f"Approved access request: {request.request_number}")
        
        return request
    
    @staticmethod
    def reject(db: Session, request_id: int, approver_id: int, reason: str) -> Optional[models.AccessRequest]:
        """Reject access request"""
        request = db.query(models.AccessRequest).filter(
            models.AccessRequest.id == request_id
        ).first()
        
        if request:
            request.status = models.RequestStatus.REJECTED
            request.approver_id = approver_id
            request.rejection_reason = reason
            request.rejected_at = datetime.utcnow()
            db.commit()
            db.refresh(request)
            logger.info(f"Rejected access request: {request.request_number}")
        
        return request
    
    @staticmethod
    def search(
        db: Session,
        query: Optional[str] = None,
        status: Optional[models.RequestStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[models.AccessRequest], int]:
        """Search access requests"""
        q = db.query(models.AccessRequest)
        
        if query:
            # Search by request number, username, or IP
            q = q.filter(or_(
                models.AccessRequest.request_number.ilike(f"%{query}%"),
                models.AccessRequest.source_ip.ilike(f"%{query}%"),
                models.AccessRequest.destination_ip.ilike(f"%{query}%")
            ))
        
        if status:
            q = q.filter(models.AccessRequest.status == status)
        
        total = q.count()
        requests = q.order_by(
            models.AccessRequest.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return requests, total


class AuditLogCRUD:
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        details: str,
        ip_address: str,
        user_agent: str,
        access_request_id: Optional[int] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> models.AuditLog:
        """Create audit log entry"""
        audit_log = models.AuditLog(
            user_id=user_id,
            access_request_id=access_request_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        return audit_log
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return db.query(models.AuditLog).filter(
            models.AuditLog.user_id == user_id
        ).order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return db.query(models.AuditLog).order_by(
            models.AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()
