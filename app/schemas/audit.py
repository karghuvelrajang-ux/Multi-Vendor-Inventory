from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    resource_type: str
    resource_id: str | None
    vendor_id: int | None
    details: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
