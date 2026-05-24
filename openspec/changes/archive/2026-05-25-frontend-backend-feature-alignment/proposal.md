## Why

前端已适配了大部分后端 API，但审计发现 6 处后端功能前端未接入或缺少 UI 交互入口，导致用户无法使用这些能力：聊天消息收藏/删除无交互入口、学习计划无 UI、自定义角色未接入、主动消息未接入、角色语音 URL 未调用、语音通话为纯占位页。

## What Changes

- **聊天消息收藏/删除交互**：ChatView 中为消息添加长按菜单（收藏/取消收藏、复制、删除）和滑动快捷操作（右滑收藏、左滑删除），调用 `toggleMessageFavorite` 和 `deleteMessage` API，乐观更新 + 失败回滚
- **学习计划页面**：在 LearnView 或独立页面中添加学习计划模块，调用 `GET /profile/plan` 展示当前计划，调用 `PUT /profile/plan` 设置计划，调用 `POST /profile/plan/complete` 完成每日任务
- **自定义角色列表**：GuideSelectView 中增加"自定义角色"分区，调用 `GET /personas/custom` 加载用户自建角色
- **主动消息展示**：在 ChatView 或独立入口中展示角色主动消息，调用 `GET /memory/proactive`
- **角色语音试听**：角色详情/选择页面增加"试听声音"按钮，调用 `getPersonaVoiceUrl` 构建 URL 并播放
- **语音通话占位完善**：VoiceCallView 保持占位但明确标注"功能开发中"，点击麦克风按钮统一为提示弹窗（去除 `alert()`）

## Capabilities

### New Capabilities
- `message-persistent-actions`: 消息收藏/删除的 UI 交互入口 + 乐观更新 + API 集成
- `learning-plan`: 学习计划的查看、设置、完成 UI + API 集成
- `custom-personas`: 自定义角色列表加载与展示
- `proactive-messages`: 角色主动消息展示
- `persona-voice`: 角色语音试听功能

### Modified Capabilities
- `persona-selection`: 增加试听声音按钮（现有 spec 已定义此需求，但前端未实现）
- `learning-progress`: 增加学习计划卡片模块（现有 spec 已定义此需求，但前端未实现）

## Impact

- **前端组件**：ChatView（添加长按/滑动交互）、LearnView 或新 PlanView（学习计划）、GuideSelectView（自定义角色分区 + 试听声音）、VoiceCallView（统一占位提示）
- **前端 API**：`toggleMessageFavorite`、`deleteMessage`、`listCustomPersonas`、`getPersonaVoiceUrl`、`getProactiveMessages`、`getPlan`、`setPlan`、`completePlan` — 这些已在 `api/` 层定义但未在组件中调用
- **后端**：无变更，所有接口已就绪
- **新增依赖**：无（所有 API client 代码已存在）