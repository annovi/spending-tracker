import pytest
from unittest.mock import MagicMock, patch

from app.services.categorizer import suggest_category


@pytest.fixture
def categorizer_db(db_session):
    """Fresh DB with no category rules (AI path when API key is set)."""
    return db_session


class TestCategorizer:
    """Test the AI categorizer service."""

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_success(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Groceries"))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Rent", "Entertainment", "Transport"]
        result = suggest_category("Whole Foods Market purchase", categories, categorizer_db)

        assert result == "Groceries"
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert "messages" in call_args.kwargs
        assert len(call_args.kwargs["messages"]) == 2

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_not_found(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Unknown Category"))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Rent", "Entertainment"]
        result = suggest_category("Some transaction", categories, categorizer_db)

        assert result is None

    @patch("app.services.categorizer.settings")
    def test_suggest_category_empty_categories(self, mock_settings, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = ""

        result = suggest_category("Some transaction", [], categorizer_db)

        assert result is None

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_api_error(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        categories = ["Groceries", "Rent"]
        result = suggest_category("Some transaction", categories, categorizer_db)

        assert result is None

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_case_insensitive(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="GROCERIES"))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Rent", "Entertainment"]
        result = suggest_category("Whole Foods purchase", categories, categorizer_db)

        assert result is None

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_with_whitespace(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="  Groceries  "))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Rent", "Entertainment"]
        result = suggest_category("Whole Foods purchase", categories, categorizer_db)

        assert result == "Groceries"

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_description_variations(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Transport"))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Rent", "Transport", "Entertainment"]
        for desc in ["Uber ride", "UBER TRIP", "Lyft - ride to airport", "Taxi fare"]:
            result = suggest_category(desc, categories, categorizer_db)
            assert result == "Transport"

    @patch("app.services.categorizer.settings")
    def test_suggest_category_empty_description(self, mock_settings, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = ""

        assert suggest_category("", ["Groceries", "Rent"], categorizer_db) is None

    @patch("app.services.categorizer.OpenAI")
    @patch("app.services.categorizer.settings")
    def test_suggest_category_partial_match(self, mock_settings, mock_openai_cls, categorizer_db):
        mock_settings.ai_provider = "openai"
        mock_settings.openai_api_key = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Grocery"))]
        mock_client.chat.completions.create.return_value = mock_response

        categories = ["Groceries", "Grocery Store", "Rent"]
        result = suggest_category("Food purchase", categories, categorizer_db)

        assert result is None
