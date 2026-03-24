# Spending Tracker Architecture

## System Overview

The Spending Tracker is a full-stack personal finance application with AI-powered categorization, built with a FastAPI backend, Next.js 14 frontend, and PostgreSQL database. It supports CSV import (generic and bank-specific), Google Sheets import/export, and optional AI categorization via OpenAI or Claude.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js 14 Dashboard]
        CSVUp[CSV Upload]
        GSheets[Google Sheets Sync]
        Trans[Transaction Table]
        Charts[Recharts Charts]
        CatMgr[Category Manager]
        AccMgr[Account Manager]
        Review[Category Review Panel]
        ApiClient[api.ts Fetch Client]
    end

    subgraph "API Layer"
        CORS[CORS Middleware]
        API[FastAPI App]
        ImportR["/imports"]
        GSheetsR["/google-sheets"]
        TransR["/transactions"]
        CatR["/categories"]
        RulesR["/category-rules"]
        AccR["/accounts"]
        AnalR["/analytics"]
    end

    subgraph "Service Layer"
        CSVParser[csv_parser_v2<br/>Column Detect & Parse]
        BankParser[bank_parsers<br/>TD · Scotia · Amex]
        ImportBatch[import_batch<br/>Deduplicate & Save]
        Categorizer[categorizer<br/>Rules + AI Fallback]
        Seed[seed<br/>Default Categories]
        GSheetsService[google_sheets<br/>Import & Export]
    end

    subgraph "Data Layer"
        ORM[SQLAlchemy 2.0 Models]
        DB[(PostgreSQL 16)]
        Alembic[Alembic Migrations]
    end

    subgraph "External Services"
        OpenAI[OpenAI API<br/>gpt-4o-mini]
        Claude[Anthropic API<br/>Claude 3 Haiku]
        GApi[Google Sheets API]
    end

    UI --> ApiClient
    CSVUp --> ApiClient
    GSheets --> ApiClient
    Trans --> ApiClient
    Charts --> ApiClient
    CatMgr --> ApiClient
    AccMgr --> ApiClient
    Review --> ApiClient

    ApiClient -- "HTTP / REST" --> CORS --> API

    API --> ImportR
    API --> GSheetsR
    API --> TransR
    API --> CatR
    API --> RulesR
    API --> AccR
    API --> AnalR

    ImportR --> CSVParser
    ImportR --> BankParser
    ImportR --> ImportBatch
    GSheetsR --> GSheetsService
    GSheetsService --> ImportBatch

    CSVParser --> ImportBatch
    BankParser --> ImportBatch
    ImportBatch --> Categorizer
    ImportBatch --> ORM

    TransR --> ORM
    CatR --> ORM
    RulesR --> ORM
    AccR --> ORM
    AnalR --> ORM

    Categorizer -.-> OpenAI
    Categorizer -.-> Claude
    GSheetsService -.-> GApi

    ORM --> DB
    Alembic --> DB

    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e9
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec

    class UI,CSVUp,GSheets,Trans,Charts,CatMgr,AccMgr,Review,ApiClient frontend
    class CORS,API,ImportR,GSheetsR,TransR,CatR,RulesR,AccR,AnalR api
    class CSVParser,BankParser,ImportBatch,Categorizer,Seed,GSheetsService service
    class ORM,DB,Alembic data
    class OpenAI,Claude,GApi external
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        Dashboard[Dashboard Page]
        TransTable[Transaction Table]
        CategoryMgr[Category Manager]
        AccountMgr[Account Manager]
        CSVUpload[CSV Upload Advanced]
        GSheetsSync[Google Sheets Sync]
        Charts[Analytics Charts]
        ReviewPanel[Category Review Panel]
    end

    subgraph "Backend Routers"
        TransRouter["/transactions"]
        CatRouter["/categories"]
        RulesRouter["/category-rules"]
        AccRouter["/accounts"]
        ImportRouter["/imports"]
        GSheetsRouter["/google-sheets"]
        AnalyticsRouter["/analytics"]
    end

    Dashboard --> TransTable
    Dashboard --> CSVUpload
    Dashboard --> GSheetsSync
    Dashboard --> Charts
    Dashboard --> ReviewPanel

    TransTable --> TransRouter
    CategoryMgr --> CatRouter
    CategoryMgr --> RulesRouter
    AccountMgr --> AccRouter
    CSVUpload --> ImportRouter
    GSheetsSync --> GSheetsRouter
    Charts --> AnalyticsRouter
    ReviewPanel --> TransRouter

    classDef component fill:#e3f2fd
    classDef module fill:#f1f8e9

    class Dashboard,TransTable,CategoryMgr,AccountMgr,CSVUpload,GSheetsSync,Charts,ReviewPanel component
    class TransRouter,CatRouter,RulesRouter,AccRouter,ImportRouter,GSheetsRouter,AnalyticsRouter module
