## Why

Mellow 后端从内存/JSON 存储迁移到 SQLite 持久化，并完成所有 P0-P3 功能实现。代码审查发现多处关键问题：Session 生命周期断裂导致数据写入静默丢失、Auth Provider 持有 stale session 导致全局认证失败、scheduler 引用已删除的 `_memories` 属性导致运行时崩溃、JWT 默认密钥 `change-me` 安全漏洞、知识库端点无认证、生词本缺少唯一约束等。

## What Changes

- **P0-1**: SQLite 持久化基础 + User/Auth 迁移（内存 dict → SQLAlchemy ORM + Repository）
- **P0-2**: Learning Profile 持久化（Pydantic → ORM + Repository + converter）
- **P0-3**: Persona Memory 持久化（同上模式）
- **P0-4**: Session Context 保持内存缓存（设计意图）
- **P0-5**: Vocabulary Book JSON→SQLite（完整重写路由）
- **P1**: 语义搜索（LanceDB + Embedding 优先，fallback SQL LIKE）
- **P2-1**: 主动消息消费端点 GET /memory/proactive
- **P2-2**: 学习计划 API（GET/PUT /profile/plan, POST /profile/plan/complete）
- **P2-3**: CEFR 历史进度追踪（CefrProgressRow ORM + Repository）
- **P2-4**: LLM 动态开场白（LLM 生成 + 硬编码 fallback）
- **P3-1**: ASR 火山引擎集成（HTTP API + 优雅降级）
- **P3-2**: TTS 火山引擎集成（HTTP API + 优雅降级）
- **修复**: Session 生命周期断裂 → 引入请求级 session 依赖注入（`get_db_session`）
- **修复**: Auth/Profile/Memory Provider stale session → JWTAuthProvider 改用 session_factory
- **修复**: scheduler.py `_memories` 引用 → 改用 DB 查询 `list_all()`
- **修复**: JWT 默认密钥 `change-me` → 空值时自动生成随机密钥 + 警告
- **修复**: 知识库端点无认证 → 添加 `get_current_user` 依赖
- **修复**: Vocabulary 唯一约束 → `UniqueConstraint('user_id', 'word')` + IntegrityError 处理
- **修复**: SQLite WAL 模式 → engine 添加 PRAGMA WAL + foreign_keys

## Capabilities

### New Capabilities
- `sqlite-persistence`: SQLite persistence via SQLAlchemy async with Repository pattern
- `session-lifecycle`: Request-scoped session management with auto commit/rollback
- `semantic-search`: Vector search with SQL fallback
- `proactive-messaging`: Proactive message consumption endpoint
- `learning-plan-api`: Learning plan CRUD endpoints
- `cefr-progress`: CEFR progress tracking with historical snapshots
- `dynamic-phrases`: LLM-generated opening phrases with fallback
- `volcano-asr-tts`: Volcano Engine ASR/TTS integration

### Modified Capabilities
- `vocabulary-book`: Migrated from JSON to SQLite with UniqueConstraint
- `auth-flow`: JWTAuthProvider now uses session_factory per-operation instead of stale session
- `chat-core`: Scheduler uses DB query instead of in-memory dict

## Impact

- **数据库**: 新增 5 张 ORM 表（users, learning_profiles, persona_memories, vocabulary_entries, cefr_progress）
- **API**: 新增 6 个端点，修改 3 个端点（phrases, knowledge, vocabulary）
- **依赖**: 新增 sqlalchemy, aiosqlite； volcanic ASR/TTS 使用 httpx
- **架构**: Repository pattern（abstract + SQLAlchemy impl），DI Container 注入 repos
- **测试**: 43 测试全部通过