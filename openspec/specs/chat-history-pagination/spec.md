# chat-history-pagination Specification

## Purpose
TBD - created by archiving change mellow-v2-profile-chat-apis. Update Purpose after archive.
## Requirements
### Requirement: 后端提供对话历史分页查询
系统 SHALL 提供分页查询指定用户与角色的对话历史接口。

#### Scenario: 首次加载历史消息
- **WHEN** 前端请求 `GET /api/v1/chat/history?persona_id=abc&limit=20`
- **THEN** 系统返回该用户与该角色最近 20 条消息，按时间倒序排列，包含 `messages` 数组和 `next_cursor`（用于下一页）

#### Scenario: 加载更多历史消息
- **WHEN** 前端请求 `GET /api/v1/chat/history?persona_id=abc&limit=20&cursor=<last_message_id>`
- **THEN** 系统返回该用户与该角色在 `cursor` 之前的 20 条更早消息

#### Scenario: 无更多历史消息
- **WHEN** 前端请求分页且数据库中无更早消息
- **THEN** 系统返回空数组，`next_cursor` 为 `null`

### Requirement: 前端集成历史消息分页加载
系统 SHALL 在聊天页支持上滑加载更多历史消息。

#### Scenario: 进入聊天页加载历史
- **WHEN** 用户进入聊天页
- **THEN** 系统自动调用 `GET /chat/history` 加载最近消息，渲染到列表顶部（按正序排列）

#### Scenario: 上滑加载更多
- **WHEN** 用户滑动到列表顶部并继续上滑
- **THEN** 系统显示加载指示器，调用下一页 API，将更早消息插入列表顶部

#### Scenario: 发送新消息后滚动
- **WHEN** 用户发送新消息
- **THEN** 列表自动滚动到底部，新消息正常参与 SSE 流式渲染

