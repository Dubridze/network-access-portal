from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Protocol(str, Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    SSH = "ssh"
    HTTPS = "https"
    HTTP = "http"
    CUSTOM = "custom"


class RequestStatus(str, Enum):
    CREATED = "created"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class UserRole(str, Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    USER = "user"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    keycloak_id: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    keycloak_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccessRequestBase(BaseModel):
    source_ip: str = Field(..., min_length=7, max_length=45)
    destination_ip: str = Field(..., min_length=7, max_length=45)
    destination_hostname: Optional[str] = None
    port: int = Field(..., ge=1, le=65535)
    protocol: Protocol = Protocol.TCP
    description: str
    business_justification: str

    @validator('source_ip', 'destination_ip')
    def validate_ip(cls, v):
        # Basic IP validation
        import ipaddress
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('Invalid IP address')


class AccessRequestCreate(AccessRequestBase):
    pass


class AccessRequestUpdate(BaseModel):
    destination_ip: Optional[str] = None
    destination_hostname: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[Protocol] = None
    description: Optional[str] = None
    business_justification: Optional[str] = None


class AccessRequestApprove(BaseModel):
    approval_comment: Optional[str] = None


class AccessRequestReject(BaseModel):
    rejection_reason: str


class AccessRequest(AccessRequestBase):
    id: int
    request_number: str
    user_id: int
    approver_id: Optional[int]
    status: RequestStatus
    approval_comment: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    user: User
    approver: Optional[User]

    class Config:
        from_attributes = True


class AccessRequestList(BaseModel):
    id: int
    request_number: str
    source_ip: str
    destination_ip: str
    destination_hostname: Optional[str]
    port: int
    protocol: Protocol
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    user: User
    approver: Optional[User]

    class Config:
        from_attributes = True


class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: str
    details: str
    ip_address: str


class AuditLog(AuditLogBase):
    id: int
    user_id: int
    access_request_id: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]
    user_agent: str
    created_at: datetime
    user: User

    class Config:
        from_attributes = True


class ConfigurationBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class Configuration(ConfigurationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    requests: List[AccessRequestList]
    total: int
    page: int
    page_size: int


class Stats(BaseModel):
    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    total_users: int
