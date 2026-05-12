from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    role: UserRole = UserRole.AUDITOR
    vendor_id: int | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: UserRole
    vendor_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}
