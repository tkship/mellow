# message-persistent-actions Specification

## Purpose
TBD - created by archiving change mellow-v2-profile-chat-apis. Update Purpose after archive.
## Requirements
### Requirement: 后端提供消息收藏持久化
系统 SHALL 提供收藏/取消收藏单条消息的 API，收藏状态持久化到后端。

#### Scenario: 收藏消息
- **WHEN** 前端请求 `PUT /api/v1/chat/messages/{id}/favorite`
- **THEN** 系统将该消息标记为收藏，返回更新后的消息对象（`is_favorite: true`）

#### Scenario: 取消收藏消息
- **WHEN** 前端对已收藏消息再次请求 `PUT /api/v1/chat/messages/{id}/favorite`
- **THEN** 系统将该消息标记为未收藏，返回更新后的消息对象（`is_favorite: false`）

#### Scenario: 收藏不存在消息
- **WHEN** 前端请求收藏一条不存在的消息 ID
- **THEN** 系统返回 404 Not Found

### Requirement: 后端提供消息删除
系统 SHALL 提供删除单条消息的 API。

#### Scenario: 删除消息
- **WHEN** 前端请求 `DELETE /api/v1/chat/messages/{id}`
- **THEN** 系统从存储中移除该消息，返回 204 No Content

#### Scenario: 删除不存在消息
- **WHEN** 前端请求删除一条不存在的消息 ID
- **THEN** 系统返回 404 Not Found

### Requirement: 前端消息收藏持久化集成
系统 SHALL 将前端消息收藏操作从本地状态改为调用后端 API。

#### Scenario: 右滑收藏消息
- **WHEN** 用户右滑消息气泡超过阈值
- **THEN** 系统先本地更新状态（乐观更新），调用 `PUT /chat/messages/{id}/favorite`，成功后保持状态；失败时回滚并显示 SnackBar 提示

#### Scenario: 长按菜单收藏
- **WHEN** 用户长按消息气泡并选择"收藏"
- **THEN** 系统调用后端 API 更新收藏状态，更新 UI 显示金色星星

### Requirement: 前端消息删除持久化集成
系统 SHALL 将前端消息删除操作从本地状态改为调用后端 API。

#### Scenario: 左滑删除消息
- **WHEN** 用户左滑消息气泡超过阈值
- **THEN** 系统先本地移除消息（乐观更新），调用 `DELETE /chat/messages/{id}`，成功后保持移除；失败时回滚并显示 SnackBar 提示

#### Scenario: 长按菜单删除
- **WHEN** 用户长按消息气泡并选择"删除"
- **THEN** 系统调用后端 API 删除消息，从列表移除并显示删除确认 SnackBar

