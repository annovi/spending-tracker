from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas.google_sheets import GoogleSheetExportBody, GoogleSheetImportBody
from ..services.google_sheets import (
    default_folder_configured,
    export_transactions_to_sheet,
    google_sheets_configured,
    list_spreadsheets_in_folder,
    list_worksheets,
    spreadsheet_rows_to_parsed,
)
from ..services.import_batch import import_parsed_transactions

router = APIRouter(prefix="/google-sheets", tags=["google-sheets"])


@router.get("/status")
def get_google_sheets_status():
    return {
        "configured": google_sheets_configured(),
        "has_default_folder": default_folder_configured(),
    }


@router.get("/spreadsheets")
def get_spreadsheets_in_folder(
    folder_id: str | None = Query(
        default=None,
        description="Google Drive folder ID; defaults to GOOGLE_DRIVE_FOLDER_ID when set",
    ),
):
    if not google_sheets_configured():
        raise HTTPException(status_code=503, detail="Google service account not configured")
    fid = (folder_id or "").strip() or settings.google_drive_folder_id.strip()
    if not fid:
        raise HTTPException(
            status_code=400,
            detail="Provide folder_id query parameter or set GOOGLE_DRIVE_FOLDER_ID",
        )
    try:
        return {"spreadsheets": list_spreadsheets_in_folder(fid)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/worksheets")
def get_worksheets(
    spreadsheet_id: str = Query(..., description="Google Spreadsheet ID"),
):
    if not google_sheets_configured():
        raise HTTPException(status_code=503, detail="Google service account not configured")
    try:
        return {"worksheets": list_worksheets(spreadsheet_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/import")
def import_from_google_sheet(
    body: GoogleSheetImportBody,
    db: Session = Depends(get_db),
):
    if not google_sheets_configured():
        raise HTTPException(status_code=503, detail="Google service account not configured")
    try:
        parsed = spreadsheet_rows_to_parsed(body.spreadsheet_id, body.worksheet_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read spreadsheet: {e}") from e
    label = body.worksheet_name or "sheet1"
    filename = f"google_sheet:{body.spreadsheet_id}:{label}"
    return import_parsed_transactions(db, parsed, filename, body.account_id)


@router.post("/export")
def export_to_google_sheet(
    body: GoogleSheetExportBody,
    db: Session = Depends(get_db),
):
    if not google_sheets_configured():
        raise HTTPException(status_code=503, detail="Google service account not configured")
    try:
        n = export_transactions_to_sheet(
            db,
            body.spreadsheet_id,
            body.worksheet_name,
            body.date_from,
            body.date_to,
        )
        return {"rows_written": n}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
