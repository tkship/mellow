## ADDED Requirements

### Requirement: 消息收藏删除 API 集成
系统 SHALL 将消息滑动交互的收藏/删除操作从纯本地状态改为调用后端 API 持久化。

#### Scenario: 右滑收藏调用 API
- **WHEN** 用户右滑消息气泡触发收藏
- **THEN** 系统显示 particle_swipe 蓝色粒子特效，乐观更新本地状态为已收藏，异步调用 `PUT /chat/messages/{id}/favorite`

#### Scenario: 左滑删除调用 API
- **WHEN** 用户左滑消息气泡触发删除
- **THEN** 系统显示 particle_swipe 红色粒子特效，乐观更新本地状态移除消息，异步调用 `DELETE /chat/messages/{id}`

#### Scenario: API 失败回滚
- **WHEN** 收藏或删除 API 调用失败（网络错误或 404）
- **THEN** 系统回滚本地状态（收藏恢复原状 / 删除恢复消息），显示 SnackBar 提示操作失败
