import pytest
from unittest.mock import patch, MagicMock

from app.services.categorizer import suggest_category


class TestCategorizer:
    """Test the AI categorizer service."""

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_success(self, mock_create):
        """Test successful category suggestion."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Groceries"))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Rent", "Entertainment", "Transport"]
        description = "Whole Foods Market purchase"
        
        result = suggest_category(description, categories)
        
        assert result == "Groceries"
        mock_create.assert_called_once()
        
        # Check the prompt was properly formatted
        call_args = mock_create.call_args
        assert "messages" in call_args.kwargs
        assert len(call_args.kwargs["messages"]) == 2

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_not_found(self, mock_create):
        """Test when AI suggests a category not in the list."""
        # Mock the OpenAI response with a category not in the list
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Unknown Category"))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Rent", "Entertainment"]
        description = "Some transaction"
        
        result = suggest_category(description, categories)
        
        assert result is None

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_empty_categories(self, mock_create):
        """Test with empty category list."""
        categories = []
        description = "Some transaction"
        
        result = suggest_category(description, categories)
        
        assert result is None
        mock_create.assert_not_called()

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_api_error(self, mock_create):
        """Test handling of OpenAI API errors."""
        # Mock an API error
        mock_create.side_effect = Exception("API Error")
        
        categories = ["Groceries", "Rent"]
        description = "Some transaction"
        
        result = suggest_category(description, categories)
        
        assert result is None

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_case_insensitive(self, mock_create):
        """Test that category matching is case insensitive."""
        # Mock the OpenAI response with different case
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="GROCERIES"))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Rent", "Entertainment"]
        description = "Whole Foods purchase"
        
        result = suggest_category(description, categories)
        
        assert result == "Groceries"

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_with_whitespace(self, mock_create):
        """Test handling of whitespace in AI response."""
        # Mock the OpenAI response with extra whitespace
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="  Groceries  "))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Rent", "Entertainment"]
        description = "Whole Foods purchase"
        
        result = suggest_category(description, categories)
        
        assert result == "Groceries"

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_description_variations(self, mock_create):
        """Test with various description formats."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Transport"))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Rent", "Transport", "Entertainment"]
        
        # Test different descriptions
        descriptions = [
            "Uber ride",
            "UBER TRIP",
            "Lyft - ride to airport",
            "Taxi fare"
        ]
        
        for desc in descriptions:
            result = suggest_category(desc, categories)
            assert result == "Transport"
            mock_create.assert_called()

    def test_suggest_category_empty_description(self):
        """Test with empty description."""
        categories = ["Groceries", "Rent"]
        
        # Empty string
        result = suggest_category("", categories)
        assert result is None
        
        # None
        result = suggest_category(None, categories)  # type: ignore
        assert result is None

    @patch('app.services.categorizer.client.chat.completions.create')
    def test_suggest_category_partial_match(self, mock_create):
        """Test when AI response partially matches a category."""
        # Mock response with partial match
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Grocery"))
        ]
        mock_create.return_value = mock_response
        
        categories = ["Groceries", "Grocery Store", "Rent"]
        description = "Food purchase"
        
        result = suggest_category(description, categories)
        
        # Should return None for partial match
        assert result is None
