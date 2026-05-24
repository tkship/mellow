## ADDED Requirements

### Requirement: 消息长按操作菜单
系统 SHALL 支持通过长按消息气泡触发操作菜单。

#### Scenario: 长按弹出菜单
- **WHEN** 用户长按聊天消息气泡（AI 或用户消息均可）
- **THEN** 系统弹出 BottomSheet 菜单，包含：收藏/取消收藏、复制文字、删除（仅限自己发送的消息不显示删除选项对AI消息也显示删除）

#### Scenario: 菜单收藏操作
- **WHEN** 用户在长按菜单中选择"收藏"
- **THEN** 系统调用 `PUT /api/v1/chat/messages/{id}/favorite?persona_id={currentPersonaId}`，乐观更新本地消息 `isFavorite` 状态，成功后消息气泡右下角显示金色星星图标；API 失败时回滚并显示 Toast 错误提示

#### Scenario: 菜单取消收藏操作
- **WHEN** 用户在长按菜单中选择"取消收藏"（已收藏消息）
- **THEN** 系统调用 `PUT /api/v1/chat/messages/{id}/favorite?persona_id={currentPersonaId}`（API 为 toggle 语义），乐观更新本地消息取消收藏状态，成功后移除金色星星图标；API 失败时回滚

#### Scenario: 菜单删除操作
- **WHEN** 用户在长按菜单中选择"删除"
- **THEN** 系统弹出确认对话框"确定删除这条消息吗？"，用户确认后调用 `DELETE /api/v1/chat/messages/{id}?persona_id={currentPersonaId}`，乐观更新从消息列表移除该条；API 失败时恢复消息并显示 Toast 错误提示

#### Scenario: 菜单复制操作
- **WHEN** 用户在长按菜单中选择"复制文字"
- **THEN** 系统将消息文本复制到剪贴板，显示 Toast"已复制"