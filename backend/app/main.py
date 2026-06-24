from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db
from app.routers import ai_settings, auth, chat, company_settings, conversations, dashboard, documents, knowledge, leads
from app.services.company_service import ensure_company_settings

app = FastAPI(title="SalesPilot AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        ensure_company_settings(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(knowledge.router)
app.include_router(documents.router)
app.include_router(ai_settings.router)
app.include_router(company_settings.router)
app.include_router(chat.router)
app.include_router(chat.public_router)
app.include_router(conversations.router)
app.include_router(leads.router)
