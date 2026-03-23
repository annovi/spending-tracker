from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .models import Account, Category, CategoryRule, ImportLog, Transaction  # noqa: F401
from .routers import accounts_router, analytics_router, categories_router, imports_router, transactions_router
from .services import seed_default_categories

app = FastAPI(title="Spending Tracker API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    from .database import SessionLocal

    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(categories_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(imports_router)
app.include_router(analytics_router)