```

## Data Flow

### CSV Import

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Parser
    participant Categorizer
    participant DB

    User->>Frontend: Upload CSV file
    Frontend->>API: POST /imports/csv/preview
    API->>Parser: csv_parser_v2.detect_columns()
    Parser->>API: Columns + sample rows
    API->>Frontend: Return preview & detected mapping
    Frontend->>User: Show column mapping UI

    alt Manual mapping
        User->>Frontend: Adjust column mapping
        Frontend->>API: POST /imports/csv/with-mapping
    else Bank preset (TD, Scotia, Amex)
        User->>Frontend: Select bank format
        Frontend->>API: POST /imports/csv/bank
        API->>Parser: bank_parsers.parse_bank_csv()
    else Auto-detect
        User->>Frontend: Click quick import
        Frontend->>API: POST /imports/csv
    end

    API->>Parser: Parse to ParsedTransaction list
    Parser->>API: Parsed rows with import_hash

    loop Each transaction
        API->>DB: Check import_hash for duplicate
        alt New transaction
            API->>Categorizer: suggest_category(description)
            Categorizer->>DB: Match CategoryRule patterns
            alt No rule match & AI configured
                Categorizer->>Categorizer: Call OpenAI or Claude
            end
            Categorizer->>API: Suggested category
            API->>DB: INSERT transaction
        else Duplicate
            API->>API: Skip (increment duplicate count)
        end
    end

    API->>DB: INSERT ImportLog
    API->>Frontend: {rows_imported, duplicates_skipped}
    Frontend->>User: Show import results
```

### Google Sheets Import

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant GSheets as Google Sheets API
    participant ImportBatch
    participant DB

    User->>Frontend: Enter spreadsheet ID
    Frontend->>API: GET /google-sheets/spreadsheets
    API->>GSheets: List spreadsheets in folder
    GSheets->>API: Spreadsheet list
    API->>Frontend: Available spreadsheets

    User->>Frontend: Select sheet & import
    Frontend->>API: POST /google-sheets/import
    API->>GSheets: Read spreadsheet rows
    GSheets->>API: Row data
    API->>ImportBatch: import_parsed_transactions()
    ImportBatch->>DB: Deduplicate & store
    API->>Frontend: Import results
```

### Dashboard View

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB

    User->>Frontend: Open dashboard
    Frontend->>API: GET /transactions
    Frontend->>API: GET /analytics/summary
    Frontend->>API: GET /analytics/categories
    Frontend->>API: GET /categories
    Frontend->>API: GET /accounts
    API->>DB: Query data
    DB->>API: Results
    API->>Frontend: JSON responses
    Frontend->>User: Render charts, tables, metrics
```

## Database Schema

