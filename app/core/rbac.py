from fastapi import HTTPException, status

from app.models.enums import UserRole
from app.models.user import User


def ensure_vendor_scope(user: User, vendor_id: int | None) -> None:
    if user.role == UserRole.SUPER_ADMIN:
        return
    if vendor_id is None:
        return
    if user.role == UserRole.VENDOR_MANAGER:
        if user.vendor_id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendor scope violation.",
            )
