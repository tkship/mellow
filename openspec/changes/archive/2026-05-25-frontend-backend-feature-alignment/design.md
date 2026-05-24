## Context

Mellow 是一个 AI 语言学习伴侣应用，后端 FastAPI 已完成全部 API 开发（33 个端点 + 1 个 WebSocket），前端 React/Vite 已适配大部分接口但存在 6 处功能缺口。所有缺失的 API client 函数（`toggleMessageFavorite`、`deleteMessage`、`listCustomPersonas`、`getPersonaVoiceUrl`、`getProactiveMessages`、`getPlan`、`setPlan`、`completePlan`）均已在 `frontend/src/api/` 层定义完毕，本次只需补 UI 交互入口和组件逻辑。

当前前端架构：
- `App.tsx` 为单文件路由/状态管理中心
- 组件在 `components/` 目录，各页面组件通过 props 接收数据和回调
- API 层在 `api/` 目录，统一 JWT 认证 + 自动刷新

## Goals / Non-Goals

**Goals:**
- 为聊天消息添加收藏/删除的 UI 交互入口（长按菜单），调用已有 API 持久化
- 实现学习计划页面（查看/设置/完成），对接 `GET/PUT /profile/plan` 和 `POST /profile/plan/complete`
- 接入自定义角色列表，在角色选择页分区展示
- 接入角色主动消息，在聊天页展示
- 实现角色语音试听按钮
- 优化 VoiceCallView 占位体验（统一提示弹窗替代 `alert()`）

**Non-Goals:**
- 不实现语音通话 WebSocket 实际功能（后端 WS 端点可用但 TTS/STT 集成未完成）
- 不修改后端代码（所有 API 已就绪）
- 不做深色模式/语言/通知的服务端持久化（需后端新增接口，超出本次范围）
- 不做自定义角色创建 UI（后端仅有列表接口，无创建接口）

## Decisions

### 1. 消息交互：长按菜单而非滑动

**决策**：采用长按菜单（ContextMenu）而非滑动手势来触发收藏/删除。

**理由**：
- 滑动手势在移动端存在与滚动手势冲突的问题，实现复杂度高
- 长按菜单是更通用的交互模式，桌面端和移动端均可使用
- 已有 spec `message-persistent-actions` 定义了长按菜单方案，保持一致

**替代方案**：Swipeable 滑动组件（已否决，手势冲突风险高）

### 2. 学习计划：嵌入 LearnView 而非独立页面

**决策**：在 LearnView 的底部添加可折叠的"本周学习计划"卡片区域，而非创建独立的 PlanView。

**理由**：
- 学习计划是学习数据的自然延伸，与 CEFR 进度、弱点分布在同一页面
- 减少导航层级，用户不需要额外跳转
- 与 spec `learning-progress` 中的"学习计划卡片"需求一致

### 3. 主动消息：ChatView 顶部 Banner

**决策**：角色主动消息以可关闭的横幅（Banner）形式展示在 ChatView 顶部。

**理由**：
- 主动消息是角色发起的对话开场，不应打断当前聊天流
- Banner 形式是常见的消息提示模式
- 用户可选择查看或关闭

### 4. 语音试听：卡片内按钮 + Audio 元素

**决策**：在 GuideSelectView 的角色卡片和角色详情区域内添加"试听"按钮，使用 HTML5 `<audio>` 元素播放。

**理由**：
- `getPersonaVoiceUrl` 已构建好 URL（`/api/v1/personas/{id}/voice`），直接用作 audio src
- 无需引入额外音频库
- 404 时显示"暂无配音"提示

## Risks / Trade-offs

- **聊天历史仅为内存存储** → 后端 `chat/messages` 端点依赖 `SessionContext`，服务重启后收藏/删除会丢失。这是后端限制，前端不做额外缓存。
- **自定义角色仅展示** → 无创建/编辑接口，用户只能看到后端预设或未来通过其他方式创建的角色。
- **VoiceCallView 仍为占位** → 保持占位但优化 UX，避免用户困惑。语音 WebSocket 集成需单独迭代。
- **学习计划卡片内容** → 后端 `WeeklyPlan` 结构较复杂（7 天 × 多字段），初始版本只展示主题和每日 topic，不做完整 CRUD。