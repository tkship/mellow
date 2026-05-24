## ADDED Requirements

### Requirement: 角色语音试听
系统 SHALL 在角色选择页提供语音试听功能。

#### Scenario: 试听按钮展示
- **WHEN** 用户查看角色卡片或选中角色详情区域
- **THEN** 系统在每个角色卡片底部显示"试听声音"按钮（喇叭图标 + 文字）

#### Scenario: 点击试听
- **WHEN** 用户点击"试听声音"按钮
- **THEN** 系统使用 `getPersonaVoiceUrl(personaId)` 构建 URL（`/api/v1/personas/{id}/voice`），创建 `<audio>` 元素播放 MP3 音频，按钮状态变为"播放中"（脉冲动画）

#### Scenario: 试听完成
- **WHEN** 音频播放完毕
- **THEN** 系统将按钮状态恢复为"试听声音"

#### Scenario: 语音不可用
- **WHEN** 音频请求返回 404 或加载失败
- **THEN** 系统显示 Toast 提示"该角色暂无配音"，按钮恢复默认状态

#### Scenario: 切换角色试听
- **WHEN** 用户在播放中点击其他角色的试听按钮
- **THEN** 系统停止当前播放，开始播放新角色的语音