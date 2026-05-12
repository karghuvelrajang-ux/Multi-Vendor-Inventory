def dispatch_inventory_sync_job(vendor_id: int) -> str | None:
    from app.worker.tasks import run_inventory_sync

    async_result = run_inventory_sync.delay(vendor_id)
    return async_result.id


def dispatch_webhook_processing(webhook_event_id: int) -> str | None:
    from app.worker.tasks import process_webhook_event

    async_result = process_webhook_event.delay(webhook_event_id)
    return async_result.id


def dispatch_reconciliation(vendor_id: int | None = None) -> str | None:
    from app.worker.tasks import run_reconciliation

    async_result = run_reconciliation.delay(vendor_id)
    return async_result.id
