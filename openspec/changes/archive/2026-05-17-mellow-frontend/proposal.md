## Why

Mellow 后端（Python/FastAPI）API 全部跑通，Docker Compose 可运行，但缺少面向用户的前端。需要构建 Flutter 前端应用对接已有后端，将 AI 英语对话学习体验交付给移动端用户。

## What Changes

- **新建 Flutter 项目** `mobile/`，基础设施：主题（Light/Dark 双主题）、GoRouter 路由、Dio API 客户端、纯 Dart 数据模型
- **迁移 11 个 Flutter Vignettes 组件**（底部导航、3D 视差卡片、粒子滑动、Canvas 图表、可展开卡片、墨迹主题切换、星空背景、粒子庆祝、表单堆叠、脉动按钮）
- **认证流程**：启动页自动登录检测、登录/注册（品牌表单）、JWT 持久化与自动刷新
- **角色选择**：预设角色 3D 视差卡片浏览、角色详情、配音试听、切换角色
- **聊天核心**：SSE 流式对话、消息气泡、粒子滑动交互（收藏/删除）、语音录制入口
- **学习 Tab**：CEFR 折线图（Canvas 交互）、统计卡片、生词本 CRUD、错题本
- **个人设置**：用户信息、主题切换（墨迹动画）、学习目标、退出登录
- **测试 + UI 审查**：Widget/Unit 测试，强制使用外部组件/Vignettes 代码，禁止手写 UI

## Capabilities

### New Capabilities

- `auth-flow`: 注册、登录、自动登录、JWT 管理
- `persona-selection`: 角色浏览、详情、试听、切换
- `chat-core`: SSE 流式对话、消息气泡、快捷开场白
- `chat-interactions`: 粒子滑动、收藏/删除、语音入口
- `learning-progress`: CEFR 图表、统计、学习计划
- `vocabulary-book`: 生词本列表、搜索、添加/删除
- `mistakes-review`: 错题本只读展示
- `profile-settings`: 用户信息、设置、主题切换
- `theme-system`: 双主题令牌、墨迹过渡动画
- `vignettes-infra`: _shared 工具库 + 11 个组件迁移

### Modified Capabilities

<!-- 全新项目，无已有能力 -->

## Impact

- **新建**: `mobile/` Flutter 项目
- **依赖**: `flutter_riverpod`, `go_router`, `shadcn_ui`, `dio`, `google_fonts`, `flutter_animate`, `record`, `just_audio`, `shared_preferences`
- **后端对接**: 8 模块 22 端点
- **约束**: 不用 codegen、不用 Freezed、不用 Provider 包、禁止手写 UI
