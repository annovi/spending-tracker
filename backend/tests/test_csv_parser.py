import pytest
from datetime import date
from decimal import Decimal

from app.services.csv_parser_v2 import parse_transactions_csv_with_mapping, detect_columns, ColumnMapping


class TestCSVParser:
    """Test the CSV parser service (using csv_parser_v2)."""

    def test_parse_simple_csv(self, sample_csv_data):
        """Test parsing a simple CSV with amount column."""
        transactions, _ = parse_transactions_csv_with_mapping(sample_csv_data)
        
        assert len(transactions) == 3
        
        # Check first transaction
        assert transactions[0].date == date(2024, 1, 1)
        assert transactions[0].description == "Coffee Shop"
        assert transactions[0].amount == Decimal("-5.50")
        
        # Check second transaction
        assert transactions[1].date == date(2024, 1, 2)
        assert transactions[1].description == "Grocery Store"
        assert transactions[1].amount == Decimal("-125.30")
        
        # Check third transaction (income)
        assert transactions[2].date == date(2024, 1, 3)
        assert transactions[2].description == "Salary"
        assert transactions[2].amount == Decimal("200.00")

    def test_parse_csv_with_debit_credit(self, sample_csv_with_debit_credit):
        """Test parsing CSV with separate debit and credit columns."""
        transactions, _ = parse_transactions_csv_with_mapping(sample_csv_with_debit_credit)
        
        assert len(transactions) == 3
        
        # Debit transactions should be negative
        assert transactions[0].amount == Decimal("-5.50")
        assert transactions[1].amount == Decimal("-125.30")
        
        # Credit transactions should be positive
        assert transactions[2].amount == Decimal("2000.00")

    def test_parse_csv_missing_required_columns(self):
        """Test error when CSV is missing required columns."""
        csv_data = b"foo,bar\n1,2\n3,4"
        
        with pytest.raises(ValueError, match="CSV must have date and description columns"):
            parse_transactions_csv_with_mapping(csv_data)

    def test_parse_csv_empty_rows(self):
        """Test CSV with empty rows is handled correctly."""
        csv_data = b"date,description,amount\n2024-01-01,Valid,10.00\n, ,\n2024-01-02,Valid2,20.00"
        
        transactions, _ = parse_transactions_csv_with_mapping(csv_data)
        
        # Should skip empty rows
        assert len(transactions) == 2
        assert transactions[0].description == "Valid"
        assert transactions[1].description == "Valid2"

    def test_import_hash_consistency(self, sample_csv_data):
        """Test that import hashes are consistent for same data."""
        transactions1, _ = parse_transactions_csv_with_mapping(sample_csv_data)
        transactions2, _ = parse_transactions_csv_with_mapping(sample_csv_data)
        
        # Same data should produce same hashes
        assert transactions1[0].import_hash == transactions2[0].import_hash
        assert transactions1[1].import_hash == transactions2[1].import_hash


class TestCSVParserV2:
    """Test the enhanced CSV parser with column mapping."""

    def test_detect_columns(self):
        """Test automatic column detection."""
        import pandas as pd
        
        # Create test DataFrame
        data = {
            "Transaction Date": ["2024-01-01", "2024-01-02"],
            "Merchant": ["Coffee", "Groceries"],
            "Amount": ["-5.50", "-125.30"]
        }
        df = pd.DataFrame(data)
        
        mapping = detect_columns(df)
        
        assert mapping.date == "Transaction Date"
        assert mapping.description == "Merchant"
        assert mapping.amount == "Amount"
        assert mapping.debit is None
        assert mapping.credit is None

    def test_parse_with_mapping(self, sample_csv_data):
        """Test parsing with explicit column mapping."""
        mapping = ColumnMapping(
            date="date",
            description="description",
            amount="amount"
        )
        
        transactions, detected_mapping = parse_transactions_csv_with_mapping(
            sample_csv_data, 
            mapping
        )
        
        assert len(transactions) == 3
        assert transactions[0].description == "Coffee Shop"
        assert transactions[0].amount == Decimal("-5.50")
        assert detected_mapping.date == "date"

    def test_parse_with_auto_detection(self, sample_csv_data):
        """Test parsing with automatic column detection."""
        transactions, mapping = parse_transactions_csv_with_mapping(sample_csv_data)
        
        assert len(transactions) == 3
        assert mapping.date == "date"
        assert mapping.description == "description"
        assert mapping.amount == "amount"

    def test_parse_with_debit_credit_mapping(self, sample_csv_with_debit_credit):
        """Test parsing with debit/credit column mapping."""
        mapping = ColumnMapping(
            date="Date",
            description="Description",
            debit="Debit",
            credit="Credit"
        )
        
        transactions, _ = parse_transactions_csv_with_mapping(
            sample_csv_with_debit_credit,
            mapping
        )
        
        assert len(transactions) == 3
        assert transactions[0].amount == Decimal("-5.50")
        assert transactions[2].amount == Decimal("2000.00")

    def test_invalid_mapping_raises_error(self):
        """Test that invalid mapping raises appropriate error."""
        csv_data = b"date,description,amount\n2024-01-01,Test,10.00"
        
        # Missing date column
        mapping = ColumnMapping(
            description="description",
            amount="amount"
        )
        
        with pytest.raises(ValueError, match="CSV must have date and description columns"):
            parse_transactions_csv_with_mapping(csv_data, mapping)

    def test_skip_zero_amount_transactions(self):
        """Test that zero amount transactions are skipped."""
        csv_data = b"date,description,amount\n2024-01-01,Valid,10.00\n2024-01-02,Zero,0.00\n2024-01-03,Valid,20.00"
        
        transactions, _ = parse_transactions_csv_with_mapping(csv_data)
        
        # Should skip zero amount transaction
        assert len(transactions) == 2
        assert all(t.amount != 0 for t in transactions)
