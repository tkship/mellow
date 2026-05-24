## Why

Mellow 后端当前将所有数据（用户、学习档案、记忆、会话、词汇）存储在内存 dict 中，服务重启即丢失全部数据。配置文件 `config.py` 已声明 `database_url = "sqlite+aiosqlite:///./data/mellow.db"`，`pyproject.toml` 已依赖 `sqlalchemy[asyncio]` 和 `aiosqlite`，但没有任何代码实际使用它们。这是生产不可用的根本阻塞项——必须先建立持久化基础设施，才能逐步迁移各模块。

## What Changes

- 新增 SQLAlchemy async engine + session 管理基础设施（`mellow.db` 包）
- 新增 Repository 模式的数据访问层，为所有模块提供统一的持久化抽象
- 新增 `User` ORM 模型，将 `jwt_auth.py` 中 `self._users: dict[str, dict]` 内存存储迁移到 SQLite
- 新增 `UserRepository` 接口与实现，供 `JWTAuthProvider` 注入使用
- 修改 `JWTAuthProvider`：移除 `self._users` / `self._lock`，改为通过 `UserRepository` 访问数据
- 修改 `Container`（`di.py`）：初始化数据库引擎、注入 `UserRepository` 到 `JWTAuthProvider`
- 新增数据库迁移机制（Alembic 或手动 `create_all`），确保首次启动自动建表
- 应用启动时自动创建 `data/` 目录和数据库文件

## Capabilities

### New Capabilities
- `db-foundation`: SQLAlchemy async 引擎、session 管理、Base 模型、数据库初始化与迁移机制
- `user-repository`: 用户数据的 Repository 接口与 SQLite 实现，替代内存 dict 存储

### Modified Capabilities
- `auth-flow`: 用户注册/登录/验证的数据存储从内存 dict 变更为 SQLite 持久化（行为不变，实现变更）

## Impact

- **代码变更**: `mellow/db/`（新增包）、`mellow/auth/jwt_auth.py`（重构数据访问）、`mellow/di.py`（注入依赖）、`mellow/main.py` 或应用启动钩子（初始化数据库）
- **API 影响**: 无——所有 REST API 接口和响应格式保持不变
- **依赖**: 已有 `sqlalchemy[asyncio]>=2.0.36` 和 `aiosqlite>=0.20.0`，无需新增依赖
- **数据迁移**: 首次部署为空库，无需从旧数据迁移（当前无生产数据）
- **部署影响**: 需确保 `data/` 目录可写；SQLite 文件路径由 `Settings.database_url` 控制