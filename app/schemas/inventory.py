from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=128)
    title: str | None = Field(default=None, max_length=512)
    quantity_available: int = Field(ge=0, default=0)
    quantity_reserved: int = Field(ge=0, default=0)
    external_product_id: str | None = None


class InventoryUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=512)
    quantity_available: int | None = Field(default=None, ge=0)
    quantity_reserved: int | None = Field(default=None, ge=0)
    external_product_id: str | None = None


class InventoryRead(BaseModel):
    id: int
    vendor_id: int
    sku: str
    title: str | None
    quantity_available: int
    quantity_reserved: int
    external_product_id: str | None
    version: int

    model_config = {"from_attributes": True}
