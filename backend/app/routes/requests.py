from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional

from app import crud, schemas, models
from app.database import get_db
from app.auth import get_current_user, get_approver_user
from app.audit import AuditService
from app.utils import get_ip_from_request

router = APIRouter()


@router.post("/", response_model=schemas.AccessRequest)
async def create_access_request(
    request_data: schemas.AccessRequestCreate,
    db: Session = Depends(get_db),
    request: Request = Request,
    current_user: dict = Depends(get_current_user)
):
    """Create new access request"""
    
    # Get or create user from Keycloak token
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    if not user:
        user_data = schemas.UserCreate(
            keycloak_id=current_user.get("sub"),
            username=current_user.get("preferred_username"),
            email=current_user.get("email"),
            first_name=current_user.get("given_name", ""),
            last_name=current_user.get("family_name", ""),
            role=schemas.UserRole.USER
        )
        user = crud.UserCRUD.get_or_create(db, current_user.get("sub"), user_data)
    
    # Create access request
    access_request = crud.AccessRequestCRUD.create(db, user.id, request_data)
    
    # Log action
    AuditService.log_request_created(
        db, user.id, access_request.id, access_request.request_number, request
    )
    
    return access_request


@router.get("/", response_model=schemas.SearchResults)
async def get_access_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    query: Optional[str] = Query(None),
    status: Optional[models.RequestStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get access requests with search"""
    
    # Get user
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Admins and approvers see all requests
    if "admin" in current_user.get("roles", []) or "approver" in current_user.get("roles", []):
        requests, total = crud.AccessRequestCRUD.search(db, query, status, skip, limit)
    else:
        # Regular users only see their own requests
        requests, total = crud.AccessRequestCRUD.search(db, query, status, skip, limit)
        requests = [r for r in requests if r.user_id == user.id]
        total = len(requests)
    
    return schemas.SearchResults(
        requests=requests,
        total=total,
        page=skip // limit,
        page_size=limit
    )


@router.get("/{request_id}", response_model=schemas.AccessRequest)
async def get_access_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific access request"""
    
    access_request = crud.AccessRequestCRUD.get_by_id(db, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check permissions
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    if user.id != access_request.user_id and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return access_request


@router.patch("/{request_id}", response_model=schemas.AccessRequest)
async def update_access_request(
    request_id: int,
    request_update: schemas.AccessRequestUpdate,
    db: Session = Depends(get_db),
    request: Request = Request,
    current_user: dict = Depends(get_current_user)
):
    """Update access request (only if in CREATED status)"""
    
    access_request = crud.AccessRequestCRUD.get_by_id(db, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    
    # Check permissions
    if user.id != access_request.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if request can be updated
    if access_request.status != models.RequestStatus.CREATED:
        raise HTTPException(status_code=400, detail="Can only update requests in CREATED status")
    
    updated = crud.AccessRequestCRUD.update(db, request_id, request_update)
    
    # Log action
    AuditService.log_action(
        db, user.id, "updated", "access_request",
        access_request.request_number,
        f"Updated access request",
        request, request_id
    )
    
    return updated


@router.post("/{request_id}/approve", response_model=schemas.AccessRequest)
async def approve_access_request(
    request_id: int,
    approval: schemas.AccessRequestApprove,
    db: Session = Depends(get_db),
    request: Request = Request,
    current_user: dict = Depends(get_approver_user())
):
    """Approve access request"""
    
    access_request = crud.AccessRequestCRUD.get_by_id(db, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    
    if access_request.status != models.RequestStatus.CREATED:
        raise HTTPException(status_code=400, detail="Can only approve requests in CREATED status")
    
    # First move to pending approval
    access_request.status = models.RequestStatus.PENDING_APPROVAL
    db.commit()
    
    # Then approve
    approved = crud.AccessRequestCRUD.approve(db, request_id, user.id, approval.approval_comment)
    
    # Log action
    AuditService.log_request_approved(
        db, user.id, request_id, access_request.request_number, request
    )
    
    return approved


@router.post("/{request_id}/reject", response_model=schemas.AccessRequest)
async def reject_access_request(
    request_id: int,
    rejection: schemas.AccessRequestReject,
    db: Session = Depends(get_db),
    request: Request = Request,
    current_user: dict = Depends(get_approver_user())
):
    """Reject access request"""
    
    access_request = crud.AccessRequestCRUD.get_by_id(db, request_id)
    if not access_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    user = crud.UserCRUD.get_by_keycloak_id(db, current_user.get("sub"))
    
    if access_request.status != models.RequestStatus.CREATED:
        raise HTTPException(status_code=400, detail="Can only reject requests in CREATED status")
    
    rejected = crud.AccessRequestCRUD.reject(db, request_id, user.id, rejection.rejection_reason)
    
    # Log action
    AuditService.log_request_rejected(
        db, user.id, request_id, access_request.request_number,
        rejection.rejection_reason, request
    )
    
    return rejected
