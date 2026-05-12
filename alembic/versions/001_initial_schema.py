"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-10

"""

from typing import Sequence, Union

from alembic import op
from sqlmodel import SQLModel

import app.models  # noqa: F401 — register metadata

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.drop_all(bind=bind)
