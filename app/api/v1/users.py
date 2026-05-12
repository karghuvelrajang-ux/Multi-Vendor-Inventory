from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    actor: Annotated[
        User, Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.OPS_ADMIN))
    ],
) -> User:
    auth_service = AuthService(session)
    audit = AuditService(session)
    try:
        user = await auth_service.register_internal_user(payload, actor_role=actor.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    await audit.record(
        actor_user_id=actor.id,
        action="user.create",
        resource_type="user",
        resource_id=str(user.id),
        details={"email": user.email, "role": user.role.value},
    )
    return user
