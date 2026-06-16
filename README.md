# SalesPilot AI / 智销助手

SalesPilot AI / 智销助手是一个面向中小企业的 AI 智能获客客服系统 Demo，用于展示全栈开发、AI 模型接入、知识库问答、客户意向识别、线索沉淀和企业 SaaS 后台设计能力。

> 本项目定位为学习、作品集和面试演示 Demo，不是生产可直接上线版本。认证、权限、密钥管理、日志审计、限流和数据安全仍需生产化加固。

## 核心闭环

```text
客户官网
  -> 公开咨询
  -> AI 回复
  -> 意向识别
  -> 高意向线索沉淀
  -> 后台跟进
```

客户可以从官网进入公开咨询页，提交姓名、联系方式和问题。系统会基于企业知识库生成 AI 回复，识别咨询类型、意向等级和问题范围，并在 high 意向时自动生成客户线索，方便销售在后台继续跟进。

## 功能模块

- 客户官网首页：展示产品能力、使用流程、适用场景、套餐方案和 FAQ。
- 公开咨询页：无需登录即可提交咨询，复用 AI 对话、RAG 检索、意向识别和线索沉淀逻辑。
- 后台登录：演示版固定管理员账号 `admin / admin123`。
- 仪表盘：统计知识库数量、今日咨询、高意向线索、总线索和最近咨询。
- 知识库管理：支持新增、编辑、删除、搜索、分类筛选和状态展示。
- AI 对话测试：模拟客户咨询，展示 AI 回复、命中知识、意向识别、问题范围和回复来源。
- 对话记录：保存完整客户问题、AI 回复、意向类型、意向等级和创建时间。
- 客户线索：管理客户姓名、联系方式、需求、意向等级、跟进状态和备注。
- 模型设置：后台配置 DeepSeek、OpenAI、通义千问、智谱 GLM、Ollama、火山方舟和自定义兼容 API。
- Mock fallback：未配置 API Key、模型请求失败或响应异常时，自动使用演示回复，保证流程可跑通。

## 技术栈

前端：

- React
- Vite
- TypeScript
- Tailwind CSS
- React Router

后端：

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

AI 与检索：

- OpenAI-Compatible Chat Completions API
- DeepSeek / OpenAI / 通义千问 / 智谱 GLM / Ollama / 火山方舟 / Custom Provider
- 简化关键词 RAG
- 意向识别与问题范围分类
- Mock AI fallback

部署：

- Docker Compose
- 前端 Node 静态服务容器
- 后端 FastAPI 容器
- SQLite Docker volume 持久化

## 项目亮点

- 完整业务闭环：从客户官网咨询到后台线索跟进，不只是单页聊天 Demo。
- 前后台联动：公开咨询生成的 high 线索会进入后台客户线索池，对话也会进入对话记录。
- AI 服务层独立：AI 调用、mock fallback、模型测试和多 Provider 配置不写死在接口里。
- 多模型后台配置：支持在后台切换默认模型，API Key 脱敏回显，并提供连接测试。
- 简化 RAG 清晰可扩展：当前用关键词检索知识库，后续可升级向量检索、Embedding 和重排。
- 销售客服定位明确：支持问候、业务问题、销售相关、闲聊、无关和风险问题的边界控制。
- 企业 SaaS 风格：后台包含仪表盘、表格、筛选、弹窗表单、加载态和错误提示。
- 本地与 Docker 双启动：适合作品集展示、面试讲解和客户演示。

## 页面预览

截图目录预留在 `docs/screenshots/`，可将实际截图替换到对应路径。

![官网首页](docs/screenshots/public-home.png)

![公开咨询页](docs/screenshots/public-chat.png)

![仪表盘](docs/screenshots/dashboard.png)

![AI 对话测试](docs/screenshots/chat.png)

![知识库管理](docs/screenshots/knowledge.png)

![客户线索](docs/screenshots/leads.png)

![模型设置](docs/screenshots/ai-settings.png)

## 快速开始

推荐优先使用 Docker Compose 一次性启动前后端：

```bash
cp .env.example .env
docker compose up --build
```

访问地址：

```text
官网首页：http://localhost:5173/
后台登录：http://localhost:5173/login
后端 API：http://localhost:8000
```

默认账号：

```text
admin / admin123
```

基础验证：

```bash
curl http://localhost:8000/api/health
curl -I http://localhost:5173
```

如果 Docker Hub 网络不稳定、BuildKit 拉取镜像元数据超时，可以使用备用启动命令：

```bash
env DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose up --build
```

## Docker Compose 启动方式

Docker Compose 会启动两个容器：

