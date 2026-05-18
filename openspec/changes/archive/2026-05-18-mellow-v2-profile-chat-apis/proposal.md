## Why

需求清单 2.0 盘点发现，Mellow 前后端联调存在多个 P0/P1 级别的 API 缺口：后端 `PUT /profile` 缺失导致前端 404，聊天历史分页、消息收藏/删除等核心功能只有本地状态而无持久化，生词本搜索前端 TODO 未接入。这些缺口直接影响 2.0 版本的可用性和数据一致性，必须在发布前补齐。

## What Changes

- **后端**：补充 4 个缺失的 API 端点
  - `PUT /api/v1/profile` — 更新用户 CEFR 目标、学习目标等画像信息
  - `GET /api/v1/chat/history` — 分页查询对话历史（按 session 分页）
  - `PUT /api/v1/chat/messages/{id}/favorite` — 收藏/取消收藏消息
  - `DELETE /api/v1/chat/messages/{id}` — 删除单条消息
- **前端**：完成 3 处 TODO 集成
  - 生词本搜索框接入 `api_client.searchVocabulary()`（learn_screen.dart:505）
  - 聊天页接入历史消息分页加载（上滑加载更多）
  - 消息收藏/删除从本地状态改为调用后端 API（chat_provider.dart:205-213）
- **数据层**：为上述 API 提供内存存储实现（与 2.0 架构一致， SQLite 迁移列为 3.0 技术债务）
- **交互规范**：所有新 API 调用均遵循现有 error handling + SnackBar 提示规范

## Capabilities

### New Capabilities
- `chat-history-pagination`: 后端分页查询对话历史 API（GET /api/v1/chat/history）及前端分页加载集成
- `message-persistent-actions`: 后端消息收藏（PUT /favorite）与删除（DELETE /{id}）API 及前端滑动交互持久化
- `profile-update-endpoint`: 后端用户画像更新 API（PUT /api/v1/profile）及前端学习目标设置集成

### Modified Capabilities
- `vocabulary-book`: 现有 spec 已定义搜索过滤 requirement，本次补充前端 `onChanged` 接入实现（spec-level behavior 无变化，仅完成实现缺口）
- `chat-core`: 现有 spec 已定义上滑加载更多 requirement，本次补充分页加载实现（spec-level behavior 无变化，仅完成实现缺口）
- `chat-interactions`: 现有 spec 已定义右滑收藏/左滑删除 requirement，本次补充 API 调用实现（spec-level behavior 无变化，仅完成实现缺口）
- `profile-settings`: 现有 spec 已定义学习目标设置 requirement，本次补充 API 调用实现（spec-level behavior 无变化，仅完成实现缺口）

## Impact

- **后端**：`main.py` 路由注册、`routers/profile.py`、`routers/chat.py`、数据模型/存储层（内存实现）
- **前端**：`learn_screen.dart`（搜索集成）、`chat_screen.dart`（分页加载）、`chat_provider.dart`（收藏/删除 API 化）
- **API 契约**：新增 4 个端点，现有端点行为不变，无 BREAKING CHANGE
- **依赖**：无新增外部依赖，复用现有 FastAPI + Riverpod + Dio 基础设施
