from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ReconciliationStatus

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class ReconciliationRun(SQLModel, table=True):
    __tablename__ = "reconciliation_run"

    id: int | None = Field(default=None, primary_key=True)
    vendor_id: int | None = Field(default=None, foreign_key="vendor.id", index=True)
    status: ReconciliationStatus = Field(default=ReconciliationStatus.PENDING)
    discrepancies: list | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    stats: dict | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    celery_task_id: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    vendor: Vendor | None = Relationship()
