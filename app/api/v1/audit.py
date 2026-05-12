from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import ensure_vendor_scope
from app.dependencies import get_db_session, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(UserRole.SUPER_ADMIN, UserRole.OPS_ADMIN, UserRole.AUDITOR)
        ),
    ],
    vendor_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
) -> list[AuditLogRead]:
    if vendor_id is not None:
        ensure_vendor_scope(user, vendor_id)
    audit_service = AuditService(session)
    rows = await audit_service.list_recent(skip=skip, limit=limit, vendor_id=vendor_id)
    return [AuditLogRead.model_validate(r) for r in rows]
