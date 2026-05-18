## ADDED Requirements

### Requirement: 后端提供用户画像更新
系统 SHALL 提供更新当前用户学习画像的 API。

#### Scenario: 更新 CEFR 目标等级
- **WHEN** 前端请求 `PUT /api/v1/profile`，body 包含 `{"cefr_level": "B1"}`
- **THEN** 系统更新用户画像中的 CEFR 等级，返回更新后的完整画像

#### Scenario: 更新多个画像字段
- **WHEN** 前端请求 `PUT /api/v1/profile`，body 包含 `cefr_level`、`vocabulary_size`、`learning_goal` 等字段
- **THEN** 系统合并更新提供的字段（未提供的字段保持不变），返回更新后的完整画像

#### Scenario: 未认证用户请求
- **WHEN** 未认证用户请求 `PUT /api/v1/profile`
- **THEN** 系统返回 401 Unauthorized

### Requirement: 前端学习目标设置 API 集成
系统 SHALL 将前端学习目标设置从本地状态改为调用后端 API 持久化。

#### Scenario: 选择 CEFR 目标等级
- **WHEN** 用户在个人页点击"学习目标"，选择 A1~C2 等级并确认
- **THEN** 系统调用 `PUT /api/v1/profile` 保存选择，成功显示 SnackBar"学习目标已更新"，失败显示错误提示

#### Scenario: 进入个人页加载目标
- **WHEN** 用户进入个人页
- **THEN** 系统从 `GET /api/v1/profile` 响应中读取 `cefr_level` 并显示当前目标
