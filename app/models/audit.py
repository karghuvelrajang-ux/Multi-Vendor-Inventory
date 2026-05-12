from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    actor_user_id: int | None = Field(
        default=None, foreign_key="user_account.id", index=True
    )
    action: str = Field(max_length=128, index=True)
    resource_type: str = Field(max_length=128, index=True)
    resource_id: str | None = Field(default=None, max_length=64)
    vendor_id: int | None = Field(default=None, foreign_key="vendor.id", index=True)
    details: dict | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    ip_address: str | None = Field(default=None, max_length=64)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
