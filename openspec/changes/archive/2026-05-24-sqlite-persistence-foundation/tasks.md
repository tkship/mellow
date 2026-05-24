## 1. 数据库基础设施

- [x] 1.1 创建 `backend/src/mellow/db/__init__.py` 包，导出 `get_engine`、`get_session_factory`、`init_db`
- [x] 1.2 创建 `backend/src/mellow/db/base.py`，定义 `Base = DeclarativeBase` 和 `TimestampMixin`
- [x] 1.3 创建 `backend/src/mellow/db/engine.py`，实现 `get_engine(settings)` 和 `get_session_factory(engine)` 函数，配置 SQLite WAL 模式和 `check_same_thread=False`
- [x] 1.4 创建 `backend/src/mellow/db/init_db.py`，实现 `init_db(engine)` 函数，调用 `Base.metadata.create_all` 并确保 `data/` 目录存在
- [x] 1.5 在 `backend/src/mellow/config.py` 的 `Settings` 中添加 `database_echo: bool = False` 配置项

## 2. User ORM 模型

- [x] 2.1 创建 `backend/src/mellow/db/models/__init__.py`，导入并注册所有模型
- [x] 2.2 创建 `backend/src/mellow/db/models/user.py`，定义 `UserRow` ORM 模型：`id`(str PK)、`username`(str UNIQUE)、`password_hash`(str)、`is_active`(bool default True)、`created_at`(datetime default utcnow)
- [x] 2.3 在 `UserRow` 上实现 `to_user_info() -> UserInfo` 方法，转换为 `mellow.providers.auth.UserInfo`

## 3. UserRepository 接口与实现

- [x] 3.1 创建 `backend/src/mellow/db/repos/__init__.py`
- [x] 3.2 创建 `backend/src/mellow/db/repos/user_repo.py`，定义 `UserRepository` 抽象基类（`get_by_username`、`get_by_id`、`create`、`update_active` 四个 async 抽象方法）
- [x] 3.3 在同一文件实现 `SqlAlchemyUserRepository`，通过 `AsyncSession` 执行数据库操作，`create` 时处理 `IntegrityError` 转为 `ConflictError`，`update_active` 时用户不存在抛 `NotFoundError`

## 4. JWTAuthProvider 重构

- [x] 4.1 修改 `backend/src/mellow/auth/jwt_auth.py`：移除 `self._users`、`self._lock`，将 `user_repo` 参数类型从 `None` 改为 `UserRepository`
- [x] 4.2 重写 `JWTAuthProvider.register()`：调用 `self._user_repo.create(username, password_hash)`，捕获 `ConflictError` 向上传播
- [x] 4.3 重写 `JWTAuthProvider.login()`：调用 `self._user_repo.get_by_username(username)` 查找用户，验证密码哈希
- [x] 4.4 重写 `JWTAuthProvider.verify_token()`：解码 JWT 后调用 `self._user_repo.get_by_username()` 查找用户
- [x] 4.5 重写 `JWTAuthProvider.refresh_token()`：解码 refresh token 后调用 `self._user_repo.get_by_id()` 查找用户

## 5. DI 容器集成

- [x] 5.1 修改 `backend/src/mellow/di.py`：添加 `_db_engine` 和 `_session_factory` 惰性属性
- [x] 5.2 修改 `backend/src/mellow/di.py`：添加 `session()` 方法返回 `AsyncSession`
- [x] 5.3 修改 `backend/src/mellow/di.py`：添加 `user_repo()` 方法创建 `SqlAlchemyUserRepository`
- [x] 5.4 修改 `backend/src/mellow/di.py` 的 `auth()` 方法：注入 `UserRepository` 到 `JWTAuthProvider`

## 6. 应用启动集成

- [x] 6.1 修改 `backend/src/mellow/main.py`（或应用入口）：在 FastAPI `lifespan` 中调用 `init_db(engine)` 初始化数据库
- [x] 6.2 在 `lifespan` 关闭时调用 `engine.dispose()` 释放连接

## 7. 测试

- [x] 7.1 创建 `backend/tests/test_db/test_engine.py`：测试引擎创建、session 工厂、WAL 模式配置
- [x] 7.2 创建 `backend/tests/test_db/test_user_repo.py`：测试 `SqlAlchemyUserRepository` 的 CRUD 操作（创建、查询、重复用户名、更新活跃状态、用户不存在）
- [x] 7.3 创建 `backend/tests/test_db/test_auth_integration.py`：测试 `JWTAuthProvider` 通过 `UserRepository` 的注册、登录、验证、刷新流程