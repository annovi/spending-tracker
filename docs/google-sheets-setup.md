# Google Sheets Import & Export

This guide walks through setting up Google Sheets integration so you can import
transactions from a spreadsheet (or export your data back to one).

---

## 1. Create a Google Cloud Service Account

You need a **service account** — a bot identity that the backend uses to read/write
your spreadsheets. No user login or OAuth consent screen is required.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Enable these two APIs:
   - **Google Sheets API**
   - **Google Drive API**
4. Go to **IAM & Admin → Service Accounts → Create Service Account**
5. Give it a name (e.g. `spending-tracker`) and click **Done**
6. Click the service account → **Keys** tab → **Add Key → Create new key → JSON**
7. Save the downloaded `.json` file somewhere safe (e.g. `~/.config/spending-tracker/service-account.json`)

## 2. Configure the Backend

Set the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable in your `.env` file.
You have two options:

**Option A — file path (recommended):**

```env
GOOGLE_SERVICE_ACCOUNT_JSON=/absolute/path/to/service-account.json
```

**Option B — inline JSON (useful for Docker / CI):**

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"...","client_email":"...@...iam.gserviceaccount.com",...}
```

Optionally, set a default Drive folder to browse:

```env
GOOGLE_DRIVE_FOLDER_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

Restart the backend after changing `.env`.

## 3. Share Your Spreadsheet with the Service Account

This is the step people forget. The service account is a separate Google identity —
it can only access spreadsheets that are explicitly shared with it.

1. Open your `.json` key file and find the `client_email` field (looks like `spending-tracker@your-project.iam.gserviceaccount.com`)
2. Open your Google Sheet in the browser
3. Click **Share** → paste the `client_email` → give it **Editor** access (needed for export; Viewer is enough for import-only)
4. Click **Send**

## 4. Find the Spreadsheet ID

The spreadsheet ID is in the URL:

```
https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                       This is the spreadsheet_id
```

## 5. Expected Spreadsheet Format

The importer reads the **first row as headers** and all subsequent rows as data.
It auto-detects columns using these conventions:

| Header name      | What it maps to  |
|------------------|------------------|
| `Date`           | Transaction date  |
| `Description`    | Transaction text  |
| `Amount`         | Signed amount (negative = expense) |
| `Withdrawals`    | Debit amount (alternative to Amount) |
| `Deposits`       | Credit amount (alternative to Amount) |

If your sheet has `Date`, `Description`, `Withdrawals`, `Deposits` columns — it works
out of the box. If it has `Date`, `Description`, `Amount` — that works too.

For other column names, the generic auto-detect (`detect_columns`) tries common
variations (date, desc, amount, debit, credit, withdrawal, deposit).

### Example sheet layout

| Date       | Description        | Withdrawals | Deposits |
|------------|--------------------|-------------|----------|
| 2025-01-15 | Grocery Store      | 87.50       |          |
| 2025-01-16 | Salary             |             | 3200.00  |
| 2025-01-17 | Netflix            | 15.99       |          |

## 6. Using the Frontend

Open **Import** (`/import`) or **Export** (`/export`) from the top navigation bar.

Once the backend is configured, the **Google Sheets import** section appears on the Import page, and **Google Sheets export** on the Export page.

### Import

1. (Optional) Enter a Drive **folder ID** and click **List spreadsheets in folder** to browse
2. Select a spreadsheet from the dropdown, or paste the **spreadsheet ID** directly
3. (Optional) Pick a **worksheet tab** from the dropdown (use **Load tabs** after pasting an ID), or type the tab name
4. (Optional) Select an **account** to tag the imported transactions
5. Click **Import from sheet**

The backend reads all rows, parses them, deduplicates by hash, auto-categorizes
with AI, and inserts into the database. You'll see a summary like:
`Imported 42, duplicates skipped 3`.

### Export

1. Enter the **spreadsheet ID** of the target sheet (must be shared with the service account)
2. Enter a **worksheet tab name** (the tab is created if it doesn't exist)
3. (Optional) Set a date range to export only a subset
4. Click **Export to sheet**

Exported columns: Date, Description, Category, Withdrawals, Deposits, Balance, Source.

## 7. Using the API Directly

You can also call the backend API without the frontend:

### Check status

```bash
curl http://localhost:8000/google-sheets/status
# {"configured": true, "has_default_folder": false}
```

### List spreadsheets in a folder

```bash
curl "http://localhost:8000/google-sheets/spreadsheets?folder_id=YOUR_FOLDER_ID"
# {"spreadsheets": [{"id": "1abc...", "name": "Bank Jan 2025"}, ...]}
```

### Import a spreadsheet

```bash
curl -X POST http://localhost:8000/google-sheets/import \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "worksheet_name": "January",
    "account_id": 1
  }'
# {"rows_imported": 42, "duplicates_skipped": 3}
```

| Field            | Required | Description |
|------------------|----------|-------------|
| `spreadsheet_id` | Yes      | From the sheet URL |
| `worksheet_name` | No       | Tab name; defaults to the first sheet |
| `account_id`     | No       | Links transactions to a specific account |

### Export to a spreadsheet

```bash
curl -X POST http://localhost:8000/google-sheets/export \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
    "worksheet_name": "Transactions",
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
  }'
# {"rows_written": 156}
```

| Field            | Required | Description |
|------------------|----------|-------------|
| `spreadsheet_id` | Yes      | Target sheet (must be Editor-shared with the service account) |
| `worksheet_name` | Yes      | Tab name; created automatically if missing |
| `date_from`      | No       | Filter start date (YYYY-MM-DD) |
| `date_to`        | No       | Filter end date (YYYY-MM-DD) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Google service account not configured" | Set `GOOGLE_SERVICE_ACCOUNT_JSON` in `.env` and restart the backend |
| "Failed to read spreadsheet" / 403 | Share the spreadsheet with the service account `client_email` |
| "Provide folder_id query parameter" | Pass `folder_id` when listing, or set `GOOGLE_DRIVE_FOLDER_ID` in `.env` |
| Import shows 0 rows | Check that the sheet has a header row and at least one data row |
| All rows are "duplicates skipped" | Those transactions were already imported (matched by date + description + amount hash) |
