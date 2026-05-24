## ADDED Requirements

### Requirement: 数据库引擎初始化
系统 SHALL 在应用启动时根据 `Settings.database_url` 创建 SQLAlchemy async engine，并配置 WAL 模式和线程安全参数。

#### Scenario: 首次启动创建数据库
- **WHEN** 应用启动且 `data/mellow.db` 文件不存在
- **THEN** 系统自动创建 `data/` 目录和数据库文件，并初始化所有表结构

#### Scenario: 后续启动复用数据库
- **WHEN** 应用启动且 `data/mellow.db` 文件已存在
- **THEN** 系统复用现有数据库文件，不重建表结构（`create_all` 跳过已存在的表）

### Requirement: Async Session 工厂
系统 SHALL 提供 `async_session_factory()` 函数，返回 `async_sessionmaker` 实例，用于创建 `AsyncSession`。

#### Scenario: 创建 session
- **WHEN** 调用 `async_session_factory()` 获取 session 工厂
- **THEN** 返回的 session 工厂可生成 `AsyncSession` 实例，且 session 在 `async with` 块结束时自动关闭

#### Scenario: Session 生命周期管理
- **WHEN** Repository 方法执行数据库操作
- **THEN** 操作在 `async with session:` 上下文中执行，异常时自动回滚，正常结束时 commit

### Requirement: DeclarativeBase 定义
系统 SHALL 在 `mellow.db.base` 中定义 `Base = DeclarativeBase`，所有 ORM 模型 MUST 继承此 Base。

#### Scenario: 模型注册
- **WHEN** 定义新的 ORM 模型类并继承 `Base`
- **THEN** 模型自动注册到 `Base.metadata`，`create_all` 时自动创建对应表

### Requirement: 数据库初始化钩子
系统 SHALL 在 FastAPI `lifespan` 上下文中调用数据库初始化，确保引擎和表在请求处理前就绪。

#### Scenario: Lifespan 启动
- **WHEN** FastAPI 应用启动
- **THEN** 在处理任何请求之前，数据库引擎已创建、表结构已初始化

#### Scenario: Lifespan 关闭
- **WHEN** FastAPI 应用关闭
- **THEN** 数据库引擎连接池正确释放

### Requirement: 数据库配置项
系统 SHALL 在 `Settings` 中支持以下数据库相关配置：

- `database_url: str` — 数据库连接字符串（已有）
- `database_echo: bool = False` — 是否输出 SQL 日志

#### Scenario: 默认配置
- **WHEN** 未设置环境变量
- **THEN** `database_url` 默认为 `sqlite+aiosqlite:///./data/mellow.db`，`database_echo` 默认为 `False`

#### Scenario: 自定义配置
- **WHEN** 通过环境变量设置 `DATABASE_URL` 和 `DATABASE_ECHO`
- **THEN** 系统使用环境变量指定的值