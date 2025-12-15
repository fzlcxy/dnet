## ADDED Requirements

### Requirement: S2C模式切换
系统 SHALL 提供C2S模式和S2C模式的切换功能，使用Tab页签实现。

#### Scenario: 切换到S2C模式
- **WHEN** 用户点击S2C模式Tab
- **THEN** 显示S2C模式面板，隐藏C2S模式面板

#### Scenario: 切换回C2S模式
- **WHEN** 用户点击C2S模式Tab
- **THEN** 显示C2S模式面板，隐藏S2C模式面板

### Requirement: S2C协议选择
系统 SHALL 在S2C模式下提供S2C协议选择功能，包括dnet文件列表和S2C协议列表。

#### Scenario: 选择S2C dnet文件
- **WHEN** 用户在S2C模式下选择一个包含S2C的dnet文件
- **THEN** 右侧S2C协议列表显示该文件中的所有S2C协议

#### Scenario: 选择S2C协议
- **WHEN** 用户选择一个S2C协议
- **THEN** 中部显示触发该S2C的C2S列表和自定义触发条件列表

### Requirement: C2S触发关系展示
系统 SHALL 遍历已有C2S配置，展示哪些C2S会触发选中的S2C协议。

#### Scenario: 展示C2S触发列表
- **WHEN** 用户选中一个S2C协议
- **THEN** 系统遍历所有C2S配置文件，找出配置了该S2C的C2S，并展示列表
- **AND** 每条记录显示C2S名称、所属文件、回包配置（类型/次数/顺序等）

#### Scenario: C2S触发列表为只读
- **WHEN** 用户尝试编辑C2S触发列表中的项
- **THEN** 系统不允许直接编辑，提示需要在C2S模式下修改

### Requirement: 自定义触发条件管理
系统 SHALL 支持用户添加、编辑、删除非C2S触发的自定义条件。

#### Scenario: 添加自定义触发条件
- **WHEN** 用户点击添加按钮并填写条件信息
- **THEN** 新条件添加到自定义触发条件列表
- **AND** 可配置类型（必然/条件）、次数（一次/多次）、顺序状态、备注等

#### Scenario: 编辑自定义触发条件
- **WHEN** 用户双击自定义触发条件列表中的项
- **THEN** 弹出编辑对话框，可修改条件信息

#### Scenario: 删除自定义触发条件
- **WHEN** 用户选中条件并点击删除或按Delete键
- **THEN** 条件从列表中移除

### Requirement: 自定义触发条件持久化
系统 SHALL 将自定义触发条件保存到S2C所属dnet对应的JSON配置文件中，与C2S配置共存。

#### Scenario: 保存自定义触发条件
- **WHEN** 用户修改自定义触发条件后保存
- **THEN** 条件保存到dnet对应的JSON文件（如`nethero.json`包含C2S配置和S2C触发条件）

#### Scenario: 加载自定义触发条件
- **WHEN** 用户选择S2C协议
- **THEN** 系统从该S2C所属dnet对应的JSON文件加载已保存的自定义触发条件

### Requirement: S2C模式详情展示
系统 SHALL 在S2C模式下部展示选中项的详情信息。

#### Scenario: 展示C2S触发详情
- **WHEN** 用户在C2S触发列表中选中一项
- **THEN** 详情区域显示该C2S的详细信息（名称、描述、字段列表）
- **AND** 同时显示当前S2C的详细信息

#### Scenario: 展示自定义条件详情
- **WHEN** 用户在自定义触发条件列表中选中一项
- **THEN** 详情区域显示该条件的完整信息
- **AND** 同时显示当前S2C的详细信息
