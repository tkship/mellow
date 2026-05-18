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

