# chat-interactions Specification

## Purpose
TBD - created by archiving change mellow-frontend. Update Purpose after archive.
## Requirements
### Requirement: 消息粒子滑动
系统 SHALL 支持消息气泡的粒子滑动手势交互。

#### Scenario: 右滑收藏
- **WHEN** 用户向右滑动消息气泡超过阈值
- **THEN** 系统显示蓝色粒子 + 星星特效，调用 API 收藏消息，气泡右下角显示金色星星

#### Scenario: 左滑删除
- **WHEN** 用户向左滑动消息气泡超过阈值
- **THEN** 系统显示红色粒子 + 爆炸特效，调用 API 删除消息，消息从列表移除

#### Scenario: 滑动未达阈值
- **WHEN** 用户滑动距离不足阈值
- **THEN** 气泡回弹到原位，无操作

### Requirement: 长按操作菜单
系统 SHALL 支持消息的辅助操作。

#### Scenario: 长按弹出菜单
- **WHEN** 用户长按消息气泡
- **THEN** 系统弹出操作菜单：收藏/取消收藏、复制文字、删除

### Requirement: 语音录制入口
系统 SHALL 提供语音录制按钮及录音状态指示。

#### Scenario: 长按录音
- **WHEN** 用户长按录音按钮
- **THEN** 按钮显示红色脉冲圈（PulsingButton）动画 + 计时器

#### Scenario: 松开发送
- **WHEN** 用户松开录音按钮
- **THEN** 系统停止录音，显示"语音功能开发中"提示（后端 WebSocket 未完成）

#### Scenario: 平台不支持
- **WHEN** 当前平台不支持录音
- **THEN** 录音按钮隐藏或禁用

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

