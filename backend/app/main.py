from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, chat, conversations, dashboard, knowledge, leads

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


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(leads.router)