- `backend`：FastAPI 服务，端口 `8000`。
- `frontend`：托管前端静态页面，并将 `/api` 反向代理到 backend 容器，端口 `5173`。

SQLite 数据库默认持久化到 Docker volume：

```text
/data/salespilot.db
```

默认 Docker 环境变量包括：

```env
DATABASE_URL=sqlite:////data/salespilot.db
APP_TIMEZONE=Asia/Shanghai
TZ=Asia/Shanghai
```

停止服务：

```bash
docker compose down
```

清空 Docker volume 并重新初始化演示数据：

```bash
docker compose down -v
docker compose up --build
```

## 本地开发启动方式

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

本地开发访问：

```text
http://localhost:5173
```

## 环境变量

本地后端环境变量位于 `backend/.env`，Docker Compose 可使用根目录 `.env`。

```env
AI_PROVIDER=deepseek
AI_API_KEY=
AI_BASE_URL=
AI_MODEL=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
ZHIPU_API_KEY=
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4-flash
OLLAMA_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
VOLCENGINE_ARK_API_KEY=
VOLCENGINE_ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VOLCENGINE_ARK_MODEL=
DATABASE_URL=sqlite:///./salespilot.db
APP_TIMEZONE=Asia/Shanghai
TZ=Asia/Shanghai
```

数据库中的后台默认模型配置优先于环境变量。环境变量主要作为 fallback：当数据库默认配置不存在、本地初始化尚未完成或 AI 服务未传入数据库会话时，系统会读取环境变量配置。

时间默认使用 `APP_TIMEZONE=Asia/Shanghai`。后端时间字段按 UTC 生成和保存，接口返回 ISO 时间字符串，前端统一按 Asia/Shanghai 展示为 `yyyy-MM-dd HH:mm`。

## 多模型 API 配置

后台「模型设置」页面支持配置多个模型 Provider：

- DeepSeek
- OpenAI
- 通义千问
- 智谱 GLM
- Ollama
- 火山方舟
- 自定义 OpenAI-Compatible API

同一时间只有一个默认模型生效，`POST /api/chat` 和 `POST /api/public/chat` 会使用当前默认模型配置。

API Key 处理规则：

- 前端不回显完整 API Key，只显示是否已配置和脱敏预览。
- 编辑配置时 API Key 留空表示不修改原 Key。
- 只有勾选清空 API Key 才会清除原 Key。
- 保存前会自动清理前后空格、`Bearer ` 前缀和首尾引号。
- 当前 Demo 将 API Key 存储在 SQLite 中，生产环境建议使用加密存储或密钥管理服务。

当默认模型未配置 API Key、配置错误、请求失败或响应格式异常时，系统会自动 fallback 到 mock 回复。Ollama 配置允许 API Key 为空。

## 火山方舟 DeepSeek 接入说明

火山方舟 DeepSeek 推荐配置：

- Provider：`火山方舟` 或 `Custom`
- Base URL：`https://ark.cn-beijing.volces.com/api/v3`
- Model：火山方舟接入点 ID，例如 `ep-xxxx`
- API Key：火山方舟 API Key

注意事项：

- 不要使用 DeepSeek 官方 Base URL：`https://api.deepseek.com`。
- 不要把 Model 填成 `deepseek-chat`，除非火山方舟控制台明确要求。
- 不要把 Base URL 填成完整的 `/chat/completions`，系统会自动拼接。
- API Key 不要带 `Bearer`、引号或空格，系统保存时会自动清理常见误输入。
- `401` 通常是 API Key 错误、权限不足、Key 与接入点不匹配或 Key 过期。
- `404` 通常是 Base URL 或 Model / 接入点 ID 错误。

Docker 中访问宿主机 Ollama 时，`base_url` 可能需要配置为：

```text
http://host.docker.internal:11434/v1
```

## 主要页面路由

公开页面：

```text
/                 客户官网首页
/public-chat      公开客户咨询页
```

后台页面：

```text
/login            后台登录
/dashboard        仪表盘
/knowledge        知识库管理
/chat             后台 AI 对话测试
/conversations    对话记录
/leads            客户线索
/ai-settings      模型设置
```

未登录访问后台页面会跳转到 `/login`。官网首页和公开咨询页不需要登录。

## 后端 API 概览

健康检查：

- `GET /api/health`

认证：

- `POST /api/auth/login`

仪表盘：

- `GET /api/dashboard/summary`

公开咨询与 AI 对话：

- `POST /api/public/chat`
- `POST /api/chat`

知识库：

- `GET /api/knowledge`
- `GET /api/knowledge/{id}`
- `POST /api/knowledge`
- `PUT /api/knowledge/{id}`
- `DELETE /api/knowledge/{id}`

