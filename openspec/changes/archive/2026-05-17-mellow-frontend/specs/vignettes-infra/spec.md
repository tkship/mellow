## ADDED Requirements

### Requirement: _shared 工具库迁移
系统 SHALL 从 Vignettes 源码完整复制 `_shared/lib/` 工具库。

#### Scenario: 复制工具库
- **WHEN** 项目初始化
- **THEN** 从 `C:\Users\Fedler\AppData\Local\Temp\opencode\vignettes_src\vignettes\_shared\lib\` 复制全部文件到 `mobile/lib/shared/vignettes/_shared/`

#### Scenario: 消除 Env.getPackage
- **WHEN** 迁移后编译
- **THEN** 所有 `App.pkg` 引用改为 Mellow 自身的包名引用

### Requirement: bubble_tab_bar 迁移
系统 SHALL 迁移底部导航栏组件。

#### Scenario: 集成到主页
- **WHEN** 应用主页渲染
- **THEN** bubble_tab_bar 渲染 Chat / Learn / Profile 三个 Tab，图标支持 3D 翻转动画

### Requirement: parallax_travel_cards_list 迁移
系统 SHALL 迁移 3D 视差卡片列表组件。

#### Scenario: 角色选择卡片
- **WHEN** 角色选择页渲染
- **THEN** 角色卡片支持 Rotation3d 倾斜 + elasticOut 回弹

### Requirement: particle_swipe 迁移
系统 SHALL 迁移粒子滑动交互组件。

#### Scenario: 消息滑动
- **WHEN** 用户在聊天消息上滑动
- **THEN** 触发粒子特效（星星/爆炸），执行收藏或删除操作

### Requirement: spending_tracker 迁移
系统 SHALL 迁移 Canvas 交互图表组件。

#### Scenario: CEFR 图表
- **WHEN** 学习进度页渲染
- **THEN** Canvas 折线图支持拖动查看数据点和缩放

### Requirement: drink_rewards_list 迁移
系统 SHALL 迁移可展开卡片组件。

#### Scenario: 学习计划卡片
- **WHEN** 学习进度页渲染
- **THEN** 任务卡片支持弹性展开 + 液体波浪填充动画

### Requirement: dark_ink_transition 迁移
系统 SHALL 迁移墨迹主题切换组件。

#### Scenario: 主题切换
- **WHEN** 用户切换主题
- **THEN** 34 帧墨迹 PNG 序列播放扩散动画

### Requirement: constellations_list 迁移
系统 SHALL 迁移星空背景组件。

#### Scenario: 背景渲染
- **WHEN** 角色选择页或学习页渲染
- **THEN** Canvas 星空粒子 + 星座连线背景持续动画

### Requirement: sparkle_party 迁移
系统 SHALL 迁移粒子庆祝特效组件。

#### Scenario: 打卡庆祝
- **WHEN** 用户完成今日学习任务
- **THEN** 全屏 Fireworks 粒子烟花效果

### Requirement: plant_forms 迁移
系统 SHALL 迁移表单堆叠组件。

#### Scenario: 登录/注册表单
- **WHEN** 登录或注册页渲染
- **THEN** 品牌风格输入框 + 堆叠页面路由 + 客户端验证

### Requirement: product_detail_zoom 迁移（PulsingButton）
系统 SHALL 迁移脉动按钮组件。

#### Scenario: 录音按钮
- **WHEN** 聊天输入栏渲染
- **THEN** 录音按钮支持 AnimatedScale 脉动 + 长按红色脉冲圈
