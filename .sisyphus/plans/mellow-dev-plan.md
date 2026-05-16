# Mellow — 英语教学 Agent 开发计划

## 项目概述

Mellow 是一个基于多范式 Agent 的英语教学移动端应用。核心特点：
- 自定义角色扮演（女朋友/严师等），影响语言风格和教学方式
- AI 生成个性化学习计划，动态刻画用户画像
- 外置知识库确保教学内容可靠
- 角色记忆（情感感知 + 主动联系）
- 即时语音互动（类似豆包）

**技术栈**：Python FastAPI 后端 + Flutter 移动端 + SQLite/LanceDB 存储

---

## Phase 1：项目骨架与环境搭建（预计 1-2 天）

### 目标
搭建可运行的最小 FastAPI 项目，建立分层目录结构，配置开发环境。

### 文件清单

```
mellow/
├── backend/
│   ├── pyproject.toml              # 项目依赖管理
│   ├── .env.example                # 环境变量模板
│   ├── .gitignore
│   ├── main.py                     # FastAPI 入口 + lifespan
│   └── src/mellow/
│       ├── __init__.py
│       ├── config.py               # 全局 Pydantic Settings（环境变量驱动）
│       ├── models.py               # 共享数据模型（Message, User 等）
│       ├── exceptions.py           # 自定义异常 + 全局错误处理
│       └── di.py                   # 依赖注入容器
```

### 关键实现

**`pyproject.toml`** — 核心依赖：
```
fastapi[standard]>=0.115
uvicorn[standard]>=0.34
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv>=1.0
openai>=1.0          # LLM/Embedding 客户端
python-jose[cryptography]  # JWT
passlib[bcrypt]      # 密码哈希
httpx                # 外部 API 异步调用
sqlalchemy>=2.0      # SQLite ORM
aiosqlite            # 异步 SQLite
lancedb>=0.25        # 向量库
```

**`config.py`** — 全局配置：
```python
class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    llm_fast_model: str = "gpt-4o-mini"  # 闲聊路由

    # Embedding
    embed_provider: str = "dashscope"
    embed_api_key: str = ""
    embed_model: str = "text-embedding-v4"
    embed_dimension: int = 1024

    # JWT
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/mellow.db"
    lancedb_path: str = "./data/lancedb"

    model_config = SettingsConfigDict(env_file=".env")
```

### 验证标准
- [x] `uvicorn main:app --reload` 启动成功
- [x] `GET /health` 返回 200
- [x] `.env` 文件正确加载配置
- [x] 目录结构符合 `src/mellow/` 分层约定

---

## Phase 2：核心抽象层（预计 2-3 天）

### 目标
定义所有可拔插接口和基础抽象类，建立项目的契约层。

### 文件清单

```
backend/src/mellow/
├── llm/
│   ├── __init__.py
│   ├── client.py                  # LLMProvider 抽象 + OpenAI 实现
│   └── router.py                  # 混合路由（快速/强模型调度）
├── providers/
│   ├── __init__.py
│   ├── knowledge.py               # KnowledgeProvider 抽象
│   ├── embedding.py               # EmbeddingProvider 抽象
│   ├── asr.py                     # ASRProvider 抽象
│   ├── tts.py                     # TTSProvider 抽象
│   └── auth.py                    # AuthProvider 抽象
├── knowledge/
│   ├── __init__.py
│   ├── base.py                    # KnowledgeProvider 协议 + WordEntry/SearchResult 模型
│   └── implementations/
│       ├── __init__.py
│       └── open_english_dict.py   # ImSingee/open-english-dictionary SQLite 实现
├── embedding/
│   ├── __init__.py
│   ├── base.py                    # EmbeddingProvider 协议
│   └── implementations/
│       ├── __init__.py
│       ├── dashscope.py           # 阿里云百炼 embedding
│       └── siliconflow.py         # 硅基流动 embedding
├── voice/
│   ├── __init__.py
│   ├── base.py                    # ASRProvider + TTSProvider 协议
│   └── implementations/
│       ├── __init__.py
│       └── volcano.py             # 火山引擎 ASR + TTS
└── auth/
    ├── __init__.py
    ├── base.py                    # AuthProvider 协议
    ├── jwt_auth.py                # JWT 自建实现
    ├── middleware.py              # FastAPI 认证中间件
    └── models.py                  # User, Token, LoginRequest
```

