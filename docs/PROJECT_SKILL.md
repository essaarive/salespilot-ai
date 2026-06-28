# SalesPilot AI 项目开发 Skill

## 项目名称

SalesPilot AI / 智销助手

## 使用方式

当使用 Codex / Claude Code / Cursor Agent 处理本项目时，请先读取并遵守本文档。

每次执行任务前应确认：

- 当前任务是否会改变接口路径
- 是否会影响 `/api/chat` 或 `/api/public/chat`
- 是否需要执行后端、前端或 Docker 验证命令
- 是否会影响客户官网、公开咨询页、后台、多模型配置等核心闭环

推荐指令：

```text
请先读取 docs/PROJECT_SKILL.md，并严格遵守其中的项目约束。
本次任务：xxx。
完成后按文档要求执行验证命令。
```

## 项目定位

这是一个面向中小企业的 AI 智能获客客服系统 Demo。

系统包含：

- 客户官网首页
- 公开客户咨询页
- 企业后台管理系统
- 单企业品牌配置
- 知识库管理
- 文件知识库上传
- 回答可信度与人工兜底
- AI 销售客服问答
- 简化 RAG 检索
- 客户意向识别
- 高意向线索自动沉淀
- 对话记录管理
- 后台多模型 API 配置
- Docker Compose 部署

核心业务闭环：

客户访问官网
→ 进入公开咨询页
→ 提交姓名、联系方式、问题
→ AI 自动回复
→ 系统识别意向等级
→ high 意向自动沉淀到后台客户线索
→ 企业销售在后台跟进

## 当前项目路径

```text
/Users/ryan/projects/SalesPilot AI
```

## 技术栈

前端：

- React
- Vite
- TypeScript
- Tailwind CSS

后端：

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

AI：

- OpenAI-Compatible Chat Completions API
- 后台可配置多模型 Provider
- 支持 mock fallback

部署：

- Docker Compose
- 后端 FastAPI 容器
- 前端 Node 静态服务容器
- SQLite volume 持久化

## 当前支持的模型 Provider

后台「模型设置」支持：

- DeepSeek
- OpenAI
- 通义千问
- 智谱 GLM
- Ollama
- 火山方舟
- Custom 自定义兼容模型

火山方舟 DeepSeek 配置：

```text
Provider：火山方舟 或 Custom
Base URL：https://ark.cn-beijing.volces.com/api/v3
Model：火山方舟接入点 ID，例如 ep-xxxx
API Key：火山方舟 API Key
```

注意：

- Base URL 不要填写 `/chat/completions`
- Model 不要填 `deepseek-chat`，除非火山方舟控制台明确要求
- API Key 不要带 `Bearer`、引号或空格

## 当前重要页面

公开页面：

```text
/                 客户官网首页
/public-chat      公开客户咨询页
/embed/chat       嵌入式 iframe 聊天页
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
/company-settings 企业设置
```

默认账号：

```text
admin / admin123
```

## 当前重要接口

认证：

```text
POST /api/auth/login
```

健康检查：

```text
GET /api/health
```

公开咨询：

```text
POST /api/public/chat
```

后台 AI 对话：

```text
POST /api/chat
```

知识库：

```text
GET /api/knowledge
GET /api/knowledge/{id}
POST /api/knowledge
PUT /api/knowledge/{id}
DELETE /api/knowledge/{id}
```

文件知识库：

```text
GET /api/documents
POST /api/documents/upload
GET /api/documents/{id}
POST /api/documents/{id}/toggle-enabled
DELETE /api/documents/{id}
```

对话记录：

```text
GET /api/conversations
GET /api/conversations/{id}
DELETE /api/conversations/{id}
```

客户线索：

```text
GET /api/leads
GET /api/leads/{id}
POST /api/leads
PUT /api/leads/{id}
DELETE /api/leads/{id}
```

模型设置：

```text
GET /api/ai-settings/configs
GET /api/ai-settings/current
POST /api/ai-settings/configs
PUT /api/ai-settings/configs/{id}
POST /api/ai-settings/configs/{id}/set-default
POST /api/ai-settings/configs/{id}/test
DELETE /api/ai-settings/configs/{id}
```

