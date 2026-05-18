# persona-selection Specification

## Purpose
TBD - created by archiving change mellow-frontend. Update Purpose after archive.
## Requirements
### Requirement: 角色列表展示
系统 SHALL 从后端获取所有预设角色并以 3D 视差卡片列表展示。

#### Scenario: 加载角色列表
- **WHEN** 用户进入角色选择页
- **THEN** 系统调用 `GET /api/v1/personas`，以 parallax_travel_cards_list 横向滑动卡片渲染角色

#### Scenario: 加载中状态
- **WHEN** 角色列表正在加载
- **THEN** 系统显示 Shimmer 骨架卡片占位，星空背景持续渲染

#### Scenario: 加载失败
- **WHEN** API 请求失败
- **THEN** 系统显示错误提示和重试按钮

### Requirement: 角色卡片交互
系统 SHALL 支持角色卡片的 3D 视差旋转和选中状态。

#### Scenario: 卡片倾斜旋转
- **WHEN** 用户手指在卡片上移动
- **THEN** 卡片跟随手指位置产生 3D Rotation3d 倾斜效果，松手后 elasticOut 回弹

#### Scenario: 选中角色
- **WHEN** 用户点击卡片
- **THEN** 卡片显示选中标记（check_circle），放大进入详情页

### Requirement: 角色详情展示
系统 SHALL 展示角色的完整信息。

#### Scenario: 查看角色详情
- **WHEN** 用户点击角色卡片
- **THEN** 系统跳转详情页，展示大号 emoji、名字、角色描述、语言风格、教学风格

#### Scenario: 试听声音
- **WHEN** 用户点击"试听声音"按钮
- **THEN** 系统调用 `GET /api/v1/personas/{id}/voice`，播放 MP3 配音

#### Scenario: 配音不可用
- **WHEN** 后端返回 404（该角色无配音）
- **THEN** 系统显示"暂无配音"提示

### Requirement: 选择角色
系统 SHALL 允许用户选择对话角色。

#### Scenario: 开始对话
- **WHEN** 用户在详情页点击"开始对话"按钮
- **THEN** 系统保存选中角色到本地状态，跳转聊天页

#### Scenario: 跳过选择
- **WHEN** 用户在角色列表页点击"跳过"按钮
- **THEN** 系统使用默认角色，跳转聊天页

### Requirement: 角色切换
系统 SHALL 允许用户在聊天中切换角色。

#### Scenario: 聊天页切换
- **WHEN** 用户在聊天页顶部点击角色名称
- **THEN** 系统弹出 PopupMenu 列出所有角色，点击后切换当前角色

#### Scenario: 设置页切换
- **WHEN** 用户在设置页点击"切换角色"
- **THEN** 系统跳转角色选择页

