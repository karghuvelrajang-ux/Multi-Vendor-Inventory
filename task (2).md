# Multi-Vendor Inventory Sync Engine

## Project Overview

Build a production-grade backend system called **Multi-Vendor Inventory Sync Engine** focused on solving real-world inventory consistency problems across multiple vendor platforms such as Shopify, Amazon, and supplier systems.

This project must demonstrate advanced backend engineering concepts including:

- Event-driven architecture
- Distributed background processing
- Inventory reconciliation
- Webhook handling
- Enterprise RBAC
- Vendor-scoped authorization
- Audit logging
- Async database architecture
- Queue systems
- Production-ready project structure

The implementation should feel like a real enterprise backend system rather than a tutorial CRUD application.

---

# Core Tech Stack

## Backend
- Python 3.13+
- FastAPI
- SQLModel
- SQLAlchemy Async
- PostgreSQL

## Async & Background Processing
- Celery
- RabbitMQ

## Authentication & Security
- JWT Authentication
- OAuth2 Login
- RBAC (Role-Based Access Control)

## Database & Migrations
- Alembic

## Validation & Serialization
- Pydantic v2

## Containerization
- Docker
- Docker Compose

## Testing
- Pytest
- HTTPX
- Factory Boy

## Utilities
- Faker
- python-jose
- passlib[bcrypt]
- Authlib

---

# Architecture Requirements

The architecture must follow clean modular enterprise backend practices.

Use:
- Repository Pattern
- Service Layer Architecture
- Dependency Injection
- Async-first implementation
- Proper separation of concerns

Avoid:
- monolithic routes
- business logic inside routers
- direct DB queries inside endpoints
- tightly coupled modules

---

# Final Folder Structure

```text
inventory-sync-engine/
├── app/
├── alembic/
├── tests/
├── scripts/
├── docker/
├── .env
├── docker-compose.yml
├── requirements.txt
├── README.md
└── alembic.ini
```

---

# Core Features

- Multi-vendor inventory synchronization
- Webhook-driven updates
- Automated reconciliation engine
- Event-driven architecture
- Enterprise RBAC
- Vendor-scoped authorization
- JWT Authentication
- OAuth2 Login
- Audit logging
- Celery background jobs
- RabbitMQ queue processing
- Alembic migrations
- Dockerized setup
- Seed data generation
- Integration & unit tests

---

# RBAC Roles

```python
class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    OPS_ADMIN = "OPS_ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    VENDOR_MANAGER = "VENDOR_MANAGER"
    AUDITOR = "AUDITOR"
```

---

# Seed Accounts

## SUPER_ADMIN
admin@inventorysync.com
Password123!

## OPS_ADMIN
ops@inventorysync.com
Password123!

## INVENTORY_MANAGER
inventory@inventorysync.com
Password123!

## VENDOR_MANAGER
vendor@inventorysync.com
Password123!

## AUDITOR
auditor@inventorysync.com
Password123!

---

# Docker Requirement

The system must fully run using:

```bash
docker compose up --build
```

---

# Engineering Quality Expectations

The project must:
- look production-grade
- follow modern Python practices
- use proper type hints
- use async architecture
- follow clean architecture
- contain recruiter-quality implementation
- avoid tutorial-level shortcuts
