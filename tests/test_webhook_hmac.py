import hashlib
import hmac

from app.config import get_settings
from app.services.webhook_service import WebhookService


def test_verify_hmac_accepts_valid_signature() -> None:
    settings = get_settings()
    body = b'{"sku":"X","quantity_available":3}'
    digest = hmac.new(
        settings.webhook_hmac_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    assert WebhookService.verify_hmac(body, digest) is True


def test_verify_hmac_accepts_sha256_prefix() -> None:
    settings = get_settings()
    body = b"{}"
    digest = (
        "sha256="
        + hmac.new(
            settings.webhook_hmac_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    assert WebhookService.verify_hmac(body, digest) is True
