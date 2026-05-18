## Context

Mellow 后端（Python/FastAPI）已完成全部 API 开发（8 模块 22 端点），Docker Compose 一键启动。前端需从零构建 Flutter 应用，移动端优先，Web 为次要目标。UI 组件必须来自 Flutter Vignettes 源码（`C:\Users\Fedler\AppData\Local\Temp\opencode\vignettes_src\vignettes\`）或 pub.dev 高星包，绝对禁止手写 UI。

## Goals / Non-Goals

**Goals:**
- Flutter 前端完整对接后端全部 22 个 API 端点
- 移动端（Android/iOS）完整体验，Chrome Web 渲染正常（次要）
- 11 个 Vignettes 组件完整迁移并适配 Mellow 品牌色
- Light/Dark 双主题 + 墨迹过渡动画
- SSE 流式对话 + 消息粒子滑动交互
- Widget/Unit 测试覆盖核心模块

**Non-Goals:**
- 后端 API 修改（后端已定型，只对接）
- WebSocket 语音完整实现（后端 Phase 8 骨架，前端只做入口 UI）
- 离线模式（首版在线优先）
- 本地化多语言（首版中文，字符串集中常量管理）
- Push 通知、Analytics、Deep Link

## Decisions

### 1. 状态管理：Riverpod 手写（不用 codegen）

**选择**: `flutter_riverpod` 手写 `Notifier`/`AsyncNotifier`，不用 `@riverpod` 注解和 `build_runner`。

**理由**: 需求清单明确要求简化、减少生成文件。手写 Provider 对 10 个功能模块而言复杂度可控，且避免了 codegen 的学习曲线和构建步骤。若后续 Provider 数量膨胀（>30），可再评估引入 codegen。

**替代方案**: 
- `@riverpod` codegen → 被需求清单否决
- Provider 包 → 与 Riverpod 混用混乱
- BLoC → 过度工程

### 2. 路由：GoRouter + StatefulNavigationShell

**选择**: `go_router` 声明式路由，底部 3 Tab 用 `StatefulNavigationShell` 嵌套。

```
GoRouter
├── /splash          → SplashScreen
├── /auth/login      → LoginScreen
├── /auth/register   → RegisterScreen
├── StatefulNavigationShell (bubble_tab_bar)
│   ├── /chat        → ChatScreen
│   ├── /learn       → LearnScreen
│   └── /profile     → ProfileScreen
├── /personas        → PersonaSelectScreen
└── /personas/:id    → PersonaDetailScreen
```

**理由**: `StatefulNavigationShell` 保持各 Tab 页面状态（不用 IndexedStack hack），GoRouter 原生支持 deep link 和重定向。`bubble_tab_bar` 作为自定义 `BottomNavigationBar` 替换默认导航栏。

### 3. UI 组件分层：shadcn_ui（基础）+ Vignettes（特效）

**选择**: 基础 UI（按钮、输入框、卡片、Tabs）用 `shadcn_ui`，动效/背景/交互（3D 翻转、粒子、墨迹、星空）用 Vignettes 源码。

**理由**: shadcn_ui 提供 shadcn 设计系统的生产级 Flutter 实现，自带品牌色适配。Vignettes 提供独有动效（粒子物理、Canvas 图表、3D 视差、帧序列动画），二者互补。禁止手写任何视觉效果。

### 4. 数据模型：纯 Dart class + fromJson/toJson

**选择**: 手动编写 `class User { final String id; ... User.fromJson(Map<String,dynamic> json) ... }`。

**理由**: 需求清单否定了 Freezed。模型数量有限（~6 个），手写 JSON 序列化可控。禁止使用 `dynamic` 类型（除 `Map<String, dynamic>` JSON 解析）。

### 5. HTTP 客户端：Dio + JWT 拦截器

**选择**: `dio` + 自定义 `InterceptorsWrapper`：
- `onRequest`: 自动附加 `Authorization: Bearer <token>`
- `onError`: 检测 401 → 调用 `/auth/refresh` → 重试原请求 → 失败则清除 token 跳转登录

**SSE 流式**: 使用 `dio` 的 `ResponseType.stream` + 手动解析 `data:` 前缀的 SSE 帧。SSE 端点认证降级为 query param `?token=xxx`。

### 6. 主题：双主题令牌 + dark_ink_transition

**选择**: 
- `lib/theme/colors.dart` — 品牌色令牌（绿 `#5BC91A` + 橙 `#F09433` + 灰阶 light/dark）
- `ShadThemeData` light/dark 配置
- `SharedPreferences` 持久化主题选择
- `dark_ink_transition` 组件包裹全局切换（PNG 序列帧 34 帧）

### 7. Provider 目录结构

按功能模块组织，每个模块内按层拆分：
```
lib/
  main.dart
  theme/
    colors.dart, shadcn_theme.dart, typography.dart, spacing.dart
  router/
    app_router.dart
  models/
    user.dart, persona.dart, message.dart, word_entry.dart, learning_stats.dart
  services/
    api_client.dart          # Dio + JWT 拦截器
  providers/
    auth_provider.dart       # 登录/注册/自动登录状态
    persona_provider.dart    # 角色列表/选中/详情
    chat_provider.dart       # 消息列表/SSE 流式
    learn_provider.dart      # 学习统计/生词/错题
    profile_provider.dart    # 用户信息/设置
    theme_provider.dart      # 主题切换/持久化
  shared/
    vignettes/               # Vignettes 源码迁移目标
      _shared/               # 共享工具库
      bubble_tab_bar/
      parallax_travel_cards_list/
      particle_swipe/
      ... (11 个)
    widgets/                 # Mellow 自定义组件
      mellow_logo.dart
      message_bubble.dart
      shimmer_loading.dart
  features/
    splash/
    auth/
    personas/
    chat/
    learn/
    profile/
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| Vignettes 组件在 Mellow 上下文编译失败（包路径、资源引用） | 逐个迁移后立即 `flutter pub get && flutter analyze`，修复所有编译错误再继续 |
| SSE 流式解析在 Dio 下不稳定 | 备选方案：回退到 `http` 包的 `Client.send()` 获取 `StreamedResponse` |
| particle_swipe 与 ListView 滚动手势冲突 | 使用 `Dismissible` 的 `confirmDismiss` + `GestureDetector` 优先级控制 |
| shadcn_ui 品牌色与 Vignettes 硬编码颜色不一致 | 统一通过 `lib/theme/colors.dart` 令牌引用，Vignettes 源码中替换颜色常量 |
| 语音录音在 Web 端不支持（需 HTTPS + getUserMedia） | Web 为次要目标，移动端优先；录音入口检测平台能力后降级 |
| 无设计稿的 Logo 需自行生成 | 用 CustomPaint 绘制简洁小猫轮廓，保持灵动感 |

## Open Questions

- Mellow 小猫 Logo 最终设计：Simple shape CustomPaint 或 Emoji 占位？
- 生词本是否需要离线缓存（Hive）？
- CEFR 图表时间范围切换是否需要动画过渡？
