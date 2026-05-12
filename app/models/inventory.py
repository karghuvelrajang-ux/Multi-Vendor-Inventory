from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class InventoryItem(SQLModel, table=True):
    __tablename__ = "inventory_item"
    __table_args__ = (
        UniqueConstraint("vendor_id", "sku", name="uq_inventory_vendor_sku"),
    )

    id: int | None = Field(default=None, primary_key=True)
    vendor_id: int = Field(foreign_key="vendor.id", index=True)
    sku: str = Field(index=True, max_length=128)
    title: str | None = Field(default=None, max_length=512)
    quantity_available: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    external_product_id: str | None = Field(default=None, max_length=255)
    extra: dict | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    version: int = Field(default=1)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
    )

    vendor: Vendor | None = Relationship(back_populates="inventory_items")
