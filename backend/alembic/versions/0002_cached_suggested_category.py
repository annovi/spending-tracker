"""add cached_suggested_category_id on transactions

Revision ID: 0002_cached
Revises: 0001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_cached"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("cached_suggested_category_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_transactions_cached_suggested_category",
        "transactions",
        "categories",
        ["cached_suggested_category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_transactions_cached_suggested_category", "transactions", type_="foreignkey")
    op.drop_column("transactions", "cached_suggested_category_id")
