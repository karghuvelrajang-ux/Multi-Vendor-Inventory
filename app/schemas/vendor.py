from pydantic import BaseModel, Field

from app.models.enums import PlatformType


class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=128)
    platform_type: PlatformType = PlatformType.OTHER
    external_account_id: str | None = None


class VendorRead(BaseModel):
    id: int
    name: str
    slug: str
    platform_type: PlatformType
    external_account_id: str | None
    is_active: bool

    model_config = {"from_attributes": True}
