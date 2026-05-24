## ADDED Requirements

### Requirement: 角色主动消息展示
系统 SHALL 在聊天界面展示角色主动发起的消息。

#### Scenario: 加载主动消息
- **WHEN** 用户进入聊天页面
- **THEN** 系统调用 `GET /api/v1/memory/proactive?persona_id={currentPersonaId}`，若返回 `messages` 非空，在聊天消息列表顶部以横幅（Banner）形式展示最新一条主动消息

#### Scenario: 主动消息横幅
- **WHEN** 存在未读主动消息
- **THEN** 系统在聊天区域顶部显示可关闭横幅，内容为消息文本，右侧显示"查看"和"关闭"按钮，左侧显示角色头像

#### Scenario: 点击查看
- **WHEN** 用户点击横幅"查看"按钮
- **THEN** 系统将主动消息内容作为 AI 消息插入聊天列表，并关闭横幅

#### Scenario: 关闭横幅
- **WHEN** 用户点击横幅"关闭"按钮
- **THEN** 系统关闭横幅，本次会话不再显示该消息

#### Scenario: 无主动消息
- **WHEN** 主动消息接口返回空列表或 `count: 0`
- **THEN** 系统不显示横幅