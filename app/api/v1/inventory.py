from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import ensure_vendor_scope
from app.dependencies import get_db_session, require_roles
from app.events.dispatcher import dispatch_inventory_sync_job
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/vendor/{vendor_id}", response_model=list[InventoryRead])
async def list_inventory(
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
    skip: int = 0,
    limit: int = Query(default=100, le=500),
) -> list[InventoryRead]:
    ensure_vendor_scope(user, vendor_id)
    inventory_service = InventoryService(session)
    rows = await inventory_service.list_vendor_inventory(
        vendor_id, skip=skip, limit=limit
    )
    return [InventoryRead.model_validate(r) for r in rows]


@router.put("/vendor/{vendor_id}/sku/{sku}", response_model=InventoryRead)
async def upsert_inventory(
    vendor_id: int,
    sku: str,
    payload: InventoryCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.OPS_ADMIN,
                UserRole.INVENTORY_MANAGER,
                UserRole.VENDOR_MANAGER,
            )
        ),
    ],
) -> InventoryRead:
    ensure_vendor_scope(user, vendor_id)
    if payload.sku != sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU must match path parameter",
        )
    inventory_service = InventoryService(session)
    audit = AuditService(session)
    item = await inventory_service.upsert_item(
        vendor_id,
        sku=sku,
        title=payload.title,
        quantity_available=payload.quantity_available,
        quantity_reserved=payload.quantity_reserved,
        external_product_id=payload.external_product_id,
    )
    await audit.record(
        actor_user_id=user.id,
        action="inventory.upsert",
        resource_type="inventory_item",
        resource_id=str(item.id),
        vendor_id=vendor_id,
        details={"sku": item.sku},
    )
    return InventoryRead.model_validate(item)


@router.patch("/vendor/{vendor_id}/sku/{sku}", response_model=InventoryRead)
async def patch_inventory(
    vendor_id: int,
    sku: str,
    payload: InventoryUpdate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.OPS_ADMIN,
                UserRole.INVENTORY_MANAGER,
                UserRole.VENDOR_MANAGER,
            )
        ),
    ],
) -> InventoryRead:
    ensure_vendor_scope(user, vendor_id)
    inventory_service = InventoryService(session)
    audit = AuditService(session)
    item = await inventory_service.patch_item(
        vendor_id,
        sku,
        title=payload.title,
        quantity_available=payload.quantity_available,
        quantity_reserved=payload.quantity_reserved,
        external_product_id=payload.external_product_id,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found"
        )
    await audit.record(
        actor_user_id=user.id,
        action="inventory.patch",
        resource_type="inventory_item",
        resource_id=str(item.id),
        vendor_id=vendor_id,
        details={"sku": item.sku},
    )
    return InventoryRead.model_validate(item)


@router.post("/vendor/{vendor_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_vendor_sync(
    vendor_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.OPS_ADMIN,
                UserRole.INVENTORY_MANAGER,
                UserRole.VENDOR_MANAGER,
            )
        ),
    ],
) -> dict[str, str | None]:
    ensure_vendor_scope(user, vendor_id)
    audit = AuditService(session)
    task_id = dispatch_inventory_sync_job(vendor_id)
    await audit.record(
        actor_user_id=user.id,
        action="inventory.sync_enqueued",
        resource_type="vendor",
        resource_id=str(vendor_id),
        vendor_id=vendor_id,
        details={"celery_task_id": task_id},
    )
    return {"status": "queued", "celery_task_id": task_id}
