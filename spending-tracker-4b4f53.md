# Spending Tracker — Architecture & Implementation Plan

A full-stack personal spending tracker replacing the Google Sheets workflow, with a Python/FastAPI backend, Next.js frontend, PostgreSQL storage, CSV import, and AI-assisted categorization.

---

## Architecture

```
┌─────────────────────────────────────┐
│         Next.js Frontend            │
│  (React + TailwindCSS + shadcn/ui) │
│  - Dashboard with charts            │
│  - Editable transaction table        │
│  - CSV upload UI                     │
│  - Category management               │
└──────────────┬──────────────────────┘
               │ REST API
┌──────────────▼──────────────────────┐
│        FastAPI Backend              │
│  - Transaction CRUD                  │
│  - CSV parsing (pandas)              │
│  - AI categorization (OpenAI)        │
│  - Summary/analytics endpoints       │
└──────────────┬──────────────────────┘
               │ SQLAlchemy ORM
┌──────────────▼──────────────────────┐
│        PostgreSQL Database          │
│  - transactions                      │
│  - categories                        │
│  - accounts (bank, credit cards)     │
│  - category_rules                    │
│  - import_logs                       │
└─────────────────────────────────────┘
```

## Tech Stack

| Layer    | Technology                    | Why                                            |
|----------|-------------------------------|------------------------------------------------|
| Frontend | Next.js 14 + React 18        | Reliable, SSR, great ecosystem                 |
| Styling  | TailwindCSS + shadcn/ui      | Beautiful, consistent, fast to build            |
| Charts   | Recharts                      | Simple, React-native charting                  |
| Backend  | Python 3.11+ + FastAPI       | Fast, typed, excellent for CSV/data processing |
| ORM      | SQLAlchemy 2.0 + Alembic     | Mature ORM + migrations                        |
| Database | PostgreSQL                    | Robust, great for financial data               |
| AI       | OpenAI API (gpt-4o-mini)     | Cheap, accurate category suggestions           |
| CSV      | pandas                        | Robust CSV parsing for bank statements         |

## Database Schema (key tables)

- **categories** — id, name, type (expense/income), color, icon
- **accounts** — id, name, type (bank/credit_card/cash)
- **transactions** — id, date, description, display_name, amount, category_id, account_id, notes, is_reviewed, source, import_hash (dedup), timestamps
- **category_rules** — id, pattern, category_id, priority (for rule-based pre-categorization)
- **import_logs** — id, filename, account_id, rows_imported, duplicates_skipped, imported_at

## Project Structure

```
windsurf-project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # DB connection & session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic request/response
│   │   ├── routers/             # API route handlers
│   │   └── services/            # CSV parser, AI categorizer, analytics
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env
├── frontend/
│   ├── src/app/                 # Next.js pages
│   ├── src/components/          # UI components
│   ├── src/lib/                 # API client, utils
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml           # PostgreSQL
└── README.md
```

## Implementation Phases

### Phase 1 — Scaffolding & Database
1. Initialize FastAPI backend with project structure
2. Set up PostgreSQL via docker-compose
3. Define SQLAlchemy models + Alembic migrations
4. Seed default categories (Groceries, Rent, Salary, etc.)

### Phase 2 — Backend API
5. Transaction CRUD endpoints (list, create, update, delete)
6. Category & Account CRUD endpoints
7. CSV import endpoint — upload, parse with pandas, deduplicate, store
8. Analytics endpoints — monthly totals, category breakdowns

### Phase 3 — Frontend Dashboard
9. Initialize Next.js + TailwindCSS + shadcn/ui
10. Transaction table with inline editing (description, category)
11. CSV upload page with column mapping
12. Dashboard page with charts (Recharts): monthly spend, category breakdown, income vs expense

### Phase 4 — AI Categorization
13. OpenAI integration — on import, suggest categories for uncategorized transactions
14. "Accept/reject suggestion" UI in the transaction table

### Phase 5 — Historical Data & Polish
15. Import 2024–2026 Google Sheets data
16. Bulk operations (categorize, delete)
17. Export to CSV

## Prerequisites
- **Python 3.11+** and **Node.js 18+** installed
- **Docker** (for PostgreSQL) or a local/cloud PostgreSQL instance
- **OpenAI API key** (for Phase 4)
