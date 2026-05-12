from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import PlatformType

if TYPE_CHECKING:
    from app.models.inventory import InventoryItem
    from app.models.user import User
    from app.models.webhook import WebhookEvent


class Vendor(SQLModel, table=True):
    __tablename__ = "vendor"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    slug: str = Field(unique=True, index=True, max_length=128)
    platform_type: PlatformType = Field(default=PlatformType.OTHER)
    external_account_id: str | None = Field(default=None, max_length=255)
    credentials_encrypted: dict | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    users: list["User"] = Relationship(back_populates="vendor")
    inventory_items: list["InventoryItem"] = Relationship(back_populates="vendor")
    webhook_events: list["WebhookEvent"] = Relationship(back_populates="vendor")
