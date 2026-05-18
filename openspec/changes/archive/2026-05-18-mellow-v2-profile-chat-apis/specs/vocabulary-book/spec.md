## ADDED Requirements

### Requirement: 生词本搜索前端集成
系统 SHALL 将生词本搜索框的输入实时接入后端搜索 API。

#### Scenario: 输入搜索关键词
- **WHEN** 用户在生词本搜索框输入文字（去抖 300ms）
- **THEN** 系统调用 `GET /api/v1/vocabulary/book/search?q={keyword}`，用返回结果替换当前列表展示

#### Scenario: 清空搜索
- **WHEN** 用户清空搜索框文字
- **THEN** 系统重新调用 `GET /api/v1/vocabulary/book` 加载完整生词本列表

#### Scenario: 搜索无结果
- **WHEN** 用户输入的关键词无匹配结果
- **THEN** 系统显示空状态提示"未找到匹配的单词"
