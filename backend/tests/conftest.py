import pytest
import asyncio
from datetime import date
from decimal import Decimal
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base
from app.models import Account, Category, Transaction
from app.services.csv_parser import parse_transactions_csv
from app.services.csv_parser_v2 import parse_transactions_csv_with_mapping, ColumnMapping


# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_category(db_session) -> Category:
    """Create a sample category for testing."""
    category = Category(
        name="Test Category",
        type="expense",
        color="#ff0000"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_account(db_session) -> Account:
    """Create a sample account for testing."""
    account = Account(
        name="Test Bank Account",
        type="bank"
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def sample_transactions(db_session, sample_category, sample_account) -> list[Transaction]:
    """Create sample transactions for testing."""
    transactions = [
        Transaction(
            date=date(2024, 1, 1),
            description="Test Transaction 1",
            amount=Decimal("-100.50"),
            category_id=sample_category.id,
            account_id=sample_account.id,
            source="test",
            import_hash="hash1",
            is_reviewed=False
        ),
        Transaction(
            date=date(2024, 1, 2),
            description="Test Transaction 2",
            amount=Decimal("200.00"),
            category_id=sample_category.id,
            account_id=sample_account.id,
            source="test",
            import_hash="hash2",
            is_reviewed=True
        )
    ]
    
    for transaction in transactions:
        db_session.add(transaction)
    
    db_session.commit()
    return transactions


@pytest.fixture
def sample_csv_data() -> bytes:
    """Sample CSV data for testing."""
    csv_content = """date,description,amount
2024-01-01,Coffee Shop,-5.50
2024-01-02,Grocery Store,-125.30
2024-01-03,Salary,2000.00
"""
    return csv_content.encode('utf-8')


@pytest.fixture
def sample_csv_with_debit_credit() -> bytes:
    """Sample CSV data with separate debit/credit columns."""
    csv_content = """Date,Description,Debit,Credit
2024-01-01,Coffee Shop,5.50,
2024-01-02,Grocery Store,125.30,
2024-01-03,Salary,,2000.00
"""
    return csv_content.encode('utf-8')
