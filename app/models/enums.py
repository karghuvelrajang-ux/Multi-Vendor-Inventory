from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    OPS_ADMIN = "OPS_ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    VENDOR_MANAGER = "VENDOR_MANAGER"
    AUDITOR = "AUDITOR"


class PlatformType(str, Enum):
    SHOPIFY = "SHOPIFY"
    AMAZON = "AMAZON"
    SUPPLIER = "SUPPLIER"
    OTHER = "OTHER"


class WebhookStatus(str, Enum):
    RECEIVED = "RECEIVED"
    QUEUED = "QUEUED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class SyncJobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