### 关键抽象接口

**LLMProvider** — LLM 客户端统一接口：
```python
class LLMProvider(Protocol):
    async def chat(self, messages: list[Message], model: str | None = None) -> str: ...
    async def chat_stream(self, messages: list[Message], model: str | None = None) -> AsyncIterator[str]: ...
```

**KnowledgeProvider** — 知识库统一接口：
```python
class KnowledgeProvider(Protocol):
    async def lookup(self, word: str) -> WordEntry | None: ...    # 精确查词
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]: ...  # 语义检索
    @property
    def source_name(self) -> str: ...
```

**EmbeddingProvider** — 向量嵌入统一接口：
```python
class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...
    @property
    def dimension(self) -> int: ...
```

**ASRProvider / TTSProvider** — 语音统一接口：
```python
class ASRProvider(Protocol):
    async def transcribe(self, audio_bytes: bytes, lang: str = "auto") -> str: ...

class TTSProvider(Protocol):
    async def synthesize(self, text: str, voice: str, speed: float = 1.0) -> bytes: ...
```

**AuthProvider** — 认证统一接口：
```python
class AuthProvider(Protocol):
    async def register(self, username: str, password: str) -> User: ...
    async def login(self, username: str, password: str) -> Token: ...
    async def verify_token(self, token: str) -> User: ...
    async def refresh_token(self, refresh_token: str) -> Token: ...
```

### 验证标准
- [x] 所有抽象接口定义清晰，类型标注完整
- [x] 每个 Provider 至少有 1 个具体实现
- [x] 依赖注入可通过 `di.py` 切换实现
- [x] `OpenEnglishDictProvider.lookup("hello")` 返回正确词条

---

## Phase 3：Agent 引擎（预计 3-4 天）

### 目标
实现 Orchestrator + 子 Agent 工厂，完成混合范式调度。

### 文件清单

```
backend/src/mellow/agent/
├── __init__.py
├── base.py                       # BaseAgent 抽象类
├── message.py                    # Message 模型（user/assistant/system/tool）
├── orchestrator.py               # OrchestratorAgent（意图识别 + 路由分发）
├── chat_agent.py                 # ChatAgent（角色扮演对话，SimpleAgent 范式）
├── teach_agent.py                # TeachAgent（教学 Plan & Solve）
├── reflect_agent.py              # ReflectAgent（纠错 Reflection）
├── tool_registry.py              # ToolRegistry（工具注册中心）
└── prompts/
    ├── __init__.py
    ├── orchestrator.py           # 意图识别 prompt 模板
    ├── chat.py                   # 角色扮演 prompt 模板
    ├── teach.py                  # 教学 prompt 模板
    └── reflect.py                # 纠错 prompt 模板
```

### 关键实现

**OrchestratorAgent** — 意图分发：
```
用户输入 → 意图识别（LLM 判断：chat / teach / reflect / lookup）
         → 路由到对应子 Agent
         → 子 Agent 返回结果
```

意图分类：
- `chat` → ChatAgent（日常对话、角色扮演）
- `teach` → TeachAgent（学习计划、新课教学）
- `reflect` → ReflectAgent（纠正错误、分析弱项）
- `lookup` → 直接查 KnowledgeProvider

**BaseAgent** — Agent 基类：
```python
class BaseAgent(ABC):
    llm: LLMProvider
    system_prompt: str
    tools: ToolRegistry

    @abstractmethod
    async def run(self, messages: list[Message], context: AgentContext) -> AgentResponse: ...
    @abstractmethod
    async def run_stream(self, messages: list[Message], context: AgentContext) -> AsyncIterator[str]: ...
```

**ChatAgent** — 角色扮演对话：
- 注入角色 system prompt（从 Persona 配置生成）
- 注入角色记忆（最近对话摘要 + 情感状态）
- 注入会话上下文
- 流式输出 → SSE

**TeachAgent** — 教学 Plan & Solve：
- Planner 步骤：分析用户画像 → 确定学习主题 → 生成周计划
- Executor 步骤：逐日展开 → 生成教学对话 → 嵌入练习
- 必须调用 `KnowledgeProvider.lookup()` 校验教学内容

**ReflectAgent** — 纠错反思：
- 检测用户错误 → 分析错误原因 → 给出针对性建议
- 更新 `LearningProfile.mistake_log`

