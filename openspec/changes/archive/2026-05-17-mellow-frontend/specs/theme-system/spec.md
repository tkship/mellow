## ADDED Requirements

### Requirement: 双主题令牌
系统 SHALL 定义 Light 和 Dark 两套颜色令牌。

#### Scenario: 品牌色令牌
- **WHEN** 系统初始化主题
- **THEN** 从 `lib/theme/colors.dart` 加载品牌色（绿 #5BC91A + 橙 #F09433）+ 灰阶 light/dark 值

#### Scenario: ShadTheme 双配置
- **WHEN** 系统切换主题
- **THEN** ShadApp 的 `theme` 和 `darkTheme` 分别应用 `ShadThemeData` light/dark 配置

### Requirement: 墨迹过渡动画
系统 SHALL 使用 dark_ink_transition 组件实现主题切换动画。

#### Scenario: 墨迹扩散
- **WHEN** 用户触发主题切换
- **THEN** 系统播放 ink_mask.png（34 帧序列）墨迹扩散动画（1500ms），从点击位置扩散至全屏

#### Scenario: 动画完成
- **WHEN** 墨迹动画播放完毕
- **THEN** 系统完成主题值切换，清理动画资源

### Requirement: 主题持久化
系统 SHALL 持久化用户主题选择。

#### Scenario: 记住主题
- **WHEN** 用户切换主题后关闭应用再打开
- **THEN** 系统自动应用上次选择的主题模式

### Requirement: Vignettes 组件暗色适配
系统 SHALL 确保所有 Vignettes 组件在暗色主题下正常渲染。

#### Scenario: 星空暗色适配
- **WHEN** 暗色主题激活且角色选择页可见
- **THEN** constellations_list 星空在暗色背景下更明显可见
