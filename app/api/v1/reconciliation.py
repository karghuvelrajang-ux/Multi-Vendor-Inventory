from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import ensure_vendor_scope
from app.dependencies import get_db_session, require_roles
from app.events.dispatcher import dispatch_reconciliation
from app.models.enums import UserRole
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter()


class ReconciliationRequest(BaseModel):
    vendor_id: int | None = Field(
        default=None,
        description="Scope reconciliation to one vendor, or all if omitted",
    )


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_reconciliation(
    body: ReconciliationRequest,
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
    vendor_id = body.vendor_id
    if user.role == UserRole.VENDOR_MANAGER:
        vendor_id = vendor_id or user.vendor_id
        if vendor_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vendor_id is required unless your account is linked to a vendor.",
            )
    if vendor_id is not None:
        ensure_vendor_scope(user, vendor_id)
    audit = AuditService(session)
    task_id = dispatch_reconciliation(vendor_id)
    await audit.record(
        actor_user_id=user.id,
        action="reconciliation.enqueued",
        resource_type="reconciliation_run",
        resource_id=None,
        vendor_id=vendor_id,
        details={"celery_task_id": task_id},
    )
    return {"status": "queued", "celery_task_id": task_id}