### 验证标准
- [x] Orchestrator 正确分发 4 种意图
- [x] ChatAgent 输出风格匹配角色设定
- [x] TeachAgent 生成的计划包含 `KnowledgeProvider` 校验过的单词
- [x] ReflectAgent 能识别并解释常见英语错误

---

## Phase 4：角色 + 知识库系统（预计 2-3 天）

### 目标
实现角色配置管理、知识库查询、预设角色库。

### 文件清单

```
backend/src/mellow/persona/
├── __init__.py
├── models.py                     # Persona, LanguageStyle, TeachingStyle 模型
├── manager.py                    # PersonaManager（CRUD + 角色工厂）
├── prompts.py                    # 角色 prompt 模板引擎
└── presets/
    ├── __init__.py
    ├── girlfriend.json           # 温柔女朋友预设
    ├── strict_teacher.json       # 严厉老师预设
    ├── study_buddy.json          # 学习伙伴预设
    └── humorous_friend.json      # 幽默朋友预设

backend/src/mellow/knowledge/
├── __init__.py
├── base.py                       # 已在 Phase 2 定义
└── implementations/
    ├── __init__.py
    ├── open_english_dict.py      # SQLite 本地词典实现
    └── composite.py              # CompositeProvider（多源聚合）
```

### 关键实现

**Persona 模型**：
```python
class Persona(BaseModel):
    id: str
    name: str
    role: str
    language_style: LanguageStyle
    teaching_style: TeachingStyle
    strictness: float
    correction_frequency: str
    intimacy_level: str
    interaction_rhythm: tuple[int, int]  # (min_hours, max_hours)
    emotional_sensitivity: float
    system_prompt_template: str          # Jinja2/Jinja 模板
    is_preset: bool
    created_by: str | None
```

**PersonaManager**：
- `get_presets()` → 返回所有预设角色
- `create_custom(persona_data)` → 创建自定义角色
- `get_persona(persona_id)` → 获取角色配置
- `render_system_prompt(persona, user_name)` → 渲染角色 prompt

**预设角色示例**（`girlfriend.json`）：
```json
{
  "name": "Sara",
  "role": "girlfriend",
  "language_style": {
    "tone": "warm, playful, affectionate",
    "traits": ["uses pet names", "always encouraging", "gentle corrections"]
  },
  "teaching_style": {
    "approach": "引导式",
    "strictness": 0.3,
    "correction_frequency": "major_only"
  },
  "intimacy_level": "close",
  "interaction_rhythm": [12, 24],
  "emotional_sensitivity": 0.9,
  "system_prompt_template": "你是 {{ user_name }} 的英语学习伙伴 Sara..."
}
```

### 验证标准
- [x] 4 个预设角色可加载并渲染 system prompt
- [x] 用户可创建自定义角色，存到 SQLite
- [x] 角色切换后，学习档案不变，角色记忆切换
- [x] `OpenEnglishDictProvider.lookup()` 返回结构化词条

---

## Phase 5：记忆系统（预计 3-4 天）

### 目标
实现三层记忆模型：学习档案、角色记忆、会话上下文。

### 文件清单

```
backend/src/mellow/memory/
├── __init__.py
├── models.py                     # LearningProfile, PersonaMemory, SessionContext
├── learning_profile.py           # LearningProfileManager（学习档案 CRUD + 知识图谱）
├── persona_memory.py             # PersonaMemoryManager（角色记忆 + 摘要压缩）
├── session_context.py            # SessionContextManager（会话上下文管理）
├── compression.py                # 对话摘要压缩（LLM 生成摘要）
└── proactive.py                  # 主动联系定时器 + 文案生成

backend/src/mellow/vector_store/
├── __init__.py
├── connection.py                 # LanceDBConnector（Singleton 连接管理）
├── schemas.py                    # LanceModel 定义
├── memory_store.py               # 对话记忆向量存储（插入/检索）
└── knowledge_store.py            # 知识库向量存储（插入/检索）
```

### 关键实现

**LearningProfile** — 学习档案：
```python
class LearningProfile(BaseModel):
    user_id: str
    vocabulary_size: int
    cefr_level: str                # A1-C2
    weak_areas: list[str]          # ["tenses", "prepositions"]
    mastered_words: dict[str, float]  # word → mastery_level
    mistake_log: list[MistakeEntry]
    completed_lessons: list[str]
    current_plan: WeeklyPlan | None
    created_at: datetime
    updated_at: datetime
```

