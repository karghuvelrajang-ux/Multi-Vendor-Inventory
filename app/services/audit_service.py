from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._audit = AuditRepository(session)

    async def record(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        vendor_id: int | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            vendor_id=vendor_id,
            details=details,
            ip_address=ip_address,
        )
        await self._audit.add(log)
        await self._session.commit()
        return log

    async def list_recent(
        self, *, skip: int = 0, limit: int = 100, vendor_id: int | None = None
    ) -> list[AuditLog]:
        return await self._audit.recent(skip=skip, limit=limit, vendor_id=vendor_id)
