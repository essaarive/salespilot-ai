# SalesPilot AI Backend

FastAPI 后端服务，包含认证、仪表盘、知识库、AI 对话、对话记录和客户线索接口。

## 创建虚拟环境

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 .env

```bash
cp .env.example .env
```

如果不配置 `DEEPSEEK_API_KEY`，系统会自动使用 mock 回复，方便本地演示。

AI 对话优先使用数据库中「模型设置」页面的默认配置。环境变量保留为 fallback，可配置 `AI_PROVIDER`、`AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL` 或各 Provider 专用变量。

## 认证说明

当前认证为演示版简化实现，默认账号为 `admin / admin123`，接口鉴权使用简单固定 token。该实现仅用于本地作品演示，不应直接用于生产环境。

生产化时应升级为 JWT 或服务端会话认证，使用 bcrypt/passlib 存储密码哈希，并通过环境变量或配置中心管理管理员账号、token 和密钥。

## 初始化数据库和种子数据

```bash
python -m app.seed
```

## 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

健康检查地址：

```text
http://localhost:8000/api/health
```