**PersonaMemory** — 角色记忆：
```python
class PersonaMemory(BaseModel):
    persona_id: str
    user_id: str
    relationship_summary: str      # LLM 生成的关系摘要
    emotional_trajectory: list[MoodEvent]  # 情绪时间线
    key_facts: list[str]           # 从对话中提取的关键信息
    last_interaction: datetime
    interaction_count: int
```

存储策略：7 天内原始对话存 LanceDB（向量可检索），超出压缩为摘要（SQLite）。

**SessionContext** — 会话上下文：
```python
class SessionContext:
    session_id: str
    user_id: str
    persona_id: str
    current_topic: str | None
    recent_mistakes: list[MistakeEntry]
    conversation_history: list[Message]  # 最近 20 轮
    user_mood: str | None
    started_at: datetime
```

### 记忆压缩流程：
```
每 N 轮对话后：
  1. 取最近对话 → LLM 生成摘要
  2. 提取关键事件（情绪转折、学习里程碑）
  3. 更新 PersonaMemory.relationship_summary
  4. 归档旧对话 → 7 天后从 LanceDB 清理
```

### 主动联系机制：
```python
class ProactiveMessenger:
    def schedule_next_poke(self, user_id: str, persona: Persona) -> datetime:
        """根据 interaction_rhythm 随机生成下次联系时间"""
        min_h, max_h = persona.interaction_rhythm
        delay = random.randint(min_h * 3600, max_h * 3600)
        return datetime.now() + timedelta(seconds=delay)

    async def check_and_poke(self) -> list[ProactiveMessage]:
        """定时检查到期用户，生成角色化文案，发送消息"""
        # 1. 查询所有 last_interaction + delay < now 的用户
        # 2. 对每个用户：取角色记忆 → LLM 生成自然开场白
        # 3. 写入消息表，下次用户连接时展示
```

### 验证标准
- [x] LearningProfile 正确追踪单词掌握度（去重）
- [x] PersonaMemory 正确记录情绪轨迹
- [x] 对话摘要压缩不丢失关键信息
- [x] 主动联系定时器到期后正确生成角色化消息
- [x] LanceDB 向量检索正确召回相关历史对话

---

## Phase 6：API 层（预计 2-3 天）

### 目标
实现 REST API + SSE 对话流 + WebSocket 语音流。

### 文件清单

```
backend/src/mellow/api/
├── __init__.py
├── deps.py                       # FastAPI Depends（用户认证、Provider 注入）
├── routes/
│   ├── __init__.py
│   ├── auth.py                   # POST /auth/register, /auth/login, /auth/refresh
│   ├── chat.py                   # POST /chat, GET /chat/stream (SSE)
│   ├── teach.py                  # POST /teach/plan, GET /teach/plan/{id}
│   ├── persona.py                # GET /personas, POST /personas, PUT /personas/{id}
│   ├── knowledge.py              # GET /knowledge/lookup?word=, GET /knowledge/search?q=
│   ├── profile.py                # GET /profile, PUT /profile
│   ├── memory.py                 # GET /memory/emotions, GET /memory/facts
│   └── voice.py                  # WS /voice/stream
├── middleware/
│   ├── __init__.py
│   ├── auth.py                   # JWT 验证中间件
│   └── error_handler.py          # 全局异常处理
└── schemas/
    ├── __init__.py
    ├── auth.py                   # 请求/响应 Schema
    ├── chat.py
    ├── teach.py
    └── persona.py
```

### API 端点设计

**认证**：
```
POST /api/v1/auth/register    # { username, password } → { user, token }
POST /api/v1/auth/login       # { username, password } → { token, refresh_token }
POST /api/v1/auth/refresh     # { refresh_token } → { token }
```

**对话**：
```
POST /api/v1/chat             # { persona_id, message } → { reply, action }
GET  /api/v1/chat/stream      # SSE: { persona_id, message } → stream text/event-stream
```

**教学**：
```
POST /api/v1/teach/plan       # { persona_id, goal?, days? } → { plan }
GET  /api/v1/teach/plan/{id}  # → { plan with progress }
POST /api/v1/teach/execute    # { plan_id, step_index } → 执行当前教学步骤
```

