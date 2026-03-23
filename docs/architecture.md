# Spending Tracker Architecture

## System Overview

The Spending Tracker is a full-stack personal finance application with AI-powered categorization, built with FastAPI backend and Next.js frontend.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js Dashboard]
        Comp[React Components]
        Charts[Recharts Visualizations]
    end
    
    subgraph "API Layer"
        API[FastAPI REST API]
        CORS[CORS Middleware]
    end
    
    subgraph "Service Layer"
        CSV[CSV Parser Service]
        AI[AI Categorization Service]
        Analytics[Analytics Service]
    end
    
    subgraph "Data Layer"
        ORM[SQLAlchemy 2.0]
        DB[(PostgreSQL)]
        Migrations[Alembic Migrations]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Files[CSV Files]
    end
    
    UI --> API
    Comp --> API
    Charts --> API
    
    API --> CSV
    API --> AI
    API --> Analytics
    
    CSV --> Files
    AI --> OpenAI
    
    API --> ORM
    ORM --> DB
    Migrations --> DB
    
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e9
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec
    
    class UI,Comp,Charts frontend
    class API,CORS api
    class CSV,AI,Analytics service
    class ORM,DB,Migrations data
    class OpenAI,Files external
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        Dashboard[Dashboard Page]
        TransTable[Transaction Table]
        CategoryMgr[Category Manager]
        AccountMgr[Account Manager]
        CSVUpload[CSV Upload]
        Charts[Analytics Charts]
        ReviewPanel[Category Review Panel]
    end
    
    subgraph "Backend Modules"
        AuthRouter[/auth]
        TransRouter[/transactions]
        CatRouter[/categories]
        AccRouter[/accounts]
        ImportRouter[/imports]
        AnalyticsRouter[/analytics]
    end
    
    Dashboard --> TransTable
    Dashboard --> CSVUpload
    Dashboard --> Charts
    Dashboard --> ReviewPanel
    
    TransTable --> TransRouter
    CategoryMgr --> CatRouter
    AccountMgr --> AccRouter
    CSVUpload --> ImportRouter
    Charts --> AnalyticsRouter
    ReviewPanel --> TransRouter
    
    classDef component fill:#e3f2fd
    classDef module fill:#f1f8e9
    
    class Dashboard,TransTable,CategoryMgr,AccountMgr,CSVUpload,Charts,ReviewPanel component
    class AuthRouter,TransRouter,CatRouter,AccRouter,ImportRouter,AnalyticsRouter module
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AI
    participant DB
    
    User->>Frontend: Upload CSV
    Frontend->>API: POST /imports/csv/preview
    API->>Frontend: Return columns & preview
    Frontend->>User: Show column mapping UI
    User->>Frontend: Map columns
    Frontend->>API: POST /imports/csv/with-mapping
    API->>API: Parse CSV
    API->>AI: Suggest categories
    AI->>API: Return suggestions
    API->>DB: Store transactions
    API->>Frontend: Import success
    Frontend->>User: Show import results
    
    User->>Frontend: View dashboard
    Frontend->>API: GET /transactions, /analytics/summary
    API->>DB: Query data
    DB->>API: Return transactions
    API->>Frontend: JSON data
    Frontend->>User: Display charts & tables
```

## Database Schema

```mermaid
erDiagram
    ACCOUNTS {
        int id PK
        string name
        enum type
        timestamp created_at
        timestamp updated_at
    }
    
    CATEGORIES {
        int id PK
        string name
        enum type
        string color
        string icon
        timestamp created_at
        timestamp updated_at
    }
    
    CATEGORY_RULES {
        int id PK
        string pattern
        int category_id FK
        int priority
        timestamp created_at
        timestamp updated_at
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

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with React 18
- **Styling**: TailwindCSS + shadcn/ui components
- **Charts**: Recharts
- **TypeScript**: Full type safety
- **State Management**: React hooks

### Backend
- **Framework**: FastAPI with Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic
- **AI Integration**: OpenAI API (gpt-4o-mini)

### Database
- **Primary**: PostgreSQL
- **Connection**: psycopg v3
- **Docker**: Containerized development environment

### Infrastructure
- **API Documentation**: Auto-generated OpenAPI/Swagger
- **CORS**: Configured for frontend
- **File Upload**: Multipart form data
- **Error Handling**: Comprehensive error responses

## Key Features

1. **CSV Import with Column Mapping**
   - Auto-detect column mappings
   - Preview before import
   - Flexible mapping interface

2. **AI-Powered Categorization**
   - OpenAI integration
   - Bulk review and apply
   - Learning from user corrections

3. **Interactive Dashboard**
   - Real-time charts
   - Inline editing
   - Responsive design

4. **Data Management**
   - Category CRUD operations
   - Account management
   - Transaction history

## Security Considerations

- CORS configured for frontend origin
- Input validation on all endpoints
- SQL injection prevention via ORM
- File upload restrictions (CSV only)
- Environment-based configuration