企业设置：

```text
GET /api/company-settings
PUT /api/company-settings
GET /api/company-settings/public
```

## 当前核心后端文件

```text
backend/app/main.py
backend/app/database.py
backend/app/models.py
backend/app/schemas.py
backend/app/seed.py
backend/app/routers/auth.py
backend/app/routers/dashboard.py
backend/app/routers/knowledge.py
backend/app/routers/chat.py
backend/app/routers/conversations.py
backend/app/routers/leads.py
backend/app/routers/ai_settings.py
backend/app/routers/documents.py
backend/app/services/ai_service.py
backend/app/services/rag_service.py
backend/app/services/intent_service.py
backend/app/services/document_parser.py
backend/app/services/document_chunker.py
```

## 当前核心前端文件

```text
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/layouts/AdminLayout.tsx
frontend/src/pages/PublicHome.tsx
frontend/src/pages/PublicChat.tsx
frontend/src/pages/EmbedChat.tsx
frontend/src/pages/Login.tsx
frontend/src/pages/Dashboard.tsx
frontend/src/pages/Knowledge.tsx
frontend/src/pages/Chat.tsx
frontend/src/pages/Conversations.tsx
frontend/src/pages/Leads.tsx
frontend/src/pages/AISettings.tsx
frontend/src/pages/CompanySettings.tsx
frontend/src/pages/helpers.ts
frontend/src/types/index.ts
```

## 重要开发原则

所有开发必须遵守：

1. 不随意改变现有接口路径。
2. 不删除现有返回字段。
3. 不破坏 `/api/chat` 和 `/api/public/chat` 的现有业务闭环。
4. 不破坏知识库、线索、对话记录、多模型配置。
5. 不执行 `npm audit fix --force`。
6. 不引入大型 UI 框架。
7. 保持 React + Vite + TypeScript + Tailwind CSS。
8. 保留 mock fallback。
9. 后端写操作要有异常处理和 rollback。
10. API Key 不能完整回显到前端。
11. 模型测试错误提示要使用友好的中文说明。
12. 当前项目是 MVP / Demo，不要包装成生产可用系统。
13. 所有修改后必须执行验证命令。

## 必须执行的验证命令

后端改动后执行：

```bash
python3 -m compileall backend/app
```

前端改动后执行：

```bash
cd frontend && npm run build
```

Docker 配置或环境变量改动后执行：

```bash
docker compose config
```

如 Docker 实际运行验证：

```bash
env DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose up --build
```

健康检查：

```bash
curl http://localhost:8000/api/health
curl http://127.0.0.1:8010/api/health
curl http://127.0.0.1:5176/api/health
```

## 本地开发启动方式

默认本地端口：

```text
前端：5173
后端：8000
```

多项目并行开发推荐端口：

```text
前端：5176
后端：8010
```

后端：

