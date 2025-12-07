## MODIFIED Requirements

### Requirement: GUI视觉与交互
系统SHALL提供美观且实用的图形界面，MUST支持以下特性：

#### Scenario: 主题与配色
- **WHEN** 用户启动GUI
- **THEN** 界面MUST使用统一的现代主题配色
- **AND** 字体大小适中，控件间距合理

#### Scenario: 顺序组视觉关联
- **WHEN** 配置面板显示带有顺序组的S2C响应
- **THEN** 相同顺序组的项目MUST使用相同背景色
- **AND** 左侧SHALL显示颜色条标识组别

#### Scenario: 工具栏快捷操作
- **WHEN** 用户需要常用操作
- **THEN** SHALL可通过顶部工具栏按钮快速执行保存、刷新、验证
- **AND** 按钮MUST显示对应快捷键提示

#### Scenario: 悬停提示
- **WHEN** 鼠标悬停在协议列表项上
- **THEN** SHALL显示该协议的完整描述信息

#### Scenario: 状态栏信息
- **WHEN** 用户编辑配置
- **THEN** 状态栏MUST显示当前文件修改状态
- **AND** SHALL显示已配置的C2S数量和S2C响应总数

#### Scenario: 顺序组说明展示
- **WHEN** 选中的C2S配置包含顺序组
- **THEN** 配置面板底部SHALL显示各顺序组的说明文字
