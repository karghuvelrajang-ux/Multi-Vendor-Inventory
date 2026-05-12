# Multi-Vendor Inventory Sync Engine

Production-style backend for inventory synchronization across vendors (Shopify, Amazon, supplier feeds), with async FastAPI, RBAC, webhooks, Celery workers, RabbitMQ, PostgreSQL, and audit logging.

## Quick start (Docker)

```bash
docker compose up --build
```

Apply demo data (accounts from the project brief):

```bash
docker compose exec api python scripts/seed.py
```

API base URL: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Seed accounts

| Role              | Email                     | Password      |
|-------------------|---------------------------|---------------|
| SUPER_ADMIN       | admin@inventorysync.com   | Password123!  |
| OPS_ADMIN         | ops@inventorysync.com     | Password123!  |
| INVENTORY_MANAGER | inventory@inventorysync.com | Password123! |
| VENDOR_MANAGER    | vendor@inventorysync.com | Password123! |
| AUDITOR           | auditor@inventorysync.com | Password123! |

### Obtain a JWT

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin@inventorysync.com&password=Password123!"
```

Use `Authorization: Bearer <token>` on protected routes.

### Google OAuth (optional)

Set `OAUTH_GOOGLE_CLIENT_ID`, `OAUTH_GOOGLE_CLIENT_SECRET`, and `OAUTH_REDIRECT_BASE_URL` (must match the authorized redirect URI in Google Cloud). Navigate to `/api/v1/auth/oauth/google/login`.

### Webhook HMAC test

Compute `HMAC-SHA256` over the raw JSON body using `WEBHOOK_HMAC_SECRET`, send as header `X-Inventory-Signature` (hex or `sha256=<hex>`).

## Stack

Python 3.13, FastAPI, SQLModel, SQLAlchemy asyncio + PostgreSQL, Celery + RabbitMQ, Alembic, JWT (`python-jose`), bcrypt passwords, Authlib (Google OIDC), Docker Compose.

## Tests

```bash
pip install -r requirements.txt
pytest
```

Health checks do not require a database; extend with integration tests pointed at PostgreSQL as needed.
