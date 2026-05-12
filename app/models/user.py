from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class User(SQLModel, table=True):
    __tablename__ = "user_account"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=320)
    hashed_password: str = Field(max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.AUDITOR)
    vendor_id: int | None = Field(default=None, foreign_key="vendor.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    vendor: Vendor | None = Relationship(back_populates="users")
