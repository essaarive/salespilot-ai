from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import AIModelConfig
from app.schemas import (
    AIModelConfigCreate,
    AIModelConfigCurrent,
    AIModelConfigOut,
    AIModelConfigTestResult,
    AIModelConfigUpdate,
    MessageResponse,
)
from app.services.ai_service import test_model_config

router = APIRouter(prefix="/api/ai-settings", tags=["ai-settings"], dependencies=[Depends(verify_token)])


def mask_api_key(api_key: str | None) -> tuple[bool, str]:
    if not api_key:
        return False, ""
    if len(api_key) <= 8:
        return True, "****"
    return True, f"{api_key[:3]}****{api_key[-4:]}"


def normalize_api_key(api_key: str | None) -> str:
    if not api_key:
        return ""

    normalized = api_key.strip()
    for _ in range(2):
        if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
            normalized = normalized[1:-1].strip()

    if normalized.lower().startswith("bearer "):
        normalized = normalized[7:].strip()

    for _ in range(2):
        if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
            normalized = normalized[1:-1].strip()

    return normalized


def to_config_out(config: AIModelConfig) -> AIModelConfigOut:
    masked, preview = mask_api_key(config.api_key)
    return AIModelConfigOut(
        id=config.id,
        provider=config.provider,
        name=config.name,
        base_url=config.base_url,
        model=config.model,
        enabled=config.enabled,
        is_default=config.is_default,
        api_key_masked=masked,
        api_key_preview=preview,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


def clear_default_flags(db: Session) -> None:
    db.query(AIModelConfig).update({AIModelConfig.is_default: False})


def ensure_default_is_enabled(is_default: bool, enabled: bool) -> None:
    if is_default and not enabled:
        raise HTTPException(status_code=400, detail="默认模型配置必须保持启用")


@router.get("/configs", response_model=list[AIModelConfigOut])
def list_configs(db: Session = Depends(get_db)) -> list[AIModelConfigOut]:
    configs = db.query(AIModelConfig).order_by(AIModelConfig.is_default.desc(), AIModelConfig.id.asc()).all()
    return [to_config_out(config) for config in configs]


@router.get("/current", response_model=AIModelConfigCurrent)
def get_current_config(db: Session = Depends(get_db)) -> AIModelConfigCurrent:
    config = (
        db.query(AIModelConfig)
        .filter(AIModelConfig.is_default.is_(True), AIModelConfig.enabled.is_(True))
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="暂无默认模型配置")
    return AIModelConfigCurrent(**to_config_out(config).model_dump())


@router.post("/configs", response_model=AIModelConfigOut)
def create_config(payload: AIModelConfigCreate, db: Session = Depends(get_db)) -> AIModelConfigOut:
    ensure_default_is_enabled(payload.is_default, payload.enabled)
    data = payload.model_dump()
    data["api_key"] = normalize_api_key(data.get("api_key"))
    config = AIModelConfig(**data)
    try:
        if config.is_default:
            clear_default_flags(db)
        db.add(config)
        db.commit()
        db.refresh(config)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建模型配置失败，请检查输入后重试") from exc
    return to_config_out(config)


@router.put("/configs/{config_id}", response_model=AIModelConfigOut)
def update_config(
    config_id: int,
    payload: AIModelConfigUpdate,
    db: Session = Depends(get_db),
) -> AIModelConfigOut:
    config = db.get(AIModelConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    data = payload.model_dump(exclude_unset=True)
    clear_api_key = bool(data.pop("clear_api_key", False))
    api_key = data.pop("api_key", None)
    target_is_default = data.get("is_default", config.is_default)
    target_enabled = data.get("enabled", config.enabled)

    if config.is_default and data.get("is_default") is False:
        raise HTTPException(status_code=400, detail="当前默认模型不能直接取消默认，请先将其他启用配置设为默认")
    ensure_default_is_enabled(bool(target_is_default), bool(target_enabled))

    if clear_api_key:
        config.api_key = ""
    else:
        normalized_api_key = normalize_api_key(api_key)
        if normalized_api_key:
            config.api_key = normalized_api_key

    if data.get("is_default") is True:
        clear_default_flags(db)

    for key, value in data.items():
        if value is not None:
            setattr(config, key, value)

    try:
        db.commit()
        db.refresh(config)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新模型配置失败，请检查输入后重试") from exc
    return to_config_out(config)


@router.post("/configs/{config_id}/set-default", response_model=AIModelConfigOut)
def set_default_config(config_id: int, db: Session = Depends(get_db)) -> AIModelConfigOut:
    config = db.get(AIModelConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    if not config.enabled:
        raise HTTPException(status_code=400, detail="未启用的模型配置不能设为默认")

    try:
        clear_default_flags(db)
        config.is_default = True
        db.commit()
        db.refresh(config)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="设置默认模型失败，请稍后重试") from exc
    return to_config_out(config)


@router.post("/configs/{config_id}/test", response_model=AIModelConfigTestResult)
async def test_config(config_id: int, db: Session = Depends(get_db)) -> AIModelConfigTestResult:
    config = db.get(AIModelConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    success, message = await test_model_config(config)
    return AIModelConfigTestResult(
        success=success,
        message=message,
        provider=config.provider,
        model=config.model,
    )


@router.delete("/configs/{config_id}", response_model=MessageResponse)
def delete_config(config_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    config = db.get(AIModelConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    if config.is_default:
        raise HTTPException(status_code=400, detail="默认模型配置不允许删除，请先切换默认配置")
    if db.query(AIModelConfig).count() <= 1:
        raise HTTPException(status_code=400, detail="至少需要保留一个模型配置")

    try:
        db.delete(config)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除模型配置失败，请稍后重试") from exc
    return MessageResponse(message="删除成功")
