from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import ensure_vendor_scope
from app.dependencies import get_db_session, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.vendor import VendorCreate, VendorRead
from app.services.audit_service import AuditService
from app.services.vendor_service import VendorService

router = APIRouter()


@router.get("/", response_model=list[VendorRead])
async def list_vendors(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.OPS_ADMIN,
                UserRole.INVENTORY_MANAGER,
                UserRole.AUDITOR,
                UserRole.VENDOR_MANAGER,
            )
        ),
    ],
    skip: int = 0,
    limit: int = 100,
) -> list[VendorRead]:
    vendor_service = VendorService(session)
    if user.role == UserRole.VENDOR_MANAGER:
        if user.vendor_id is None:
            return []
        v = await vendor_service.get(user.vendor_id)
        return [VendorRead.model_validate(v)] if v else []
    vendors = await vendor_service.list_active(skip=skip, limit=limit)
    return [VendorRead.model_validate(v) for v in vendors]


@router.post("/", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    payload: VendorCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.OPS_ADMIN))
    ],
) -> VendorRead:
    vendor_service = VendorService(session)
    audit = AuditService(session)
    try:
        vendor = await vendor_service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    await audit.record(
        actor_user_id=user.id,
        action="vendor.create",
        resource_type="vendor",
        resource_id=str(vendor.id),
        details={"slug": vendor.slug},
    )
    return VendorRead.model_validate(vendor)


@router.get("/{vendor_id}", response_model=VendorRead)
async def get_vendor(
    vendor_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.OPS_ADMIN,
                UserRole.INVENTORY_MANAGER,
                UserRole.AUDITOR,
                UserRole.VENDOR_MANAGER,
            )
        ),
    ],
) -> VendorRead:
    ensure_vendor_scope(user, vendor_id)
    vendor_service = VendorService(session)
    vendor = await vendor_service.get(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )
    return VendorRead.model_validate(vendor)
