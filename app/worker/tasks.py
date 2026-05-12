from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.sync_engine import sync_engine
from app.models.enums import (
    ReconciliationStatus,
    SyncJobStatus,
    WebhookStatus,
)
from app.models.inventory import InventoryItem
from app.models.reconciliation import ReconciliationRun
from app.models.sync_job import SyncJob
from app.models.webhook import WebhookEvent
from app.worker.celery_app import celery_app


@celery_app.task(name="webhooks.process_event")
def process_webhook_event(webhook_event_id: int) -> dict:
    """Apply webhook payload to inventory (simplified vendor delta)."""
    with Session(sync_engine) as session:
        event = session.get(WebhookEvent, webhook_event_id)
        if event is None:
            return {"ok": False, "error": "event_not_found"}
        if event.status != WebhookStatus.QUEUED:
            return {"ok": True, "skipped": True}
        payload = event.payload or {}
        sku = payload.get("sku")
        qty = payload.get("quantity_available")
        reserved = payload.get("quantity_reserved", 0)
        title = payload.get("title")
        try:
            if sku is None or qty is None:
                raise ValueError("missing sku or quantity_available")
            stmt = select(InventoryItem).where(
                InventoryItem.vendor_id == event.vendor_id,
                InventoryItem.sku == str(sku),
            )
            row = session.exec(stmt).first()
            if row:
                row.quantity_available = int(qty)
                row.quantity_reserved = int(reserved)
                if title is not None:
                    row.title = str(title)
                row.version = row.version + 1
                session.add(row)
            else:
                session.add(
                    InventoryItem(
                        vendor_id=event.vendor_id,
                        sku=str(sku),
                        title=str(title) if title else None,
                        quantity_available=int(qty),
                        quantity_reserved=int(reserved),
                    )
                )
            event.status = WebhookStatus.PROCESSED
            event.processed_at = datetime.now(timezone.utc)
            session.add(event)
            session.commit()
            return {"ok": True, "vendor_id": event.vendor_id, "sku": sku}
        except Exception as exc:  # noqa: BLE001 — task boundary
            session.rollback()
            event = session.get(WebhookEvent, webhook_event_id)
            if event:
                event.status = WebhookStatus.FAILED
                event.error_message = str(exc)[:1024]
                session.add(event)
                session.commit()
            return {"ok": False, "error": str(exc)}


@celery_app.task(name="inventory.sync_vendor")
def run_inventory_sync(vendor_id: int) -> dict:
    """Simulated pull sync — marks job complete with placeholder summary."""
    with Session(sync_engine) as session:
        job = SyncJob(vendor_id=vendor_id, status=SyncJobStatus.RUNNING)
        session.add(job)
        session.commit()
        session.refresh(job)
        stmt = select(InventoryItem).where(InventoryItem.vendor_id == vendor_id)
        rows = session.exec(stmt).all()
        job.status = SyncJobStatus.COMPLETED
        job.summary = {"items_observed": len(rows), "simulated": True}
        job.finished_at = datetime.now(timezone.utc)
        session.add(job)
        session.commit()
        return {"ok": True, "job_id": job.id, "items_observed": len(rows)}


@celery_app.task(name="inventory.reconcile")
def run_reconciliation(vendor_id: int | None) -> dict:
    """Detect inventory inconsistencies (reserved vs available)."""
    with Session(sync_engine) as session:
        run = ReconciliationRun(
            vendor_id=vendor_id, status=ReconciliationStatus.RUNNING
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        stmt = select(InventoryItem)
        if vendor_id is not None:
            stmt = stmt.where(InventoryItem.vendor_id == vendor_id)
        rows = session.exec(stmt).all()
        discrepancies = []
        for row in rows:
            if row.quantity_reserved > row.quantity_available:
                discrepancies.append(
                    {
                        "sku": row.sku,
                        "vendor_id": row.vendor_id,
                        "issue": "reserved_exceeds_available",
                        "quantity_available": row.quantity_available,
                        "quantity_reserved": row.quantity_reserved,
                    }
                )
        run.status = ReconciliationStatus.COMPLETED
        run.discrepancies = discrepancies
        run.stats = {"checked": len(rows), "issues": len(discrepancies)}
        run.finished_at = datetime.now(timezone.utc)
        session.add(run)
        session.commit()
        return {"ok": True, "run_id": run.id, "issues": len(discrepancies)}