**角色**：
```
GET    /api/v1/personas            # → [{ preset personas }]
GET    /api/v1/personas/custom     # → [{ user's custom personas }]
POST   /api/v1/personas            # { persona_data } → { persona }
PUT    /api/v1/personas/{id}       # { partial_persona } → { persona }
DELETE /api/v1/personas/{id}
```

**知识库**：
```
GET /api/v1/knowledge/lookup?word=hello     # → { word_entry }
GET /api/v1/knowledge/search?q=difference   # → [{ search_results }]
```

**用户画像**：
```
GET /api/v1/profile           # → { learning_profile }
PUT /api/v1/profile           # { partial_profile } → { profile }
GET /api/v1/profile/mistakes  # → [{ mistake_entries }]
```

**记忆**：
```
GET /api/v1/memory/emotions   # → [{ mood_events }]
GET /api/v1/memory/facts      # → [{ key_facts }]
GET /api/v1/memory/summary    # → { relationship_summary }
```

**WebSocket**：
```
WS /api/v1/voice/stream       # 双向音频流
```

### SSE 流式对话实现：
```python
@router.get("/chat/stream")
async def chat_stream(
    persona_id: str,
    message: str,
    user: User = Depends(get_current_user),
    agent: OrchestratorAgent = Depends(get_agent),
):
    async def event_generator():
        async for token in agent.run_stream(...):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"}  # 禁用 nginx 缓冲
    )
```

### 验证标准
- [x] 完整的认证流程（注册 → 登录 → 获取 token → 调用需认证的 API）
- [x] SSE 流式对话正确输出逐 token
- [x] WebSocket 端点可建立连接
- [x] 所有端点有正确的错误响应格式

---

## Phase 7：Flutter 移动端（预计 4-5 天）

### 目标
实现聊天界面 + 学习计划展示 + 角色选择 + 查词功能。

### 文件清单

```
mellow/mobile/
├── pubspec.yaml
├── lib/
│   ├── main.dart
│   ├── app.dart                     # MaterialApp + 路由
│   ├── config/
│   │   └── api_config.dart          # API base URL 配置
│   ├── models/
│   │   ├── user.dart                # User, Token
│   │   ├── persona.dart             # Persona
│   │   ├── message.dart             # ChatMessage
│   │   ├── learning_plan.dart       # WeeklyPlan
│   │   └── word_entry.dart          # WordEntry
│   ├── services/
│   │   ├── api_client.dart          # HTTP 客户端（Dio）
│   │   ├── auth_service.dart        # 认证服务
│   │   ├── chat_service.dart        # 对话 + SSE
│   │   ├── teach_service.dart       # 教学计划
│   │   ├── persona_service.dart     # 角色管理
│   │   └── knowledge_service.dart   # 查词
│   ├── providers/
│   │   ├── auth_provider.dart       # 认证状态（ChangeNotifier）
│   │   ├── chat_provider.dart       # 对话状态
│   │   └── persona_provider.dart    # 角色状态
│   ├── screens/
│   │   ├── login_screen.dart        # 登录/注册页
│   │   ├── persona_select_screen.dart  # 角色选择页
│   │   ├── chat_screen.dart         # 聊天主页
│   │   ├── plan_screen.dart         # 学习计划页
│   │   ├── profile_screen.dart      # 用户画像页
│   │   └── word_lookup_screen.dart  # 查词页
│   └── widgets/
│       ├── chat_bubble.dart         # 聊天气泡（支持 Markdown）
│       ├── persona_card.dart        # 角色卡片
│       ├── plan_card.dart           # 学习计划卡片
│       ├── typing_indicator.dart    # 打字中指示器
│       └── voice_button.dart        # 语音按钮（hold to talk）
```

### 关键实现

**SSE 流式对话**（`chat_service.dart`）：
```dart
Stream<String> chatStream(String personaId, String message) async* {
  final response = await _client.get(
    '/chat/stream',
    queryParameters: {'persona_id': personaId, 'message': message},
    options: Options(responseType: ResponseType.stream),
  );
  await for (final chunk in response.data.stream) {
    final line = utf8.decode(chunk);
    if (line.startsWith('data: ')) {
      final data = jsonDecode(line.substring(6));
      if (data['done']) break;
      yield data['token'];
    }
  }
}
```

