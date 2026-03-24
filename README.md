# Spending Tracker

A full-stack personal finance application with AI-powered transaction categorization, CSV import, and interactive analytics dashboard.

## Features

- **Interactive Dashboard** - Real-time charts and transaction overview
- **Account Management** - Track multiple bank accounts, credit cards, and cash
- **Category Management** - Create custom categories with colors and icons
- **Flexible CSV Import** - Auto-detect columns, manual mapping, or bank presets (TD Visa, Scotia, Amex)
- **Google Sheets** - Optional import/export via a Google service account
- **AI-Powered Categorization** - OpenAI or Claude integration for smart transaction categorization
- **Transaction Management** - Edit, categorize, and review transactions
- **Analytics & Reports** - Monthly summaries and category breakdowns

## Tech Stack

| Backend | Frontend |
|---------|----------|
| FastAPI | Next.js 14 |
| PostgreSQL | TypeScript |
| SQLAlchemy 2.0 | TailwindCSS |
| Alembic (migrations) | shadcn/ui |
| OpenAI / Claude API | Recharts |
| Pandas (CSV processing) | |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/annovi/spending-tracker.git
cd spending-tracker
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your AI provider:

```bash
# Choose "openai" or "claude"
AI_PROVIDER=openai

# OpenAI (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Claude (if using Claude)
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-haiku-20240307

# Optional: Google Sheets — see docs/google-sheets-setup.md for full guide
# GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
# GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id

# CORS — include your frontend origin (e.g. http://localhost:3001)
# CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Run the application

#### Option A: Docker (Recommended)

```bash
docker compose up --build
```

That's it. All services (Postgres, backend, frontend) start automatically. The backend container runs **`alembic upgrade head`** on each start so the database schema stays up to date (e.g. new columns like `cached_suggested_category_id`).

#### Option B: Manual Setup

**Prerequisites:** Python 3.11+, Node.js 18+, PostgreSQL 16+

**Start PostgreSQL** (via Docker, or use your local instance):

```bash
docker compose up -d postgres
```

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env   # Edit DATABASE_URL (host port 5433 if using compose Postgres)
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (in a separate terminal):

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Open the app

| Service | URL |
|---------|-----|
| Frontend (Docker Compose) | http://localhost:3001 |
| Frontend (`npm run dev` in `frontend/`) | http://localhost:3000 |
| Import / Export (same origin as frontend) | `/import` and `/export` (top nav) |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## Testing

The backend includes unit tests covering API endpoints, CSV parsing, AI categorization, and database models.

```bash
cd backend
pytest
```

With coverage report:

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

## Project Structure

```
spending-tracker/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Unit tests
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities
│   └── package.json
├── .env.example             # Environment variables template
└── docker-compose.yml
```

## Google Sheets Integration

The app can import transactions from (and export to) Google Sheets using a
service account. See **[docs/google-sheets-setup.md](docs/google-sheets-setup.md)**
for the full step-by-step guide covering:

- Creating a Google Cloud service account
- Sharing spreadsheets with the service account
- Expected spreadsheet format (Date, Description, Withdrawals/Deposits or Amount)
- Using the frontend UI or the API directly (`POST /google-sheets/import`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.
