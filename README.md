# Spending Tracker

A full-stack personal finance application with AI-powered transaction categorization, CSV import, and interactive analytics dashboard.

## Features

- 📊 **Interactive Dashboard** - Real-time charts and transaction overview
- 🏦 **Account Management** - Track multiple bank accounts, credit cards, and cash
- 📁 **Category Management** - Create custom categories with colors and icons
- 📄 **Flexible CSV Import** - Auto-detect columns or map them manually
- 🤖 **AI-Powered Categorization** - OpenAI or Claude integration for smart transaction categorization
- 📝 **Transaction Management** - Edit, categorize, and review transactions
- 📈 **Analytics & Reports** - Monthly summaries and category breakdowns

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **OpenAI/Claude API** - AI categorization
- **Pandas** - CSV processing

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - Modern UI components
- **Recharts** - Data visualization

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/annovi/spending-tracker.git
cd spending-tracker
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your AI provider configuration:

# For OpenAI (default):
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here

# For Claude:
AI_PROVIDER=claude
CLAUDE_API_KEY=your_claude_api_key_here
```

3. Start all services with Docker:
```bash
docker-compose up --build
```

4. The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- OpenAI API key

#### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/annovi/spending-tracker.git
cd spending-tracker
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings:

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/spending_tracker

# AI Provider Configuration
# Choose which AI provider to use: "openai" or "claude"
AI_PROVIDER=openai

# For OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# For Claude (alternative)
# AI_PROVIDER=claude
# CLAUDE_API_KEY=your_claude_api_key
# CLAUDE_MODEL=claude-3-haiku-20240307

# CORS
CORS_ORIGINS=http://localhost:3000
```

4. Start PostgreSQL (using Docker):
```bash
docker-compose up -d postgres
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. In a new terminal, set up the frontend:
```bash
cd frontend
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local if needed:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Testing

### Running Tests

The backend includes comprehensive unit tests covering:
- API endpoints
- CSV parsing logic
- AI categorization service
- Database models

To run all tests:

```bash
cd backend
pytest
```

To run tests with coverage report:

```bash
./run_tests.sh
```

Or manually:

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Test Structure

```
backend/tests/
├── conftest.py          # Test fixtures and configuration
├── test_api.py          # API endpoint tests
├── test_csv_parser.py   # CSV parsing tests
├── test_categorizer.py  # AI categorization tests
└── test_models.py       # Database model tests
```

### Adding New Tests

1. Create test files in the `tests/` directory with the `test_` prefix
2. Use the provided fixtures in `conftest.py`
3. Follow the naming conventions:
   - Test classes: `TestClassName`
   - Test functions: `test_function_name`

## API Documentation

Once the backend is running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

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
│   ├── Dockerfile           # Docker configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities
│   ├── Dockerfile           # Docker configuration
│   └── package.json         # Node dependencies
├── docs/
│   └── architecture.md      # Architecture diagrams
├── .env.example             # Environment variables template
└── docker-compose.yml       # All services configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.
