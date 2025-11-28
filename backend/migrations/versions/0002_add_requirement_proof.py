"""add requirement proof fields

Revision ID: 0002_add_requirement_proof
Revises: 0001_initial
Create Date: 2025-01-15 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_add_requirement_proof"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("requirements", sa.Column("proof_url", sa.String(length=500), nullable=True))
    op.add_column(
        "requirements",
        sa.Column(
            "proof_submitted_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("requirements", "proof_submitted_by")
    op.drop_column("requirements", "proof_url")
