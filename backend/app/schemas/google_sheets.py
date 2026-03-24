from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class GoogleSheetImportBody(BaseModel):
    spreadsheet_id: str = Field(..., min_length=1)
    worksheet_name: str | None = None
    account_id: int | None = None


class GoogleSheetExportBody(BaseModel):
    spreadsheet_id: str = Field(..., min_length=1)
    worksheet_name: str = Field(..., min_length=1)
    date_from: date | None = None
    date_to: date | None = None
