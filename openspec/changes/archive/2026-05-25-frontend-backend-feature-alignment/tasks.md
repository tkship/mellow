## 1. 消息交互 — 收藏/删除 UI

- [x] 1.1 在 ChatView 中添加消息长按检测（触摸 500ms / 右键），弹出 ContextMenu 组件
- [x] 1.2 实现 ContextMenu 选项：收藏/取消收藏、复制文字、删除，点击后调用对应 API（toggleMessageFavorite / deleteMessage）
- [x] 1.3 实现乐观更新：收藏立即切换星星图标、删除立即移除消息、API 失败时回滚并 Toast 提示
- [x] 1.4 删除操作增加确认对话框
- [x] 1.5 App.tsx 中导入 toggleMessageFavorite 和 deleteMessage，通过 props 传递给 ChatView

## 2. 学习计划模块

- [x] 2.1 App.tsx 中导入 getPlan / setPlan / completePlan，新增 plan state，在 loadLearnData 中并发调用 getPlan()
- [x] 2.2 LearnView 底部添加"本周学习计划"卡片区域：plan 非空时展示 theme + days 列表，plan 为空时显示"创建学习计划"按钮
- [x] 2.3 实现每日任务"完成"按钮，调用 completePlan() 并更新 UI（删除线 + 灰色）
- [x] 2.4 实现简单创建计划表单（周数 + 主题），调用 setPlan() 后刷新计划数据

## 3. 自定义角色接入

- [x] 3.1 App.tsx 中导入 listCustomPersonas，在加载预设角色后并发调用获取自定义角色
- [x] 3.2 合并预设角色和自定义角色到 personas state，自定义角色需要添加 `isCustom` 标记以区分
- [x] 3.3 GuideSelectView 添加"我的角色"分区标题，仅在自定义角色列表非空时展示
- [x] 3.4 自定义角色卡片使用首字母头像（无 PERSONA_AVATAR_MAP 映射），交互与预设角色一致

## 4. 主动消息展示

- [x] 4.1 App.tsx 中导入 getProactiveMessages，进入聊天时调用并存储 proactiveMessages state
- [x] 4.2 ChatView 顶部添加可关闭横幅组件，展示最新一条主动消息
- [x] 4.3 横幅"查看"按钮：将消息内容作为 AI 消息插入聊天列表并关闭横幅
- [x] 4.4 横幅"关闭"按钮：关闭横幅，本次会话不再显示

## 5. 角色语音试听

- [x] 5.1 App.tsx 或 GuideSelectView 中添加 audio 播放逻辑：当前播放的 personaId state + playVoice(personaId) 函数
- [x] 5.2 角色卡片底部添加"试听声音"按钮（喇叭图标 + 文字），调用 getPersonaVoiceUrl 构建 URL
- [x] 5.3 使用 HTML5 `<audio>` 播放，按钮状态切换（默认 → 播放中动画 → 完成），404 时 Toast 提示"暂无配音"
- [x] 5.4 切换角色时停止当前播放

## 6. VoiceCallView 优化

- [x] 6.1 将麦克风按钮的 alert('语音功能开发中') 替换为 Toast/SnackBar 提示组件
- [x] 6.2 确认"语音功能开发中"文案和"下个版本上线"占位提示清晰可见