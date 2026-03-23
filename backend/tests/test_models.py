import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models import Account, Category, Transaction, ImportLog, CategoryRule


class TestAccountModel:
    """Test the Account model."""

    def test_create_account(self, db_session):
        """Test creating an account."""
        account = Account(
            name="Test Bank",
            type="bank"
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        assert account.id is not None
        assert account.name == "Test Bank"
        assert account.type == "bank"
        assert account.created_at is not None
        assert account.updated_at is not None

    def test_account_relationships(self, db_session, sample_account):
        """Test account relationships with transactions."""
        # Create a transaction for the account
        transaction = Transaction(
            date=date(2024, 1, 1),
            description="Test Transaction",
            amount=Decimal("100.00"),
            account_id=sample_account.id
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Test relationship
        assert len(sample_account.transactions) == 1
        assert sample_account.transactions[0].description == "Test Transaction"


class TestCategoryModel:
    """Test the Category model."""

    def test_create_category(self, db_session):
        """Test creating a category."""
        category = Category(
            name="Test Category",
            type="expense",
            color="#ff0000",
            icon="🛒"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.type == "expense"
        assert category.color == "#ff0000"
        assert category.icon == "🛒"

    def test_category_relationships(self, db_session, sample_category):
        """Test category relationships with transactions."""
        # Create a transaction for the category
        transaction = Transaction(
            date=date(2024, 1, 1),
            description="Test Transaction",
            amount=Decimal("100.00"),
            category_id=sample_category.id
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Test relationship
        assert len(sample_category.transactions) == 1
        assert sample_category.transactions[0].description == "Test Transaction"

    def test_category_rules_relationship(self, db_session, sample_category):
        """Test category relationship with rules."""
        rule = CategoryRule(
            pattern="*coffee*",
            category_id=sample_category.id,
            priority=1
        )
        db_session.add(rule)
        db_session.commit()
        
        # Test relationship
        assert len(sample_category.rules) == 1
        assert sample_category.rules[0].pattern == "*coffee*"


class TestTransactionModel:
    """Test the Transaction model."""

    def test_create_transaction(self, db_session, sample_category, sample_account):
        """Test creating a transaction."""
        transaction = Transaction(
            date=date(2024, 1, 1),
            description="Test Transaction",
            display_name="Custom Display Name",
            amount=Decimal("-100.50"),
            category_id=sample_category.id,
            account_id=sample_account.id,
            notes="Test notes",
            is_reviewed=True,
            source="manual",
            import_hash="test_hash"
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        
        assert transaction.id is not None
        assert transaction.date == date(2024, 1, 1)
        assert transaction.description == "Test Transaction"
        assert transaction.display_name == "Custom Display Name"
        assert transaction.amount == Decimal("-100.50")
        assert transaction.category_id == sample_category.id
        assert transaction.account_id == sample_account.id
        assert transaction.notes == "Test notes"
        assert transaction.is_reviewed is True
        assert transaction.source == "manual"
        assert transaction.import_hash == "test_hash"
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_transaction_relationships(self, db_session, sample_transactions):
        """Test transaction relationships."""
        transaction = sample_transactions[0]
        
        # Test relationships are loaded correctly
        assert transaction.category is not None
        assert transaction.account is not None
        assert transaction.category.name == "Test Category"
        assert transaction.account.name == "Test Bank Account"

    def test_transaction_defaults(self, db_session, sample_category, sample_account):
        """Test transaction default values."""
        transaction = Transaction(
            date=date(2024, 1, 1),
            description="Test",
            amount=Decimal("100.00"),
            category_id=sample_category.id,
            account_id=sample_account.id
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        
        assert transaction.display_name is None
        assert transaction.notes is None
        assert transaction.is_reviewed is False
        assert transaction.source == "manual"
        assert transaction.import_hash is None


class TestImportLogModel:
    """Test the ImportLog model."""

    def test_create_import_log(self, db_session, sample_account):
        """Test creating an import log."""
        import_log = ImportLog(
            filename="test.csv",
            account_id=sample_account.id,
            rows_imported=100,
            duplicates_skipped=5
        )
        db_session.add(import_log)
        db_session.commit()
        db_session.refresh(import_log)
        
        assert import_log.id is not None
        assert import_log.filename == "test.csv"
        assert import_log.account_id == sample_account.id
        assert import_log.rows_imported == 100
        assert import_log.duplicates_skipped == 5
        assert import_log.imported_at is not None

    def test_import_log_relationship(self, db_session, sample_account):
        """Test import log relationship with account."""
        import_log = ImportLog(
            filename="test.csv",
            account_id=sample_account.id,
            rows_imported=100,
            duplicates_skipped=0
        )
        db_session.add(import_log)
        db_session.commit()
        
        # Test relationship
        assert import_log.account is not None
        assert import_log.account.name == "Test Bank Account"


class TestCategoryRuleModel:
    """Test the CategoryRule model."""

    def test_create_category_rule(self, db_session, sample_category):
        """Test creating a category rule."""
        rule = CategoryRule(
            pattern="*amazon*",
            category_id=sample_category.id,
            priority=1
        )
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        
        assert rule.id is not None
        assert rule.pattern == "*amazon*"
        assert rule.category_id == sample_category.id
        assert rule.priority == 1
        assert rule.created_at is not None
        assert rule.updated_at is not None

    def test_category_rule_relationship(self, db_session, sample_category):
        """Test category rule relationship with category."""
        rule = CategoryRule(
            pattern="*coffee*",
            category_id=sample_category.id,
            priority=2
        )
        db_session.add(rule)
        db_session.commit()
        
        # Test relationship
        assert rule.category is not None
        assert rule.category.name == "Test Category"
