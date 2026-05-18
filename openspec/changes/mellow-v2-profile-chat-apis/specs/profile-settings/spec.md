## ADDED Requirements

### Requirement: 学习目标设置后端持久化
系统 SHALL 将学习目标设置从纯前端状态改为调用后端 `PUT /profile` API 保存。

#### Scenario: 保存 CEFR 目标
- **WHEN** 用户在设置页选择 CEFR 等级并确认
- **THEN** 系统调用 `PUT /api/v1/profile` 发送 `{cefr_level: "B2"}`，成功显示确认提示，失败显示错误 SnackBar

#### Scenario: 加载已保存目标
- **WHEN** 用户进入设置页
- **THEN** 系统从 `GET /api/v1/profile` 响应读取当前 `cefr_level`，在 SimpleDialog 中高亮显示当前选择
