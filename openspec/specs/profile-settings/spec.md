# profile-settings Specification

## Purpose
TBD - created by archiving change mellow-frontend. Update Purpose after archive.
## Requirements
### Requirement: 用户信息展示
系统 SHALL 展示当前用户的基本信息。

#### Scenario: 加载用户信息
- **WHEN** 用户进入个人 Tab
- **THEN** 系统调用 `GET /api/v1/auth/me` 和 `GET /api/v1/profile/stats`，展示头像（MellowLogo）、用户名、学习等级、消息数/学习天数/打卡次数

#### Scenario: 当前角色卡
- **WHEN** 渲染个人页
- **THEN** 系统显示当前选中角色卡（emoji + 名字 + 角色 + 切换入口）

### Requirement: 学习目标设置
系统 SHALL 允许用户设置 CEFR 目标等级。

#### Scenario: 选择目标等级
- **WHEN** 用户点击"学习目标"设置项
- **THEN** 系统弹出 SimpleDialog（A1~C2 选项），用户选择后调用 `PUT /api/v1/profile` 保存

### Requirement: 主题切换
系统 SHALL 支持亮/暗主题切换。

#### Scenario: 切换主题
- **WHEN** 用户点击"深色模式"开关
- **THEN** 系统触发 dark_ink_transition 墨迹过渡动画，切换 ShadThemeData

#### Scenario: 主题持久化
- **WHEN** 用户切换主题
- **THEN** 系统保存选择到 SharedPreferences，下次启动自动应用

### Requirement: 退出登录
系统 SHALL 支持退出登录功能。

#### Scenario: 退出确认
- **WHEN** 用户点击"退出登录"（红色文字）并确认弹窗选择"确定"
- **THEN** 系统清除 Token，跳转登录页

### Requirement: 页脚信息
系统 SHALL 在个人页底部显示应用信息。

#### Scenario: 版本信息
- **WHEN** 渲染个人页底部
- **THEN** 系统显示"关于 Mellow · v0.1.0"（muted 文字居中）

### Requirement: 学习目标设置后端持久化
系统 SHALL 将学习目标设置从纯前端状态改为调用后端 `PUT /profile` API 保存。

#### Scenario: 保存 CEFR 目标
- **WHEN** 用户在设置页选择 CEFR 等级并确认
- **THEN** 系统调用 `PUT /api/v1/profile` 发送 `{cefr_level: "B2"}`，成功显示确认提示，失败显示错误 SnackBar

#### Scenario: 加载已保存目标
- **WHEN** 用户进入设置页
- **THEN** 系统从 `GET /api/v1/profile` 响应读取当前 `cefr_level`，在 SimpleDialog 中高亮显示当前选择

