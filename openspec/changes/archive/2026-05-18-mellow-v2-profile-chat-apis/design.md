## Context

Mellow 2.0 前后端联调盘点发现多个 API 缺口阻塞发布：

- **后端**：`PUT /profile` 端点缺失（前端调用返回 404），`chat.py` 无历史消息查询/收藏/删除端点，消息仅存在于流式会话内存中，重启后全部丢失。
- **前端**：`api_client.dart` 已有 `updateProfile()` / `searchVocabulary()` 方法签名，但后端未实现对应端点或前端未接入（生词本搜索框 TODO）。`chat_provider.dart` 的 `toggleFavorite()` / `deleteMessage()` 仅操作本地 Riverpod state，刷新后状态复原。
- **存储架构**：当前所有画像/记忆/会话数据均为内存存储（`LearningProfileManager._profiles`、`SessionContextManager._ctx`），2.0 不迁移到 SQLite，但需为新增 API 提供内存实现以保持一致性。

## Goals / Non-Goals

**Goals:**
- 补充 4 个缺失的后端 API 端点（`PUT /profile`、`GET /chat/history`、`PUT /chat/messages/{id}/favorite`、`DELETE /chat/messages/{id}`）
- 完成 3 处前端 TODO 集成（生词本搜索、聊天历史分页、消息收藏/删除持久化）
- 保持现有端点行为不变，无 BREAKING CHANGE
- 所有新 API 遵循现有错误处理规范（MellowError → JSONResponse + SnackBar）

**Non-Goals:**
- 不迁移内存存储到 SQLite（3.0 技术债务）
- 不实现语音功能（Phase 8，3.0 计划）
- 不修改现有的 SSE 流式对话协议
- 不修改用户认证流程

## Decisions

### 1. 消息存储：在 `SessionContextManager` 中增加消息历史列表
**决策**：扩展 `SessionContextManager` 维护 `List[Message]`，为 `GET /chat/history` 提供数据源，而非新建独立存储。
**理由**：最小改动，复用现有会话上下文基础设施。会话粒度的消息列表与当前 Agent 上下文架构一致。
**替代方案**：新建 `MessageRepository` —— 需要更多文件和依赖注入改动，过度设计。

### 2. 消息 ID 生成：使用 `ULID`（基于时间排序的 UUID）
**决策**：后端生成消息 ID 使用 `python-ulid` 库，确保时间有序、可排序、无碰撞。
**理由**：`GET /chat/history` 需要按时间倒序分页，ULID 的字典序即时间序，避免额外索引。
**替代方案**：自增整数 —— 需要全局计数器，分布式场景下不友好；UUID v4 —— 无序，需要额外 `created_at` 字段排序。

### 3. 分页协议：Cursor-based（基于 ULID 的 last_id + limit）
**决策**：历史消息分页使用 `last_id` + `limit` 而非 offset/limit。
**理由**：消息列表追加频繁，cursor 分页避免跳页问题，且 ULID 天然支持字典序游标。
**替代方案**：Offset 分页 —— 在并发追加场景下可能出现数据重复或跳过。

### 4. Profile 更新：全量更新（PUT 语义），非 PATCH
**决策**：`PUT /profile` 接收完整 profile 对象，后端做字段级合并。
**理由**：前端当前调用方式即全量发送，与现有 `api_client.updateProfile(data)` 签名一致，无需修改前端调用代码。
**替代方案**：PATCH —— 需要前端修改调用方式，引入不必要的复杂度。

### 5. 前端消息状态：先更新本地 state 再调用 API（乐观更新）
**决策**：收藏/删除操作先更新 Riverpod state，再异步调用 API，失败时回滚。
**理由**：提供即时反馈，避免滑动交互卡顿。与现有 particle_swipe 动画节奏一致。
**替代方案**：先 API 后 UI —— 网络延迟会导致滑动动画完成后 UI 无变化，体验差。

## Risks / Trade-offs

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 消息内存存储，重启后历史丢失 | 高（用户数据丢失） | 在 API 文档和响应中明确标注"内存存储，重启数据丢失"；3.0 迁移 SQLite |
| 会话上下文内存泄漏 | 中（长期运行内存增长） | 限制 `_session_contexts` 字典大小（最多保留最近 50 个活跃会话），LRU 淘汰 |
| 乐观更新后 API 失败导致状态不一致 | 低（可回滚） | ChatNotifier 中捕获异常，回滚 state，显示 SnackBar 提示 |
| 多设备登录同一账号消息不同步 | 低（2.0 单设备场景为主） | 记录为已知限制，3.0 持久化后自然解决 |

## Migration Plan

无需数据库迁移或部署变更。本次为纯代码变更：
1. 后端：新增路由 handler 和内存存储逻辑
2. 前端：替换 TODO 为实际 API 调用
3. 测试：验证新增端点返回正确格式，前端集成后功能正常
4. 回滚：直接 revert 代码提交，无数据迁移风险

## Open Questions

- 聊天历史分页的 `session_id` 是否需要持久化到后端？当前设计使用 `user_id + persona_id` 组合作为隐式会话标识，前端不需要传递 session_id。
- 收藏消息是否需要按会话隔离？当前设计为全局消息收藏（不区分会话），与前端 UI 行为一致。
