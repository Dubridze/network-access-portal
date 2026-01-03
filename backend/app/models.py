from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class RequestStatus(str, enum.Enum):
    CREATED = "created"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    USER = "user"


class Protocol(str, enum.Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    SSH = "ssh"
    HTTPS = "https"
    HTTP = "http"
    CUSTOM = "custom"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_keycloak_id', 'keycloak_id'),
        Index('idx_users_username', 'username'),
    )

    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    requests = relationship("AccessRequest", back_populates="user", foreign_keys="AccessRequest.user_id")
    approvals = relationship("AccessRequest", back_populates="approver", foreign_keys="AccessRequest.approver_id")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class AccessRequest(Base):
    __tablename__ = "access_requests"
    __table_args__ = (
        Index('idx_access_requests_user_id', 'user_id'),
        Index('idx_access_requests_status', 'status'),
        Index('idx_access_requests_approver_id', 'approver_id'),
        Index('idx_access_requests_created_at', 'created_at'),
        Index('idx_access_requests_source_ip', 'source_ip'),
        Index('idx_access_requests_destination_ip', 'destination_ip'),
        Index('idx_access_requests_request_number', 'request_number'),
    )

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    source_ip = Column(String(50), index=True)
    destination_ip = Column(String(50), index=True)
    destination_hostname = Column(String(255))
    port = Column(Integer)
    protocol = Column(Enum(Protocol), default=Protocol.TCP)
    description = Column(Text)
    business_justification = Column(Text)
    
    status = Column(Enum(RequestStatus), default=RequestStatus.CREATED, index=True)
    approval_comment = Column(Text)
    rejection_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="requests", foreign_keys=[user_id])
    approver = relationship("User", back_populates="approvals", foreign_keys=[approver_id])
    audit_logs = relationship("AuditLog", back_populates="access_request", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AccessRequest {self.request_number}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_access_request_id', 'access_request_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    access_request_id = Column(Integer, ForeignKey("access_requests.id"), nullable=True, index=True)
    action = Column(String(255), index=True)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="audit_logs")
    access_request = relationship("AccessRequest", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"


class Configuration(Base):
    __tablename__ = "configurations"
    __table_args__ = (
        Index('idx_config_key', 'key'),
    )

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True)
    value = Column(Text)
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Configuration {self.key}>"
