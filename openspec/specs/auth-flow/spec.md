# auth-flow Specification

## Purpose
TBD - created by archiving change mellow-frontend. Update Purpose after archive.
## Requirements
### Requirement: 用户注册
系统 SHALL 允许新用户通过用户名和密码注册账号。

#### Scenario: 注册成功
- **WHEN** 用户输入有效用户名（≥3 字符）和密码（≥6 字符）并提交
- **THEN** 系统调用 `POST /api/v1/auth/register`，成功后自动登录并跳转角色选择页

#### Scenario: 注册验证失败
- **WHEN** 用户输入的用户名不足 3 字符或密码不足 6 字符
- **THEN** 系统在客户端显示红色验证错误，不发起网络请求

#### Scenario: 用户名已存在
- **WHEN** 后端返回 409 Conflict
- **THEN** 系统在表单显示"用户名已被使用"错误提示

### Requirement: 用户登录
系统 SHALL 允许已注册用户通过用户名和密码登录。

#### Scenario: 登录成功
- **WHEN** 用户输入正确的用户名和密码并提交
- **THEN** 系统调用 `POST /api/v1/auth/login`，存储 `access_token`/`refresh_token` 到 SharedPreferences，跳转聊天页

#### Scenario: 登录失败
- **WHEN** 后端返回 401 Unauthorized
- **THEN** 系统显示"用户名或密码错误"提示

### Requirement: 自动登录检测
系统 SHALL 在启动时自动检测已存储的 JWT Token 有效性。

#### Scenario: Token 有效
- **WHEN** 启动时 SharedPreferences 中存在 token 且 `GET /api/v1/auth/me` 返回 200
- **THEN** 系统跳过登录页，直接进入聊天页

#### Scenario: Token 过期
- **WHEN** 启动时 token 存在但 `/auth/me` 返回 401 且 refresh 也失败
- **THEN** 系统清除本地 token，显示启动页

#### Scenario: 无 Token
- **WHEN** 启动时 SharedPreferences 中无 token
- **THEN** 系统显示启动页，"开始"按钮跳转登录页

### Requirement: JWT Token 刷新
系统 SHALL 在 API 请求返回 401 时自动尝试刷新 Token。

#### Scenario: 刷新成功
- **WHEN** API 请求返回 401 且 `POST /api/v1/auth/refresh` 返回新 token
- **THEN** 系统更新本地 token 并重试原请求

#### Scenario: 刷新失败
- **WHEN** API 请求返回 401 且 refresh 也失败
- **THEN** 系统清除 token，跳转登录页

### Requirement: 退出登录
系统 SHALL 允许用户退出登录。

#### Scenario: 退出确认
- **WHEN** 用户在设置页点击"退出登录"并确认
- **THEN** 系统清除 SharedPreferences 中的 token，跳转登录页

