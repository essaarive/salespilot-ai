from collections.abc import Generator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

DEMO_TOKEN = "salespilot-demo-token"


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(authorization: str | None = Header(default=None)) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != DEMO_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
