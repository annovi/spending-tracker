import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient


class TestCategoriesAPI:
    """Test the categories API endpoints."""

    def test_list_categories_empty(self, client: TestClient):
        """Test listing categories when none exist."""
        response = client.get("/categories")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_category(self, client: TestClient):
        """Test creating a new category."""
        category_data = {
            "name": "Test Category",
            "type": "expense",
            "color": "#ff0000",
            "icon": "🛒"
        }
        
        response = client.post("/categories", json=category_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Category"
        assert data["type"] == "expense"
        assert data["color"] == "#ff0000"
        assert data["icon"] == "🛒"
        assert "id" in data

    def test_create_duplicate_category(self, client: TestClient):
        """Test creating a duplicate category raises error."""
        category_data = {
            "name": "Test Category",
            "type": "expense"
        }
        
        # Create first category
        client.post("/categories", json=category_data)
        
        # Try to create duplicate
        response = client.post("/categories", json=category_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_category(self, client: TestClient, sample_category):
        """Test updating an existing category."""
        update_data = {
            "name": "Updated Category",
            "color": "#00ff00"
        }
        
        response = client.patch(f"/categories/{sample_category.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Category"
        assert data["color"] == "#00ff00"
        assert data["type"] == sample_category.type  # Unchanged

    def test_delete_category(self, client: TestClient, sample_category):
        """Test deleting a category."""
        response = client.delete(f"/categories/{sample_category.id}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        # Verify it's deleted
        response = client.get("/categories")
        assert response.json() == []


class TestAccountsAPI:
    """Test the accounts API endpoints."""

    def test_list_accounts_empty(self, client: TestClient):
        """Test listing accounts when none exist."""
        response = client.get("/accounts")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_account(self, client: TestClient):
        """Test creating a new account."""
        account_data = {
            "name": "Test Bank",
            "type": "bank"
        }
        
        response = client.post("/accounts", json=account_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Bank"
        assert data["type"] == "bank"
        assert "id" in data

    def test_create_duplicate_account(self, client: TestClient):
        """Test creating a duplicate account raises error."""
        account_data = {
            "name": "Test Bank",
            "type": "bank"
        }
        
        # Create first account
        client.post("/accounts", json=account_data)
        
        # Try to create duplicate
        response = client.post("/accounts", json=account_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_account(self, client: TestClient, sample_account):
        """Test updating an existing account."""
        update_data = {
            "name": "Updated Bank",
            "type": "credit_card"
        }
        
        response = client.patch(f"/accounts/{sample_account.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Bank"
        assert data["type"] == "credit_card"

    def test_delete_account(self, client: TestClient, sample_account):
        """Test deleting an account."""
        response = client.delete(f"/accounts/{sample_account.id}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestTransactionsAPI:
    """Test the transactions API endpoints."""

    def test_list_transactions_empty(self, client: TestClient):
        """Test listing transactions when none exist."""
        response = client.get("/transactions")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_transactions_with_data(self, client: TestClient, sample_transactions):
        """Test listing transactions with sample data."""
        response = client.get("/transactions")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["description"] == "Test Transaction 1"
        assert data[1]["description"] == "Test Transaction 2"

    def test_update_transaction(self, client: TestClient, sample_transactions):
        """Test updating a transaction."""
        transaction = sample_transactions[0]
        update_data = {
            "display_name": "Updated Display Name",
            "category_id": transaction.category_id,
            "is_reviewed": True
        }
        
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["display_name"] == "Updated Display Name"
        assert data["is_reviewed"] is True

    def test_get_recategorization_suggestions(self, client: TestClient, sample_transactions):
        """Test getting recategorization suggestions."""
        response = client.get("/transactions/review/suggestions")
        assert response.status_code == 200
        
        # Should return only unreviewed transactions
        data = response.json()
        assert len(data) == 1  # Only one transaction is not reviewed
        assert data[0]["transaction_id"] == sample_transactions[0].id

    def test_apply_bulk_recategorization(self, client: TestClient, sample_transactions):
        """Test applying bulk recategorization."""
        # Create a new category to reassign to
        new_category = {
            "name": "New Category",
            "type": "expense"
        }
        cat_response = client.post("/categories", json=new_category)
        new_cat_id = cat_response.json()["id"]
        
        bulk_data = {
            "items": [
                {
                    "transaction_id": sample_transactions[0].id,
                    "category_id": new_cat_id
                }
            ]
        }
        
        response = client.post("/transactions/review/apply", json=bulk_data)
        assert response.status_code == 200
        assert response.json()["updated"] == 1
        
        # Verify the transaction was updated
        trans_response = client.get(f"/transactions/{sample_transactions[0].id}")
        assert trans_response.json()["category_id"] == new_cat_id
        assert trans_response.json()["is_reviewed"] is True


class TestImportsAPI:
    """Test the imports API endpoints."""

    def test_csv_preview(self, client: TestClient, sample_csv_data):
        """Test CSV preview endpoint."""
        files = {"file": ("test.csv", sample_csv_data, "text/csv")}
        response = client.post("/imports/csv/preview", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "columns" in data
        assert "sample_rows" in data
        assert "detected_mapping" in data
        assert "date" in data["detected_mapping"]
        assert "description" in data["detected_mapping"]
        assert "amount" in data["detected_mapping"]

    def test_csv_import_with_mapping(self, client: TestClient, sample_csv_data, sample_account):
        """Test CSV import with column mapping."""
        import json
        
        files = {
            "file": ("test.csv", sample_csv_data, "text/csv")
        }
        data = {
            "mapping": json.dumps({
                "date": "date",
                "description": "description",
                "amount": "amount"
            }),
            "account_id": str(sample_account.id)
        }
        
        response = client.post("/imports/csv/with-mapping", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "rows_imported" in result
        assert "duplicates_skipped" in result
        assert result["rows_imported"] == 3

    def test_csv_import_invalid_file_type(self, client: TestClient):
        """Test CSV import with invalid file type."""
        files = {"file": ("test.txt", b"not a csv", "text/plain")}
        response = client.post("/imports/csv", files=files)
        
        assert response.status_code == 400
        assert "Only CSV files are supported" in response.json()["detail"]


class TestAnalyticsAPI:
    """Test the analytics API endpoints."""

    def test_monthly_summary(self, client: TestClient, sample_transactions):
        """Test monthly summary endpoint."""
        response = client.get("/analytics/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # Check that summary calculations are correct
        summary = data[0]
        assert "month" in summary
        assert "income" in summary
        assert "expense" in summary
        assert "net" in summary

    def test_category_breakdown(self, client: TestClient, sample_transactions):
        """Test category breakdown endpoint."""
        response = client.get("/analytics/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # Check structure
        breakdown = data[0]
        assert "category" in breakdown
        assert "total" in breakdown
        assert "transaction_count" in breakdown
