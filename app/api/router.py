from fastapi import APIRouter

from app.api.v1 import (
    audit,
    auth,
    health,
    inventory,
    reconciliation,
    users,
    vendors,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(
    reconciliation.router, prefix="/reconciliation", tags=["reconciliation"]
)
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