**聊天界面**（`chat_screen.dart`）：
- 顶部：角色头像 + 名字
- 中间：消息列表（聊天气泡、打字指示器）
- 底部：文字输入 + 语音按钮
- 可选：学习计划入口按钮

### 验证标准
- [x] 完整的登录/注册流程
- [x] 角色选择页正确展示预设角色
- [x] SSE 流式对话实时显示
- [x] 学习计划正确渲染
- [x] 查词功能正常

---

## Phase 8：语音管道（预计 2-3 天）

### 目标
实现 WebSocket 双向音频流 + ASR/TTS 集成。

### 文件清单

```
backend/src/mellow/voice/
├── __init__.py
├── pipeline.py                   # VoicePipeline（WebSocket 管理 + 音频流处理）
└── implementations/
    ├── __init__.py
    └── volcano.py                # 火山引擎 ASR + TTS

backend/src/mellow/api/routes/
└── voice.py                      # WS /voice/stream 端点

mobile/lib/services/
└── voice_service.dart            # Flutter 端语音服务
```

### 关键实现

**VoicePipeline**（后端 WebSocket 处理）：
```python
class VoicePipeline:
    asr: ASRProvider
    tts: TTSProvider

    async def handle_stream(self, websocket: WebSocket, user: User, persona: Persona):
        """处理双向音频流"""
        await websocket.accept()
        audio_buffer = bytearray()

        async for message in websocket.iter_bytes():
            # 1. 接收音频 → ASR
            text = await self.asr.transcribe(message)
            if not text.strip():
                continue

            # 2. ASR 结果 → Agent
            response = await self.agent.run_text(text, user, persona)

            # 3. Agent 回复 → TTS
            audio = await self.tts.synthesize(response, voice=persona.voice_id)

            # 4. 文字 + 音频 → Flutter
            await websocket.send_json({"type": "text", "content": response})
            await websocket.send_bytes(audio)
```

**Flutter 端**（`voice_service.dart`）：
```dart
class VoiceService {
  WebSocketChannel? _channel;
  final _recorder = AudioRecorder();

  Future<void> connect(String token, String personaId) async {
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://$host/voice/stream?token=$token&persona_id=$personaId'),
    );
    _channel!.stream.listen(_handleMessage);
  }

  Future<void> startRecording() async {
    await _recorder.startStream(RecorderStream(stream: _channel!.sink));
  }

  void _handleMessage(dynamic data) {
    if (data is String) {
      // 文字转写结果
      final msg = jsonDecode(data);
      if (msg['type'] == 'text') {
        // 更新 UI 显示
      }
    } else {
      // 音频数据 → 播放
      _audioPlayer.play(data);
    }
  }
}
```

### 验证标准
- [x] WebSocket 连接成功，音频流双向传输
- [x] 按住说话 → 松开 → 文字显示 → 语音回复播放
- [x] 火山引擎 ASR 中英混合识别正确
- [x] 火山引擎 TTS 语音自然度可接受

---

## Phase 9：主动联系 + 定时任务（预计 1-2 天）

### 目标
实现定时器驱动的主动消息生成和投递。

### 文件清单

```
backend/src/mellow/memory/
└── proactive.py                  # ProactiveMessenger（含更新）

backend/
├── scheduler.py                  # APScheduler 或简单 asyncio 定时任务
└── main.py                       # 在 lifespan 中启动 scheduler
```

### 关键实现

**ProactiveMessenger** — 已 Phase 5 定义，Phase 9 重点是集成定时调度：
```python
# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=15)
async def check_proactive_messages():
    messenger = ProactiveMessenger()
    messages = await messenger.check_and_poke()
    for msg in messages:
        # 写入消息表
        await message_store.add_proactive_message(msg)

# main.py lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
```

### 验证标准
- [x] 定时器正确触发
- [x] 超时未互动的用户收到 LLM 生成的角色化消息
- [x] 消息风格匹配角色设定
- [x] 用户互动后倒计时正确重置

---

## Phase 10：测试 + 优化 + 部署（预计 2-3 天）

### 目标
单元测试、集成测试、性能优化、Docker 化部署。

### 文件清单

