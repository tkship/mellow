## ADDED Requirements

### Requirement: 自定义角色列表加载
系统 SHALL 在角色选择页加载并展示自定义角色。

#### Scenario: 加载自定义角色
- **WHEN** 用户进入角色选择页
- **THEN** 系统同时调用 `GET /api/v1/personas`（预设角色）和 `GET /api/v1/personas/custom`（自定义角色），将两部分角色合并展示

#### Scenario: 自定义角色分区展示
- **WHEN** 自定义角色列表非空
- **THEN** 系统在预设角色下方添加"我的角色"分区标题，展示自定义角色卡片（使用首字母头像，无专属图片映射）

#### Scenario: 自定义角色为空
- **WHEN** 自定义角色列表为空
- **THEN** 系统不显示"我的角色"分区

#### Scenario: 自定义角色交互
- **WHEN** 用户点击自定义角色卡片
- **THEN** 交互行为与预设角色一致（选中 → 确认 → 进入聊天）