对话记录：

- `GET /api/conversations`
- `GET /api/conversations/{id}`
- `DELETE /api/conversations/{id}`

客户线索：

- `GET /api/leads`
- `GET /api/leads/{id}`
- `POST /api/leads`
- `PUT /api/leads/{id}`
- `DELETE /api/leads/{id}`

模型设置：

- `GET /api/ai-settings/configs`
- `GET /api/ai-settings/current`
- `POST /api/ai-settings/configs`
- `PUT /api/ai-settings/configs/{id}`
- `POST /api/ai-settings/configs/{id}/set-default`
- `POST /api/ai-settings/configs/{id}/test`
- `DELETE /api/ai-settings/configs/{id}`

`/api/chat` 和 `/api/public/chat` 会返回原有核心字段：

```text
answer
intent_type
intent_level
matched_knowledge
```

同时包含可选辅助字段：

```text
ai_source
provider
model
scope_type
```

## 演示流程

1. 打开官网首页：`http://localhost:5173/`。
2. 点击“立即咨询”，进入 `/public-chat`。
3. 输入客户信息：
   - 姓名：`张三`
   - 联系方式：`13800000000`
   - 问题：`你们能接企业微信吗？多少钱？`
4. 查看 AI 回复、意向类型、意向等级、命中知识库和 high 线索提示。
5. 打开 `/login`，使用 `admin / admin123` 登录后台。
6. 进入客户线索页面，查看刚刚自动沉淀的 high 线索。
7. 进入对话记录页面，查看完整咨询记录。
8. 进入模型设置页面，展示多模型 API 配置能力。
9. 进入后台 AI 对话测试页，查看当前模型、回复来源和问题范围。

也可以在后台知识库新增一条资料，再回到公开咨询页测试知识库更新后的回复效果。

## 数据重置说明

重新导入种子数据：

```bash
cd backend
source .venv/bin/activate
python -m app.seed
```

完全清空本地 SQLite 后重新初始化：

```bash
rm backend/salespilot.db
cd backend
source .venv/bin/activate
python -m app.seed
```

Docker 环境清空 volume 后重启：

```bash
docker compose down -v
docker compose up --build
```

种子脚本是幂等的，不会重复插入同名内置知识和默认模型配置。本项目没有引入数据库迁移系统，如旧数据库缺少新增表或默认配置，可执行 `python -m app.seed` 补齐；如果演示数据可以丢弃，也可以删除 SQLite 文件后重新初始化。

## 版本记录

```text
v0.1.0：前后端基础 MVP，包含登录、仪表盘、知识库、AI 对话、对话记录和客户线索
v0.2.0：稳定性修复，补充异常处理、rollback、枚举校验和前端失败提示
v0.3.0：Docker Compose 部署包装与作品集 README 优化
v0.4.0：客户官网首页与公开咨询入口
v0.4.1：问候与无关问题兜底优化
v0.4.2：知识库扩充与销售客服回复效果优化
v0.4.3：模型 API 接入体验与火山方舟支持优化
v0.4.4：问题范围识别与对话边界优化
v0.4.5：系统时间生成与展示时区统一
```

## 当前限制

- 认证为演示版简化实现，固定账号和简单 token 仅适合本地演示。
- 未实现 JWT、刷新 token、RBAC、多租户和细粒度权限控制。
- API Key 当前存储在 SQLite 中，未做生产级加密或密钥托管。
- RAG 使用关键词检索，没有接入向量数据库、Embedding 和召回重排。
- SQLite 适合本地 Demo，不适合高并发生产场景。
- 未加入完整审计日志、限流、防暴力破解、监控告警和备份策略。
- npm audit 中与前端构建链相关的 high 警告未使用 `npm audit fix --force` 强制处理。

## 后续路线图

- 登录升级为 JWT、bcrypt/passlib 密码哈希、RBAC 和用户管理。
- 知识库支持文件上传、Excel / PDF / Word 批量导入和内容解析。
- RAG 升级为向量检索、Embedding、召回重排和引用来源展示。
- 接入企业微信、飞书、微信公众号、网页客服等多渠道。
- 增加线索跟进阶段、销售提醒、统计报表、导出和 CRM 对接。
- 增加测试用例、Playwright E2E、CI 和自动截图。
- 增加生产化 Docker Compose、HTTPS、反向代理、云数据库和备份策略。

## 免责声明

本项目为学习、作品集和面试演示 Demo，重点展示完整业务闭环、全栈工程结构和 AI 接入思路。当前版本未做生产级权限、安全、密钥管理、审计、限流和高可用加固，不建议直接用于真实生产环境。
