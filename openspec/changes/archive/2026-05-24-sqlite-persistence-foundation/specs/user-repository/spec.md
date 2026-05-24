## ADDED Requirements

### Requirement: UserRepository 抽象接口
系统 SHALL 定义 `UserRepository` 抽象接口，提供用户数据的 CRUD 操作。

接口方法：
- `get_by_username(username: str) -> UserRow | None` — 按用户名查找
- `get_by_id(user_id: str) -> UserRow | None` — 按 ID 查找
- `create(username: str, password_hash: str) -> UserRow` — 创建用户
- `update_active(user_id: str, is_active: bool) -> UserRow` — 更新活跃状态

#### Scenario: 接口定义
- **WHEN** 定义 `UserRepository` 抽象基类
- **THEN** 包含上述四个抽象方法，所有方法为 `async`

### Requirement: SQLAlchemy UserRepository 实现
系统 SHALL 提供 `SqlAlchemyUserRepository` 实现，使用 SQLAlchemy `AsyncSession` 访问 SQLite 数据库。

#### Scenario: 创建用户
- **WHEN** 调用 `create(username, password_hash)`
- **THEN** 系统生成 UUID 作为 `id`，设置 `created_at` 为当前 UTC 时间，`is_active` 为 `True`，将记录插入 `users` 表并返回 `UserRow`

#### Scenario: 创建重复用户名
- **WHEN** 调用 `create` 时 `username` 已存在于数据库
- **THEN** 数据库 UNIQUE 约束触发，Repository 抛出 `ConflictError`

#### Scenario: 按用户名查找
- **WHEN** 调用 `get_by_username(username)`
- **THEN** 返回匹配的 `UserRow`，不存在时返回 `None`

#### Scenario: 按 ID 查找
- **WHEN** 调用 `get_by_id(user_id)`
- **THEN** 返回匹配的 `UserRow`，不存在时返回 `None`

#### Scenario: 更新活跃状态
- **WHEN** 调用 `update_active(user_id, is_active)`
- **THEN** 更新指定用户的 `is_active` 字段并返回更新后的 `UserRow`；用户不存在时抛出 `NotFoundError`

### Requirement: User ORM 模型
系统 SHALL 定义 `UserRow` ORM 模型（`mellow.db.models.user`），映射到 `users` 表。

字段：
- `id: str` — 主键，UUID 格式
- `username: str` — 唯一索引，不区分大小写存储（存储前 lower+strip）
- `password_hash: str` — PBKDF2-SHA256 哈希
- `is_active: bool` — 默认 `True`
- `created_at: datetime` — 默认 UTC 当前时间

#### Scenario: 表结构
- **WHEN** `create_all` 执行
- **THEN** 创建 `users` 表，包含 `id`（PRIMARY KEY）、`username`（UNIQUE）、`password_hash`、`is_active`、`created_at` 列

#### Scenario: 用户名唯一约束
- **WHEN** 尝试插入相同 `username` 的记录
- **THEN** 数据库拒绝插入并抛出 `IntegrityError`

### Requirement: UserRow 到 UserInfo 转换
系统 SHALL 提供 `UserRow` 到 `UserInfo`（`mellow.providers.auth.UserInfo`）的转换方法。

#### Scenario: 转换
- **WHEN** 调用 `user_row.to_user_info()`
- **THEN** 返回 `UserInfo(id=user_row.id, username=user_row.username, is_active=user_row.is_active)`