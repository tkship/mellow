## MODIFIED Requirements

### Requirement: 角色详情展示
系统 SHALL 展示角色的完整信息。

#### Scenario: 查看角色详情
- **WHEN** 用户点击角色卡片
- **THEN** 系统跳转详情页，展示大号 emoji、名字、角色描述、语言风格、教学风格

#### Scenario: 试听声音
- **WHEN** 用户点击"试听声音"按钮
- **THEN** 系统调用 `getPersonaVoiceUrl(personaId)` 构建 URL，播放 MP3 配音

#### Scenario: 配音不可用
- **WHEN** 后端返回 404（该角色无配音）
- **THEN** 系统显示"暂无配音"提示

### Requirement: 角色列表展示
系统 SHALL 从后端获取所有预设角色和自定义角色并以 3D 视差卡片列表展示。

#### Scenario: 加载角色列表
- **WHEN** 用户进入角色选择页
- **THEN** 系统并行调用 `GET /api/v1/personas` 和 `GET /api/v1/personas/custom`，以 parallax_travel_cards_list 横向滑动卡片渲染预设角色，下方分区渲染自定义角色

#### Scenario: 自定义角色为空
- **WHEN** 自定义角色接口返回空列表
- **THEN** 系统仅展示预设角色分区，不显示"我的角色"标题

#### Scenario: 加载失败
- **WHEN** 自定义角色接口返回 401 或其他错误
- **THEN** 系统忽略错误，仅展示预设角色，不打断整体页面渲染