```bash
cd /Users/ryan/projects/SalesPilot\ AI/backend
source .venv/bin/activate
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

前端：

```bash
cd /Users/ryan/projects/SalesPilot\ AI/frontend
VITE_PORT=5176 VITE_PROXY_TARGET=http://127.0.0.1:8010 npm run dev -- --host 127.0.0.1
```

访问：

```text
http://127.0.0.1:5176
```

前端开发环境规则：

```text
VITE_PORT 未设置 -> 5173
VITE_PROXY_TARGET 未设置 -> http://127.0.0.1:8000
端口使用 strictPort，端口冲突时应明确报错，不自动漂移。
前端 API 请求使用相对路径 /api/...，由 Vite proxy 转发。
```

本地开发 CORS 允许来源：

```text
http://localhost:5173
http://127.0.0.1:5173
http://localhost:5176
http://127.0.0.1:5176
```

其中 `5173` 是默认兼容端口，`5176` 是多项目并行开发推荐端口。此允许列表用于 Demo 本地开发，不等同于生产级完整跨域安全方案。

## Docker 启动方式

```bash
cd /Users/ryan/projects/SalesPilot\ AI
env DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose up --build
```

多项目并行开发推荐 Docker 启动：

```bash
cd /Users/ryan/projects/SalesPilot\ AI
FRONTEND_PORT=5176 BACKEND_PORT=8010 \
env DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 \
docker compose up --build
```

访问：

```text
默认：http://localhost:5173
推荐：http://127.0.0.1:5176
```

## 时间配置

```text
默认 APP_TIMEZONE=Asia/Shanghai。
Docker 中同时设置 TZ=Asia/Shanghai。
后端时间字段统一按 UTC 生成和保存，接口返回 ISO 时间字符串。
前端统一按 Asia/Shanghai 格式化展示时间，格式为 yyyy-MM-dd HH:mm。
如果部署到其他地区，可修改 APP_TIMEZONE，并按需要同步调整前端展示时区。
```

## 运行方式注意事项

本项目不要同时混用 Docker 前端和本地 Vite 前端。

如果页面刷新后看不到最新代码，优先检查：

- 当前浏览器访问的是 Docker 容器还是本地 Vite
- 是否重新执行了 `npm run dev`
- Docker 模式下是否重新 `docker compose up --build`
- 端口 5173 / 8000 / 5176 / 8010 是否被旧进程占用

排查命令：

```bash
lsof -i :5173
lsof -i :8000
lsof -i :5176
lsof -i :8010
```

如果登录页出现“无法连接后端服务，请确认前端代理配置和后端服务是否已启动。”，优先检查：

- 后端是否已启动。
- `VITE_PROXY_TARGET` 是否指向当前后端端口。
- `VITE_PORT` 是否与其他项目冲突。
- 浏览器访问地址是否为当前 SalesPilot AI 项目端口。

## 数据重置

本地 SQLite：

```bash
cd /Users/ryan/projects/SalesPilot\ AI/backend
rm -f salespilot.db
python -m app.seed
```

Docker volume：

```bash
cd /Users/ryan/projects/SalesPilot\ AI
docker compose down -v
env DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose up --build
```

注意：`docker compose down -v` 会清空线索、对话、知识库等数据。

## 文件知识库上传

```text
上传目录：storage/uploads
Docker volume：salespilot_uploads -> /app/storage/uploads
环境变量：UPLOAD_DIR=storage/uploads
环境变量：MAX_UPLOAD_SIZE_MB=10
```

支持格式：

```text
.pdf
.docx
.xlsx
.txt
.md
```

限制：

- 单次只上传一个文件。
- 单文件最大 10 MB，文件名最大 120 个字符。
- 不支持 .doc / .xls / .csv / 图片 / 扫描件 PDF OCR / 压缩包 / 网页链接 / 音视频。
- 服务端必须重新生成安全保存文件名，禁止路径穿越。
- 上传目录不作为公开静态资源目录。
- 上传文件不能进入 Git，`storage/uploads/*` 默认忽略，仅保留 `.gitkeep`。
- 文件知识片段复用 `knowledge_items`，`source_type=document`。
- 文件可通过 `documents.is_enabled` 停用；停用后文件记录保留，但对应 `source_document_id` 的知识片段不参与 RAG。
- 删除 documents 记录时必须同步删除关联知识片段和本地原文件。

解析策略：

- PDF 使用 pypdf 按页提取文本，不做 OCR。
- DOCX 使用 python-docx 提取段落和表格。
- XLSX 使用 openpyxl 读取可见 Sheet 并按表头组织行文本。
- TXT / Markdown 使用 UTF-8 / UTF-8-SIG 读取并清理空行和 Markdown 噪声。
- 切片目标 400-600 字，最大 700 字，保留 50-80 字上下文重叠。

## 当前意向类型

```text
greeting      问候
pricing       询价
cooperation   合作/接入咨询
product       产品咨询
delivery      交付周期
after_sales   售后问题
irrelevant    无关问题
```

## 当前意向等级

```text
high
medium
low
```

## 当前问题范围类型

当前 `/api/chat` 和 `/api/public/chat` 已返回可选字段 `scope_type`，可选值：

```text
business_related   业务相关
sales_adjacent     销售相关
general_chat       普通闲聊
out_of_scope       无关问题
unsafe             风险/不合规问题
```

处理原则：

- `business_related`：结合知识库认真回答，可根据意向生成线索
- `sales_adjacent`：简短建议，并引导到 AI 客服价值
- `general_chat`：简短回应，然后拉回 AI 销售客服业务
- `out_of_scope`：不展开无关话题，引导回业务咨询
- `unsafe`：拒绝协助，并引导回合规客服用途

## 当前 AI 来源字段

`/api/chat` 和 `/api/public/chat` 原有字段：

```text
answer
intent_type
intent_level
matched_knowledge
```

新增可选字段：

```text
ai_source: model | mock
provider
model
scope_type
retrieval_confidence: high | medium | low | none
answer_basis: knowledge | general_guidance | fallback
requires_handoff
handoff_reason
```

后台 Chat 页面显示：

```text
回复来源：真实模型 / mock 演示
当前模型：provider / model
API Key：已配置 / 未配置
回答依据：企业知识库 / 通用业务引导 / 人工兜底
匹配度：高 / 中 / 低 / 无
```

公开咨询页不暴露内部模型细节、文件名和片段编号。

## 当前回答可信度与人工兜底

`retrieval_confidence` 用于表达当前关键词 RAG 的命中可靠度：

```text
high    命中具体产品名、方案名、价格、交期、接入能力等明确事实，或文件知识强匹配
medium  命中相关业务资料，但不宜做过度精确承诺
low     只有弱关键词匹配，不足以支撑企业事实
none    没有可靠知识项
```

`answer_basis` 取值：

```text
knowledge          回答主要基于企业知识库
general_guidance   通用业务引导，不应视为企业事实
fallback           资料不足、人工兜底或风险场景回复
```

人工跟进触发：

```text
customer_requested_human  客户要求转人工、找销售、人工客服
knowledge_not_found       业务相关问题低置信度或无可靠资料
special_quote             定制报价、合同、招标、大批量、特殊折扣
custom_requirement        代理合作、项目合作、复杂定制
complaint_or_risk         投诉、退款、赔偿、纠纷、严重问题
```

规则：

- `business_related` 且低置信度 / 无命中时，不编造价格、交期、接入能力等企业事实。
- `requires_handoff=true` 且客户填写姓名或联系方式时，即使不是 high 意向，也沉淀线索。
- 普通闲聊、无关问题和风险拒答不应因为弱关键词自动生成 high 线索。
- 当前可信度是 Demo 级关键词规则，不等同于生产级事实校验。

## 当前企业品牌配置

v0.8.0 支持单企业品牌配置，不做多租户。

后台页面：

```text
/company-settings
```

数据库表：

```text
company_settings
```

主要字段：

```text
company_name
company_short_name
company_logo_url
company_intro
customer_service_name
customer_service_avatar_url
welcome_message
brand_color
business_scope
human_contact_phone
human_contact_wechat
human_contact_email
business_hours
handoff_message
forbidden_topics
allowed_embed_domains
widget_position
```

规则：

- 系统启动时如果没有 `company_settings` 记录，会自动创建默认 SalesPilot AI 配置。
- 公开接口 `/api/company-settings/public` 不返回 `forbidden_topics`、数据库内部字段、模型配置或 API Key。
- 官网首页和公开咨询页优先使用企业名称、Logo URL、客服名称、欢迎语、品牌主色和人工联系方式。
- `/api/chat` 和 `/api/public/chat` 的 Prompt 会注入当前企业名称、客服名称、业务范围、工作时间、人工联系方式和禁止回答内容。
- 命中 `forbidden_topics` 时不展开回答，走人工兜底并设置 `requires_handoff=true`。
- Logo 第一版仅支持 URL；不支持 Logo 文件上传、企业注册、多租户、自定义域名或复杂主题编辑器。

## 当前官网嵌入式客服组件

v0.9.0 支持单企业官网嵌入式 AI 客服组件，不做多租户 Widget Key。

公开资源与页面：

```text
/widget.js       纯 JavaScript 嵌入脚本
/embed/chat      iframe 聊天页面
```

脚本示例：

```html
<script
  src="https://your-domain.com/widget.js"
  data-api-base="https://your-domain.com"
  data-position="right"
  data-brand-color="#0F766E"
  data-allowed-domains="example.com,www.example.com"
></script>
```

本地开发示例：

```html
<script
  src="http://127.0.0.1:5176/widget.js"
  data-api-base="http://127.0.0.1:5176"
  data-position="right"
  data-brand-color="#0F766E"
  data-allowed-domains="127.0.0.1,localhost"
></script>
```

规则：

- `widget.js` 是原生 JavaScript，不依赖 React、Tailwind、jQuery 或第三方 CDN。
- widget 使用 Shadow DOM 隔离宿主页面样式，避免污染企业官网。
- 悬浮位置通过 `data-position=right|left` 控制。
- 企业品牌色通过 `data-brand-color` 传入，仅接受 `#RGB` 或 `#RRGGBB`；非法值回退 `#2563EB`。
- iframe URL 为 `{data-api-base}/embed/chat`。
- iframe 聊天页复用 `GET /api/company-settings/public` 和 `POST /api/public/chat`。
- `/embed/chat` 不显示官网导航、后台导航、内部文件名、模型配置或后台链接。
- iframe 关闭协议为 `salespilot:close`，宿主脚本必须同时校验 message origin 和当前 iframe source，并忽略其他消息。
- iframe 初始 title 为“在线咨询”；企业公开配置加载成功后，页面 title 更新为“企业简称 在线咨询”。
- `allowed_embed_domains` 保存在 `company_settings`，后台用于生成嵌入代码。
- `data-allowed-domains` 按 hostname 白名单判断，忽略协议和端口；留空为 Demo 模式。
- `/api/company-settings/public` 不返回 `allowed_embed_domains`、`forbidden_topics` 或内部字段。
- 白名单是前端基础限制，不是生产级安全认证；不要把当前 Demo 包装成安全隔离完整的生产 Widget。

v0.9.1 线索轻量去重规则：

- 仅处理 `intent_level=high` 或 `requires_handoff=true` 的自动沉淀线索。
- 有有效联系方式时，按规范化电话、邮箱、微信或完整联系方式匹配最近 24 小时内的线索。
- 命中后保留原始创建时间和跟进状态，更新最新需求、备注、意向等级、人工转接状态和更明确的跟进原因。
- 没有有效联系方式时不做模糊去重，继续沿用原有创建逻辑。
- 这是 Demo 级时间窗口规则，不等同于 CRM 主数据合并，也不保证并发请求下的强唯一性。

本地宿主页测试文件：

```text
docs/widget-demo.html
```

## 真实模型 API 验收流程

配置真实模型后，必须验证：

1. 进入 `/ai-settings`
2. 确认目标配置：
   - `enabled=true`
   - `is_default=true`
   - API Key 已配置
3. 点击“测试连接”
4. 进入 `/chat`
5. 提问：

```text
你们做 AI 客服多少钱？
```

预期：

- `ai_source=model`
- 显示真实模型回复
- `intent_level=high`
- 自动沉淀客户线索

如果返回 `ai_source=mock`，说明真实模型调用失败，系统走了 mock fallback。

## 当前对话策略

系统不是通用聊天机器人，而是 AI 销售客服系统。

回答原则：

1. 业务相关问题：认真回答，结合知识库，最后引导客户补充需求。
2. 销售相关问题：简短建议，并引出 AI 客服价值。
3. 普通闲聊：可以简短回应一句，但要拉回 AI 销售客服业务。
4. 无关问题：礼貌引导回价格、功能、交付、行业、接入方式。
5. 高风险问题：拒绝协助，并引导回合规客服场景。
6. 默认回复控制在 80-180 字。
7. 不使用 Markdown 加粗符号、复杂标题或长编号列表。
8. 不编造知识库没有的价格、功能、交付承诺。

## 当前知识库方向

已扩充知识库分类：

- 价格套餐
- 渠道接入
- 企业微信
- 飞书
- 网页客服
- 知识库导入
- 数据安全
- 私有化部署
- 售后维护
- 人工接管
- 适用行业
- 和 Coze/Dify 区别
- 客户案例
- 常见异议处理

检索策略：

- 标题、分类、关键词、内容都参与评分。
- 支持简单同义词扩展。
- 默认最多返回 5 条知识。
- 有最低分数阈值，避免弱词误召回。

## 模型测试错误提示规则

测试连接错误需要映射为中文：

```text
401：鉴权失败，请检查 API Key 是否正确、是否带有多余引号/空格，以及该 Key 是否有权限调用当前模型或接入点。
403：无权限调用，请检查账号权限、模型权限、接入点权限或当前模型是否已开通。
404：接口或模型不存在，请检查 Base URL 是否正确，以及 Model 是否填写为正确的模型名或接入点 ID。
429：请求过于频繁或额度不足，请稍后重试，或检查平台额度和限流设置。
5xx：模型服务异常，请稍后重试，或检查模型平台服务状态。
网络失败：连接失败，请检查 Base URL、网络连接、代理配置或服务是否可访问。
返回格式异常：模型接口已响应，但返回格式不符合 OpenAI-Compatible Chat Completions 格式，请检查接口兼容性。
```

## API Key 处理规则

保存 API Key 前自动清理：

1. trim 前后空格。
2. 去掉 `Bearer ` 前缀。
3. 去掉首尾单引号或双引号。
4. 新增配置清理后为空，视为未配置。
5. 编辑时 `api_key=""` 不覆盖原 Key。
6. 只有 `clear_api_key=true` 才清空旧 Key。
7. 前端只显示脱敏预览，不回显完整 Key。

## 当前版本记录建议

```text
v0.4.0：客户官网 + 公开咨询入口
v0.4.1：问候与无关问题兜底优化
v0.4.2：知识库与销售回复效果优化
v0.4.3：模型 API 接入体验与火山方舟支持优化
v0.4.4：问题范围识别与对话边界优化
v0.4.5：系统时间生成与展示时区统一
v0.6.0：企业文件知识库上传版
v0.7.0：回答可信度、人工兜底与文件知识状态管理
v0.8.0：单企业品牌配置与企业专属 AI 客服版
v0.9.0：官网嵌入式 AI 客服组件
v0.9.1：Widget 品牌化完善与线索轻量去重
```

## 推荐演示流程

1. 打开官网首页 `/`。
2. 点击“立即咨询”进入 `/public-chat`。
3. 输入：
   - 姓名：张三
   - 联系方式：13800000000
   - 问题：你们能接企业微信吗？多少钱？
4. 查看 AI 回复、意向类型、意向等级、命中知识库。
5. 登录后台 `/login`。
6. 使用 `admin / admin123`。
7. 进入客户线索，查看自动沉淀的 high 线索。
8. 进入对话记录，查看完整咨询记录。
9. 进入模型设置，展示 DeepSeek / OpenAI / 通义 / 智谱 / Ollama / 火山方舟配置。
10. 进入后台 Chat 页面，展示当前模型、回复来源：真实模型或 mock 演示。
11. 进入知识库的「文件知识库」Tab，上传企业资料文件，测试 `/chat` 和 `/public-chat` 是否能命中文件片段。

## 截图清单

```text
docs/screenshots/public-home.png
docs/screenshots/public-chat.png
docs/screenshots/dashboard.png
docs/screenshots/knowledge.png
docs/screenshots/leads.png
docs/screenshots/conversations.png
docs/screenshots/ai-settings.png
docs/screenshots/embed-chat.png
```

## Codex 输出要求

每次任务完成后，Codex 应输出：

1. 修改 / 新增文件
2. 核心修改点
3. 是否改变接口路径或返回字段
4. 验证命令和结果
5. 仍未处理的问题
6. 是否建议提交 Git

如果任务只读验收，应明确说明“未修改代码”。

## 后续路线图

优先级从高到低：

```text
v0.10.0：向量检索 / Chroma / FAISS
v1.0.0：JWT + bcrypt/passlib + RBAC
v1.1.0：Playwright E2E 测试与自动截图
```
