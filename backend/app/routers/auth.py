from fastapi import APIRouter, HTTPException

from app.deps import DEMO_TOKEN
from app.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if payload.username == "admin" and payload.password == "admin123":
        return LoginResponse(token=DEMO_TOKEN, username="admin", role="admin")
    raise HTTPException(status_code=401, detail="用户名或密码错误")
