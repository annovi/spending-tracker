from pydantic import BaseModel
from typing import Optional


class ColumnMapping(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[str] = None
    debit: Optional[str] = None
    credit: Optional[str] = None


class CsvPreview(BaseModel):
    columns: list[str]
    sample_rows: list[dict[str, str]]
    detected_mapping: Optional[ColumnMapping] = None


class CsvImportRequest(BaseModel):
    columns: list[str]
    mapping: ColumnMapping
