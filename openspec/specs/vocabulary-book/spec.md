# vocabulary-book Specification

## Purpose
TBD - created by archiving change mellow-frontend. Update Purpose after archive.
## Requirements
### Requirement: 生词本列表
系统 SHALL 展示用户的生词本，按首字母分组。

#### Scenario: 加载生词本
- **WHEN** 用户进入学习 Tab 生词本页
- **THEN** 系统调用 `GET /api/v1/vocabulary/book?sort=recent`，按首字母分组渲染列表

#### Scenario: 排序切换
- **WHEN** 用户切换排序方式（最近添加 / 字母序）
- **THEN** 系统重新请求对应排序的列表

#### Scenario: 空状态
- **WHEN** 生词本为空
- **THEN** 系统显示 MellowLogo + "在对话中长按单词即可加入生词本"提示

#### Scenario: 加载中
- **WHEN** 列表加载中
- **THEN** 系统显示 Shimmer 列表骨架

### Requirement: 生词搜索
系统 SHALL 支持生词本内搜索。

#### Scenario: 搜索过滤
- **WHEN** 用户在搜索框输入文字
- **THEN** 系统调用 `GET /api/v1/vocabulary/book/search?q=` 过滤匹配的单词

### Requirement: 生词删除
系统 SHALL 支持滑动删除生词。

#### Scenario: 左滑删除
- **WHEN** 用户向左滑动单词条目超过阈值
- **THEN** 系统显示红色粒子，调用 `DELETE /api/v1/vocabulary/book/{word}`，从列表移除

### Requirement: 单词详情
系统 SHALL 展示单词的详细信息。

#### Scenario: 查看详情
- **WHEN** 用户点击单词条目
- **THEN** 系统弹出 BottomSheet，展示单词、发音、词性、释义、例句、同义词

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