```
backend/tests/
├── __init__.py
├── conftest.py                    # pytest fixtures
├── test_config.py
├── test_llm/
│   └── test_client.py
├── test_agent/
│   ├── test_orchestrator.py
│   ├── test_chat_agent.py
│   └── test_teach_agent.py
├── test_knowledge/
│   └── test_open_english_dict.py
├── test_memory/
│   ├── test_learning_profile.py
│   └── test_persona_memory.py
├── test_api/
│   ├── test_auth.py
│   └── test_chat.py
└── test_persona/
    └── test_manager.py

backend/
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

### 测试重点
- Agent 意图识别准确率
- 学习计划生成的单词唯一性（不重复已掌握单词）
- 知识库查词正确性
- JWT 认证流程
- SSE 流式输出完整性

### 部署
- Docker Compose：FastAPI + 数据卷挂载
- 环境变量通过 `.env` 注入
- Caddy/Nginx 反向代理（生产环境）

---

## 总时间估算

| Phase | 内容 | 预计天数 |
|---|---|---|
| 1 | 项目骨架 | 1-2 |
| 2 | 核心抽象层 | 2-3 |
| 3 | Agent 引擎 | 3-4 |
| 4 | 角色 + 知识库 | 2-3 |
| 5 | 记忆系统 | 3-4 |
| 6 | API 层 | 2-3 |
| 7 | Flutter 移动端 | 4-5 |
| 8 | 语音管道 | 2-3 |
| 9 | 主动联系 | 1-2 |
| 10 | 测试 + 部署 | 2-3 |
| **合计** | | **22-32 天** |

MVP（Phase 1-6）可在 **12-18 天** 内交付一个具备角色扮演 + 教学计划 + 流式对话的后端。

---

## 架构全景图

```
┌──────────────────────────────────────────────────────────────────┐
│                        Flutter Mobile App                         │
│  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Login  │  │ Persona   │  │  Chat    │  │  Voice Button    │ │
│  │         │  │ Select    │  │  Screen  │  │  (Hold to Talk)  │ │
│  └────┬────┘  └─────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
└───────┼─────────────┼─────────────┼─────────────────┼───────────┘
        │   REST      │   REST      │   SSE           │  WebSocket
        ▼             ▼             ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Python)                      │
│                                                                   │
│  ┌─────────┐  ┌───────────┐  ┌────────────┐  ┌────────────────┐ │
│  │  Auth   │  │  Persona  │  │    Chat     │  │    Voice       │ │
│  │  JWT    │  │  Manager  │  │  (SSE)      │  │  Pipeline      │ │
│  └────┬────┘  └─────┬─────┘  └──────┬──────┘  └───────┬────────┘ │
│       │             │               │                  │          │
│       ▼             ▼               ▼                  ▼          │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                  Orchestrator Agent                       │    │
│  │  ┌──────────┐  ┌───────────┐  ┌───────────────┐         │    │
│  │  │  Chat    │  │  Teach    │  │   Reflect     │         │    │
│  │  │  Agent   │  │  Agent    │  │   Agent       │         │    │
│  │  └────┬─────┘  └─────┬─────┘  └───────┬───────┘         │    │
│  └───────┼──────────────┼────────────────┼──────────────────┘    │
│          │              │                │                        │
│  ┌───────┴──────────────┴────────────────┴──────────────────┐    │
│  │                    Core Services                          │    │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │    │
│  │  │  Memory  │  │ Knowledge │  │   Persona Manager    │  │    │
│  │  │  Engine  │  │ Provider  │  │                      │  │    │
│  │  └────┬─────┘  └─────┬─────┘  └──────────┬───────────┘  │    │
│  └───────┼──────────────┼────────────────────┼──────────────┘    │
│          │              │                    │                    │
│  ┌───────┴──────────────┴────────────────────┴──────────────┐    │
│  │                      Data Layer                           │    │
│  │  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │    │
│  │  │  SQLite  │  │   LanceDB    │  │  Open-English     │  │    │
│  │  │ (结构数据) │  │  (向量检索)   │  │  Dictionary       │  │    │
│  │  └──────────┘  └──────────────┘  └───────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │               External APIs (可选装)                       │    │
│  │  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │    │
│  │  │  LLM   │  │Embedding │  │   ASR    │  │    TTS     │ │    │
│  │  │Provider│  │ Provider │  │ Provider │  │  Provider  │ │    │
│  │  └────────┘  └──────────┘  └──────────┘  └────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```
