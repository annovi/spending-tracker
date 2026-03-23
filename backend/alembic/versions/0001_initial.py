"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    category_type = sa.Enum("expense", "income", name="categorytype")
    account_type = sa.Enum("bank", "credit_card", "cash", name="accounttype")

    category_type.create(op.get_bind(), checkfirst=True)
    account_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", category_type, nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False, server_default="#64748b"),
        sa.Column("icon", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_categories_id", "categories", ["id"])
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", account_type, nullable=False),
    )
    op.create_index("ix_accounts_id", "accounts", ["id"])
    op.create_index("ix_accounts_name", "accounts", ["name"], unique=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("display_name", sa.String(length=500), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_reviewed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="manual"),
        sa.Column("import_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])
    op.create_index("ix_transactions_date", "transactions", ["date"])
    op.create_index("ix_transactions_import_hash", "transactions", ["import_hash"])

    op.create_table(
        "category_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pattern", sa.String(length=200), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_category_rules_id", "category_rules", ["id"])

    op.create_table(
        "import_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("rows_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_import_logs_id", "import_logs", ["id"])


def downgrade() -> None:
    op.drop_index("ix_import_logs_id", table_name="import_logs")
    op.drop_table("import_logs")

    op.drop_index("ix_category_rules_id", table_name="category_rules")
    op.drop_table("category_rules")

    op.drop_index("ix_transactions_import_hash", table_name="transactions")
    op.drop_index("ix_transactions_date", table_name="transactions")
    op.drop_index("ix_transactions_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_accounts_name", table_name="accounts")
    op.drop_index("ix_accounts_id", table_name="accounts")
    op.drop_table("accounts")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_table("categories")

    sa.Enum(name="accounttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="categorytype").drop(op.get_bind(), checkfirst=True)
