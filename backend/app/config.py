from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/spending_tracker"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    claude_api_key: str = ""
    claude_model: str = "claude-3-haiku-20240307"
    ai_provider: str = "openai"  # Options: "openai", "claude"
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    # Google Sheets: JSON file path, or inline JSON object string (starts with "{")
    google_service_account_json: str = ""
    google_drive_folder_id: str = ""


settings = Settings()