```mermaid
erDiagram
    ACCOUNTS {
        int id PK
        string name UK
        enum type "bank | credit_card | cash"
    }

    CATEGORIES {
        int id PK
        string name UK
        enum type "expense | income"
        string color
        string icon
    }

    CATEGORY_RULES {
        int id PK
        string pattern
        int category_id FK
        int priority
    }

    TRANSACTIONS {
        int id PK
        date date
        string description
        string display_name
        decimal amount
        int category_id FK
        int account_id FK
        string notes
        boolean is_reviewed
        string source
        string import_hash
        timestamp created_at
        timestamp updated_at
    }

    IMPORT_LOGS {
        int id PK
        string filename
        int account_id FK
        int rows_imported
        int duplicates_skipped
        timestamp imported_at
    }

    ACCOUNTS ||--o{ TRANSACTIONS : "has many"
    CATEGORIES ||--o{ TRANSACTIONS : "has many"
    CATEGORIES ||--o{ CATEGORY_RULES : "has many"
    ACCOUNTS ||--o{ IMPORT_LOGS : "has many"
```

## Import Pipeline

All import paths (CSV upload, bank presets, Google Sheets, bulk CLI script) converge on a single shared pipeline:

```mermaid
flowchart LR
    CSV[CSV Upload] --> P1[csv_parser_v2]
    Bank[Bank Preset] --> P2[bank_parsers]
    GS[Google Sheets] --> P3[google_sheets service]
    CLI[bulk_import_csv.py] --> P1 & P2

    P1 --> IB[import_batch<br/>import_parsed_transactions]
    P2 --> IB
    P3 --> IB

    IB --> Dedup{Check import_hash}
    Dedup -- new --> Cat[categorizer<br/>Rules → AI fallback]
    Cat --> DB[(PostgreSQL)]
    Dedup -- duplicate --> Skip[Skip]
    IB --> Log[ImportLog]
    Log --> DB
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with React 18 (App Router)
- **Styling**: TailwindCSS + shadcn/ui components
- **Charts**: Recharts
- **Language**: TypeScript
- **State Management**: React hooks (useState, useEffect, useMemo)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (sync engine)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **CSV Processing**: Pandas
- **AI Integration**: OpenAI API (gpt-4o-mini) or Anthropic Claude (claude-3-haiku)

### Database
- **Primary**: PostgreSQL 16
- **Driver**: psycopg v3 (`postgresql+psycopg://`)
- **Containerized**: Docker with named volume for persistence

### Infrastructure
- **Orchestration**: Docker Compose (Postgres + backend + frontend)
- **API Documentation**: Auto-generated OpenAPI/Swagger at `/docs`
- **CORS**: Configured for frontend origins
- **Ports**: Backend `:8000`, Frontend `:3001` (Docker) / `:3000` (local dev), Postgres `:5433` (host) / `:5432` (internal)

## Key Features

1. **Flexible CSV Import**
   - Auto-detect column mappings
   - Manual column mapping with preview
   - Bank-specific presets (TD Visa, Scotia Visa, Scotia Bank, Amex)
   - Bulk CLI import for historical data (`backend/scripts/bulk_import_csv.py`)

2. **Google Sheets Integration**
   - Import transactions from Google Sheets
   - Export transactions to Google Sheets
   - Browse spreadsheets in a configured Drive folder

3. **AI-Powered Categorization**
   - Rule-based matching first (regex/substring patterns via CategoryRule)
   - AI fallback via OpenAI or Claude (configurable via `AI_PROVIDER`)
   - Bulk review and apply workflow

4. **Interactive Dashboard**
   - Monthly income/expense trend charts
   - Category breakdown visualization
   - Inline transaction editing
   - Responsive design

5. **Data Management**
   - Category CRUD with colors and icons
   - Account management (bank, credit card, cash)
   - Category rules with priority ordering
   - Import deduplication via SHA-256 hash

## Security Considerations

- CORS restricted to configured frontend origins
- Input validation on all endpoints via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- File upload restrictions (CSV only, server-side validation)
- Environment-based configuration (secrets via `.env`, never committed)
- Single-user design; see `docs/authentication.md` for multi-user guidance
