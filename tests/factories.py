"""Factory Boy factories for tests and seed-style demos."""

import factory

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"synthetic{n}@inventorysync.com")
    hashed_password = factory.LazyFunction(lambda: hash_password("Password123!"))
    full_name = factory.Faker("name")
    role = UserRole.INVENTORY_MANAGER
    vendor_id = None
    is_active = True
