## ADDED Requirements

### Requirement: 错题本展示
系统 SHALL 以只读列表展示用户常见错误。

#### Scenario: 加载错题
- **WHEN** 用户进入学习 Tab 错题本页
- **THEN** 系统调用 `GET /api/v1/profile/mistakes`，渲染错题卡片列表

#### Scenario: 错题卡片内容
- **WHEN** 渲染错题条目
- **THEN** 卡片展示错误类型、错误示例 → 正确形式、出现次数

#### Scenario: 空状态
- **WHEN** 暂无错题记录
- **THEN** 系统显示"继续对话，AI 会自动记录你的常见错误"提示

#### Scenario: 加载中
- **WHEN** 数据加载中
- **THEN** 系统显示 Shimmer 卡片骨架
