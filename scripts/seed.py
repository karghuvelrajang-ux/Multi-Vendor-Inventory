"""Seed core vendors, RBAC users from task spec, and demo inventory."""

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.enums import PlatformType, UserRole
from app.models.inventory import InventoryItem
from app.models.user import User
from app.models.vendor import Vendor


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing_admin = await session.execute(
            select(User).where(User.email == "admin@inventorysync.com")
        )
        if existing_admin.scalar_one_or_none():
            print("Seed skipped: admin@inventorysync.com already exists.")
            return

        shopify = Vendor(
            name="Demo Shopify Store",
            slug="demo-shopify",
            platform_type=PlatformType.SHOPIFY,
            external_account_id="shopify-demo-001",
        )
        amazon = Vendor(
            name="Demo Amazon Seller",
            slug="demo-amazon",
            platform_type=PlatformType.AMAZON,
            external_account_id="amazon-demo-001",
        )
        session.add(shopify)
        session.add(amazon)
        await session.flush()

        users_spec = [
            ("admin@inventorysync.com", UserRole.SUPER_ADMIN, None),
            ("ops@inventorysync.com", UserRole.OPS_ADMIN, None),
            ("inventory@inventorysync.com", UserRole.INVENTORY_MANAGER, None),
            ("vendor@inventorysync.com", UserRole.VENDOR_MANAGER, shopify.id),
            ("auditor@inventorysync.com", UserRole.AUDITOR, None),
        ]
        pwd = hash_password("Password123!")
        for email, role, vendor_id in users_spec:
            session.add(
                User(
                    email=email,
                    hashed_password=pwd,
                    role=role,
                    vendor_id=vendor_id,
                    full_name=email.split("@")[0].replace(".", " ").title(),
                )
            )

        session.add_all(
            [
                InventoryItem(
                    vendor_id=shopify.id,
                    sku="SKU-DEMO-1",
                    title="Demo Product One",
                    quantity_available=120,
                    quantity_reserved=5,
                    external_product_id="gid://shopify/Product/1001",
                ),
                InventoryItem(
                    vendor_id=amazon.id,
                    sku="AMZ-ITEM-42",
                    title="Amazon Demo SKU",
                    quantity_available=80,
                    quantity_reserved=10,
                    external_product_id="B00DEMO42",
                ),
                InventoryItem(
                    vendor_id=shopify.id,
                    sku="BAD-RESERVED",
                    title="Reserved mismatch demo",
                    quantity_available=2,
                    quantity_reserved=5,
                    external_product_id=None,
                ),
            ]
        )

        await session.commit()
        print("Seed completed: vendors, users, inventory inserted.")


if __name__ == "__main__":
    asyncio.run(seed())
