## ADDED Requirements

### Requirement: 学习计划展示
系统 SHALL 在 LearnView 底部展示用户当前学习计划。

#### Scenario: 加载学习计划
- **WHEN** 用户切换到学习 Tab
- **THEN** 系统调用 `GET /api/v1/profile/plan`，若返回 `plan` 非空，在 CEFR 进度图和弱点分布下方渲染"本周学习计划"卡片区域

#### Scenario: 计划卡片内容
- **WHEN** 学习计划数据加载完成
- **THEN** 系统展示计划主题（theme）、周数（week），以及每日任务列表（day: 1-7, topic, vocabulary[], grammar_point, practice）

#### Scenario: 完成每日任务
- **WHEN** 用户点击某日任务的"完成"按钮
- **THEN** 系统调用 `POST /api/v1/profile/plan/complete`，成功后该任务标记为已完成（视觉上加删除线 + 灰色），显示 Toast "任务已完成"

#### Scenario: 无学习计划
- **WHEN** `GET /profile/plan` 返回 `plan: null`
- **THEN** 系统显示"暂无学习计划"空状态提示，不展示计划卡片

### Requirement: 创建学习计划
系统 SHALL 允许用户设置学习计划。

#### Scenario: 设置学习计划入口
- **WHEN** 学习计划为空（`plan: null`）
- **THEN** 系统显示"创建学习计划"按钮

#### Scenario: 设置学习计划
- **WHEN** 用户点击"创建学习计划"
- **THEN** 系统弹出简单表单（周数、主题），用户填写后调用 `PUT /api/v1/profile/plan`，成功后渲染计划卡片