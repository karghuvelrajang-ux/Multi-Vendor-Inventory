from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import WebhookStatus

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class WebhookEvent(SQLModel, table=True):
    __tablename__ = "webhook_event"

    id: int | None = Field(default=None, primary_key=True)
    vendor_id: int = Field(foreign_key="vendor.id", index=True)
    topic: str = Field(max_length=128)
    payload: dict = Field(sa_column=Column(JSONB, nullable=False))
    signature_valid: bool = Field(default=False)
    status: WebhookStatus = Field(default=WebhookStatus.RECEIVED)
    error_message: str | None = Field(default=None, max_length=1024)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    processed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    vendor: Vendor | None = Relationship(back_populates="webhook_events")
