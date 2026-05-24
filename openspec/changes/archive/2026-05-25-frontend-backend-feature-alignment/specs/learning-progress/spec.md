## MODIFIED Requirements

### Requirement: 学习计划卡片
系统 SHALL 展示学习计划任务的可展开卡片。

#### Scenario: 计划卡片展示
- **WHEN** 获取到 `current_plan` 数据（通过 `GET /api/v1/profile/plan`）
- **THEN** 系统以 drink_rewards_list 风格卡片展示每日任务，显示主题（theme）、每日 topic、词汇列表（vocabulary）、语法点（grammar_point）

#### Scenario: 完成今日任务
- **WHEN** 用户点击某日任务的"完成"按钮
- **THEN** 系统调用 `POST /api/v1/profile/plan/complete`，成功后该任务标记为已完成（视觉上加删除线 + 灰色），显示 Toast"任务已完成"

#### Scenario: 无学习计划
- **WHEN** `GET /profile/plan` 返回 `plan: null`
- **THEN** 系统显示"创建学习计划"按钮，点击后弹出简单表单，调用 `PUT /api/v1/profile/plan` 创建计划

#### Scenario: 计划加载失败
- **WHEN** `GET /profile/plan` API 失败
- **THEN** 系统不展示计划区域，不影响其他学习数据的显示