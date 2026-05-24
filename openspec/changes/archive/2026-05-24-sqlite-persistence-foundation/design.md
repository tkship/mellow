## Context

Mellow 后端是一个 FastAPI 应用，当前所有数据存储在内存 dict 中。核心问题：

- `JWTAuthProvider._users: dict[str, dict]` 存储用户数据，进程重启即丢失
- `LearningProfileManager`、`PersonaMemoryManager` 等同样使用内存 dict
- `Settings.database_url` 已配置为 `sqlite+aiosqlite:///./data/mellow.db`，但无代码使用
- `pyproject.toml` 已声明 `sqlalchemy[asyncio]>=2.0.36` 和 `aiosqlite>=0.20.0` 依赖

当前架构采用 Provider 抽象模式（`mellow/providers/`），每个模块有抽象接口和具体实现。DI 容器（`mellow/di.py:Container`）通过 `_lazy()` 惰性初始化并缓存实例。`JWTAuthProvider.__init__` 已预留 `user_repo=None` 参数，注释标注 "Phase 5: UserRepository"。

本变更仅覆盖基础设施 + 用户/认证迁移，其他模块（profile、memory、vocabulary 等）在后续变更中逐步迁移。

## Goals / Non-Goals

**Goals:**
- 建立 SQLAlchemy async 引擎和 session 管理基础设施，供所有模块复用
- 建立 Repository 模式数据访问层，为后续模块迁移提供统一范式
- 将用户数据从 `JWTAuthProvider._users` 内存 dict 迁移到 SQLite
- 保持所有 REST API 接口和响应格式完全不变
- 应用启动时自动创建数据库表（无需手动迁移）

**Non-Goals:**
- 不迁移 learning_profile、persona_memory、vocabulary 等模块（后续变更）
- 不引入 Alembic 迁移框架（当前无生产数据，`create_all` 足够；后续有生产数据时再引入）
- 不实现数据库连接池调优（SQLite 单文件场景无需连接池配置）
- 不修改前端代码或 API 接口

## Decisions

### D1: 使用 SQLAlchemy 2.0 async 声明式映射

**选择**: SQLAlchemy 2.0+ `DeclarativeBase` + `Mapped` + `mapped_column` 类型注解风格

**替代方案**:
- (A) SQLAlchemy 1.4 旧式 `Column()` 声明 — 已过时，2.0 风格更类型安全
- (B) raw aiosqlite — 需要手写 SQL、无迁移路径、无类型安全
- (C) Tortoise ORM — 社区较小、与已有 SQLAlchemy 依赖冲突

**理由**: 项目已依赖 `sqlalchemy[asyncio]>=2.0.36`，2.0 风格提供更好的类型提示和 IDE 支持，且是 SQLAlchemy 官方推荐方式。

### D2: Repository 模式作为数据访问层

**选择**: 定义抽象 `Repository[T]` 基类 + 具体 `UserRepository` 实现，通过 DI 注入到 `JWTAuthProvider`

**替代方案**:
- (A) 直接在 `JWTAuthProvider` 中使用 `AsyncSession` — 耦合 ORM 实现细节到业务逻辑
- (B) Unit of Work 模式 — 对当前规模过度设计
- (C) 保持 dict 接口但底层用 SQLAlchemy — 类型不安全，无法利用 ORM 优势

**理由**: Repository 模式将数据访问逻辑与业务逻辑解耦，便于测试（可 mock repository），且为后续模块迁移提供统一范式。`JWTAuthProvider.__init__` 已预留 `user_repo` 参数。

### D3: 应用启动时 `create_all` 建表

**选择**: 在 FastAPI `lifespan` 事件中调用 `Base.metadata.create_all(engine)` 自动建表

**替代方案**:
- (A) Alembic 迁移 — 当前无生产数据，引入 Alembic 增加复杂度无实际收益
- (B) 手动 SQL 脚本 — 不可维护、无版本控制

**理由**: 项目处于开发阶段，无生产数据需要迁移。`create_all` 简单可靠，后续引入 Alembic 时可平滑过渡（Alembic 可从现有模型生成初始迁移）。

### D4: Session 管理使用 async context manager

**选择**: 提供 `async_session_factory()` 生成 `AsyncSession`，通过 `async with` 管理 session 生命周期

**理由**: 这是 SQLAlchemy async 的标准模式，确保 session 在请求结束时正确关闭，避免连接泄漏。

### D5: 数据库初始化放在 `mellow.db` 包

**选择**: 新建 `mellow/db/` 包，包含 `engine.py`（引擎和 session 工厂）、`base.py`（DeclarativeBase）、`models/`（ORM 模型）、`repos/`（Repository 实现）

**理由**: 集中管理数据库基础设施，与业务模块（auth、memory 等）分离。ORM 模型按领域组织但统一注册到 `Base`。

### D6: `Container` 中注入 `UserRepository` 到 `JWTAuthProvider`

**选择**: 修改 `Container.auth()` 方法，先创建 `AsyncSession` 工厂和 `UserRepository`，再传入 `JWTAuthProvider`

**理由**: `JWTAuthProvider.__init__` 已预留 `user_repo` 参数，只需在 DI 容器中完成注入。保持 `AuthProvider` 接口不变。

## Risks / Trade-offs

- **[SQLite 并发写入限制]** → SQLite 单写者模型，WAL 模式下读写可并发。Mellow 是单用户教学应用，并发写入压力极低。通过 `connect_args={"check_same_thread": False}` 和 WAL 模式缓解。

- **[create_all 不支持 schema 变更]** → 首次部署后如需修改表结构，`create_all` 不会 alter 已有表。缓解：当前无生产数据，开发阶段可删库重建；后续引入 Alembic 管理迁移。

- **[Repository 抽象层增加代码量]** → 每个实体需要 Interface + Implementation 两个文件。但这是必要的解耦，且为测试和后续迁移提供基础。

- **[JWTAuthProvider 重构可能引入回归]** → 通过保持 `AuthProvider` 接口不变 + 现有 API 测试覆盖来缓解。所有 API 端点签名和响应格式不变。

## Migration Plan

1. 部署：首次启动时 `lifespan` 自动创建 `data/mellow.db` 和表
2. 无需数据迁移：当前无生产数据
3. 回滚：删除 `data/mellow.db` 文件即可恢复到空状态；代码回滚到旧版本后内存存储自动恢复
4. 后续：引入 Alembic 时，从当前 ORM 模型生成初始迁移脚本

## Open Questions

- 是否需要在 `Settings` 中增加 `database_echo: bool = False` 控制 SQL 日志？（建议：是，开发调试有用，默认关闭）
- `UserRepository` 是否需要 `soft_delete`（`is_active=False`）支持？（建议：暂不需要，`is_active` 字段已存在于当前模型）