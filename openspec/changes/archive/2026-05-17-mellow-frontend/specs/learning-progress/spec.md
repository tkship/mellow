## ADDED Requirements

### Requirement: 学习统计展示
系统 SHALL 展示用户的学习统计数据。

#### Scenario: 加载统计数据
- **WHEN** 用户进入学习 Tab 进度页
- **THEN** 系统调用 `GET /api/v1/profile/stats?range=month`，展示 CEFR 等级、词汇量、学习天数三个统计卡片

#### Scenario: 时间范围切换
- **WHEN** 用户点击 周/月/半年 SegmentedControl
- **THEN** 系统重新请求对应 range 的统计数据并更新图表

#### Scenario: 加载中状态
- **WHEN** 数据加载中
- **THEN** 系统显示 Shimmer 卡片和 Shimmer 图表占位

### Requirement: CEFR 折线图
系统 SHALL 以 Canvas 交互折线图展示 CEFR 进步轨迹。

#### Scenario: 图表渲染
- **WHEN** 获取到 `cefr_progress` 数据
- **THEN** 系统渲染 spending_tracker 风格折线图（Canvas 绘制），Y 轴 A0~C2，X 轴日期

#### Scenario: 图表交互
- **WHEN** 用户在图表上拖动
- **THEN** 系统显示当前触摸点的数据详情（日期 + CEFR 等级 + 分数）

#### Scenario: 图表缩放
- **WHEN** 用户双指捏合图表
- **THEN** 系统缩放图表时间轴

### Requirement: 弱点分布
系统 SHALL 展示学习弱项分布。

#### Scenario: 弱点进度条
- **WHEN** 获取到 `weak_areas` 数据
- **THEN** 系统以横向进度条展示听力/语法/词汇/发音各项，品牌绿色填充

### Requirement: 学习计划卡片
系统 SHALL 展示学习计划任务的可展开卡片。

#### Scenario: 计划卡片展示
- **WHEN** 获取到 `current_plan` 数据
- **THEN** 系统以 drink_rewards_list 风格卡片展示每日任务，液体填充进度

#### Scenario: 完成今日任务
- **WHEN** 用户点击"完成今日任务"按钮
- **THEN** 系统触发 sparkle_party Fireworks 粒子庆祝全屏特效
