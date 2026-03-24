"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Databases bootstrapped with SQLAlchemy create_all() may already have these types.
    # create_table() would emit CREATE TYPE again unless we use create_type=False.
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
                CREATE TYPE categorytype AS ENUM ('expense', 'income');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
        )
    )
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
                CREATE TYPE accounttype AS ENUM ('bank', 'credit_card', 'cash');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
        )
    )

    category_type = postgresql.ENUM(
        "expense", "income", name="categorytype", create_type=False
    )
    account_type = postgresql.ENUM(
        "bank", "credit_card", "cash", name="accounttype", create_type=False
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", category_type, nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False, server_default="#64748b"),
        sa.Column("icon", sa.String(length=50), nullable=True),
        if_not_exists=True,
    )
    op.create_index("ix_categories_id", "categories", ["id"], if_not_exists=True)
    op.create_index(
        "ix_categories_name", "categories", ["name"], unique=True, if_not_exists=True
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", account_type, nullable=False),
        if_not_exists=True,
    )
    op.create_index("ix_accounts_id", "accounts", ["id"], if_not_exists=True)
    op.create_index(
        "ix_accounts_name", "accounts", ["name"], unique=True, if_not_exists=True
    )

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
        if_not_exists=True,
    )
    op.create_index("ix_transactions_id", "transactions", ["id"], if_not_exists=True)
    op.create_index("ix_transactions_date", "transactions", ["date"], if_not_exists=True)
    op.create_index(
        "ix_transactions_import_hash", "transactions", ["import_hash"], if_not_exists=True
    )

    op.create_table(
        "category_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pattern", sa.String(length=200), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        if_not_exists=True,
    )
    op.create_index("ix_category_rules_id", "category_rules", ["id"], if_not_exists=True)

    op.create_table(
        "import_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("rows_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        if_not_exists=True,
    )
    op.create_index("ix_import_logs_id", "import_logs", ["id"], if_not_exists=True)


def downgrade() -> None:
    op.drop_index("ix_import_logs_id", table_name="import_logs", if_exists=True)
    op.drop_table("import_logs", if_exists=True)

    op.drop_index("ix_category_rules_id", table_name="category_rules", if_exists=True)
    op.drop_table("category_rules", if_exists=True)

    op.drop_index("ix_transactions_import_hash", table_name="transactions", if_exists=True)
    op.drop_index("ix_transactions_date", table_name="transactions", if_exists=True)
    op.drop_index("ix_transactions_id", table_name="transactions", if_exists=True)
    op.drop_table("transactions", if_exists=True)

    op.drop_index("ix_accounts_name", table_name="accounts", if_exists=True)
    op.drop_index("ix_accounts_id", table_name="accounts", if_exists=True)
    op.drop_table("accounts", if_exists=True)

    op.drop_index("ix_categories_name", table_name="categories", if_exists=True)
    op.drop_index("ix_categories_id", table_name="categories", if_exists=True)
    op.drop_table("categories", if_exists=True)

    sa.Enum(name="accounttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="categorytype").drop(op.get_bind(), checkfirst=True)
