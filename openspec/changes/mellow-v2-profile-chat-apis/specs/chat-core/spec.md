## ADDED Requirements

### Requirement: 聊天页历史消息加载集成
系统 SHALL 在聊天页实现历史消息的分页加载，与后端 `GET /chat/history` 对接。

#### Scenario: 聊天页初始加载
- **WHEN** 用户进入聊天页
- **THEN** 系统调用 `GET /api/v1/chat/history?persona_id={id}&limit=20`，按正序渲染历史消息（旧消息在上，新消息在下）

#### Scenario: 上滑加载更多
- **WHEN** 用户滑动到消息列表顶部并继续上滑
- **THEN** 系统调用下一页 API（`cursor={last_id}`），将更早消息 prepend 到列表顶部

#### Scenario: 发送新消息后历史一致性
- **WHEN** 用户在已有历史消息的会话中发送新消息
- **THEN** 新消息正常追加到列表底部，不影响已加载的历史消息
