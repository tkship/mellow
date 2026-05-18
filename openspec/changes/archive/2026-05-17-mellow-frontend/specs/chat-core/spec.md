## ADDED Requirements

### Requirement: 聊天主界面
系统 SHALL 在聊天页展示对话历史和新消息。

#### Scenario: 空状态展示
- **WHEN** 用户进入聊天页且无历史消息
- **THEN** 系统显示 MellowLogo、问候语"和 {name} 说点什么吧~"和快捷开场白气泡

#### Scenario: 快捷开场白
- **WHEN** 聊天页加载
- **THEN** 系统调用 `GET /api/v1/chat/phrases?persona_id=` 获取动态开场白列表

### Requirement: SSE 流式对话
系统 SHALL 通过 SSE 流式接收 AI 回复并逐字显示。

#### Scenario: 发送消息
- **WHEN** 用户输入文字并点击发送按钮
- **THEN** 系统立即显示用户消息气泡，调用 `GET /api/v1/chat/stream?persona_id=&message=`，逐 token 渲染 AI 回复气泡

#### Scenario: 流式输出指示
- **WHEN** AI 正在生成回复
- **THEN** 消息气泡显示 TypingIndicator（三点跳动动画）

#### Scenario: 流式完成
- **WHEN** 收到 SSE `{"done": true}` 事件
- **THEN** 系统停止流式动画，标记消息为完整状态

#### Scenario: 流式连接中断
- **WHEN** SSE 连接异常断开
- **THEN** 系统显示"连接中断"提示和重试按钮

### Requirement: 消息气泡渲染
系统 SHALL 区分 AI 消息和用户消息的气泡样式。

#### Scenario: AI 消息气泡
- **WHEN** 渲染 AI 消息
- **THEN** 左对齐，shadcn muted 背景 + mutedForeground 文字，16px 圆角（左上直角），AI emoji 头像

#### Scenario: 用户消息气泡
- **WHEN** 渲染用户消息
- **THEN** 右对齐，品牌绿 #5BC91A 背景 + 白色文字，16px 圆角（右上直角），用户图标头像

#### Scenario: 收藏消息标识
- **WHEN** 消息已被收藏
- **THEN** 气泡右下角显示金色星星 ⭐

### Requirement: 消息发送
系统 SHALL 支持文字输入和发送。

#### Scenario: 发送按钮状态
- **WHEN** 输入框为空
- **THEN** 发送按钮为灰色不可点击状态
- **WHEN** 输入框有文字
- **THEN** 发送按钮变为品牌绿高亮可点击状态

#### Scenario: 消息滚动
- **WHEN** 新消息到达
- **THEN** 列表自动滚动到底部

#### Scenario: 上滑加载更多
- **WHEN** 用户滑动到列表顶部
- **THEN** 系统加载更早的历史消息（分页）
