from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    async def issue_token_for_user(self, user: User) -> str:
        return create_access_token(subject=user.email)

    async def get_or_create_google_oauth_user(
        self, *, email: str, full_name: str | None
    ) -> User:
        existing = await self._users.get_by_email(email)
        if existing:
            return existing
        user = User(
            email=email,
            hashed_password=hash_password(f"oauth-google-{email}-unused"),
            full_name=full_name,
            role=UserRole.INVENTORY_MANAGER,
        )
        await self._users.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def register_internal_user(
        self, data: UserCreate, *, actor_role: UserRole
    ) -> User:
        if await self._users.get_by_email(str(data.email)):
            raise ValueError("Email already registered")
        if data.role == UserRole.SUPER_ADMIN and actor_role != UserRole.SUPER_ADMIN:
            raise PermissionError("Cannot assign SUPER_ADMIN")
        user = User(
            email=str(data.email),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
            vendor_id=data.vendor_id,
        )
        await self._users.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
