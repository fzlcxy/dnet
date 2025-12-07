# 协议配置GUI规范

## ADDED Requirements

### Requirement: .dnet文件解析
系统SHALL能够解析proto目录下的.dnet协议文件，提取C2S和S2C协议信息。

#### Scenario: 解析包含C2S和S2C的.dnet文件
- **WHEN** 用户选择一个.dnet文件
- **THEN** 系统解析文件内容，提取所有C2S协议名称和S2C协议名称，并在GUI中显示

#### Scenario: 解析带子目录的proto结构
- **WHEN** proto目录包含子目录（如proto/x_huodong/nethuodong.dnet）
- **THEN** 系统递归扫描所有子目录，保持目录层级结构，并在GUI中以树形结构展示

### Requirement: C2S回包配置管理
系统SHALL允许用户为每个C2S协议配置对应的S2C响应列表，包括响应顺序、响应类型和条件说明。

#### Scenario: 双击添加S2C响应
- **WHEN** 用户在右侧S2C列表中双击某个S2C协议
- **THEN** 该S2C被添加到当前选中C2S的响应列表末尾，默认类型为"必然回包"

#### Scenario: 为C2S添加多个S2C响应
- **WHEN** 用户为同一个C2S协议添加多个S2C响应
- **THEN** 所有S2C都被记录在响应列表中，按添加顺序排列，每个响应有独立的顺序编号

#### Scenario: 移除C2S的S2C响应
- **WHEN** 用户点击删除按钮移除某个S2C响应
- **THEN** 该映射关系被删除，后续响应的顺序编号自动更新

#### Scenario: 调整S2C响应顺序
- **WHEN** 用户点击"上移"或"下移"按钮
- **THEN** 选中的S2C响应与相邻项交换位置，顺序编号更新

#### Scenario: 设置S2C响应类型和条件
- **WHEN** 用户点击"设置条件"按钮
- **THEN** 弹出对话框，用户可以选择响应类型（"必然回包"或"按条件回包"），并输入条件说明文本

#### Scenario: 显示S2C响应的完整信息
- **WHEN** 配置的S2C面板显示响应列表
- **THEN** 每行显示：顺序编号、协议名称、类型、条件说明（如果有）

### Requirement: 配置文件持久化
系统SHALL将配置保存为JSON格式文件，存储在clientconfig目录下，并保持与proto目录相同的目录结构。

#### Scenario: 保存配置到JSON文件
- **WHEN** 用户保存对nethero.dnet的配置
- **THEN** 系统在clientconfig/nethero.json中保存配置，包含该文件所有C2S的响应映射

#### Scenario: 保存子目录中的配置文件
- **WHEN** 用户保存对proto/x_huodong/nethuodong.dnet的配置
- **THEN** 系统在clientconfig/x_huodong/nethuodong.json中保存配置，自动创建必要的子目录

#### Scenario: 加载已有配置文件
- **WHEN** 用户打开一个已有配置的.dnet文件
- **THEN** 系统自动加载对应的JSON配置文件，在GUI中显示已配置的C2S-S2C映射

### Requirement: 配置验证
系统SHALL验证配置的S2C协议是否存在于对应的.dnet文件中。

#### Scenario: 验证合法的S2C配置
- **WHEN** 用户保存配置时，所有配置的S2C都存在于.dnet文件中
- **THEN** 验证通过，配置成功保存

#### Scenario: 检测不存在的S2C配置
- **WHEN** 用户配置的S2C不存在于当前.dnet文件中
- **THEN** 系统显示警告信息，标记无效的S2C配置，但允许保存

### Requirement: GUI用户界面布局
系统SHALL提供基于Tkinter的图形化用户界面，主窗口分为左右两部分，左侧为C2S部分（占40%宽度），右侧为S2C部分（占60%宽度）。

#### Scenario: 左侧C2S部分布局
- **WHEN** GUI启动时
- **THEN** 左侧从上到下依次显示：dnet过滤栏、dnet文件选择面板、C2S协议面板、C2S详情面板

#### Scenario: dnet过滤功能
- **WHEN** 用户在过滤栏输入关键字
- **THEN** dnet文件列表实时过滤，仅显示文件名包含关键字的文件

#### Scenario: 仅显示包含C2S的dnet文件
- **WHEN** 用户勾选"仅显示包含C2S的dnet"单选按钮
- **THEN** dnet文件列表仅显示包含至少一个C2S协议的文件，隐藏纯S2C协议文件

#### Scenario: 显示.dnet文件树形结构
- **WHEN** dnet文件选择面板加载
- **THEN** 以树形控件显示proto目录下所有.dnet文件，支持目录层级展开和收起

#### Scenario: 显示C2S协议列表
- **WHEN** 用户在dnet文件面板中点击选中某个.dnet文件
- **THEN** C2S协议面板显示该文件的所有C2S协议，格式为"协议名称 - 协议描述"

#### Scenario: 显示C2S详情
- **WHEN** 用户在C2S协议面板中点击选中某个C2S
- **THEN** C2S详情面板显示该协议的完整信息（协议名称、描述、字段列表）

#### Scenario: 右侧S2C部分布局
- **WHEN** 用户选中某个C2S协议
- **THEN** 右侧从上到下依次显示：配置的S2C面板、选择配置面板、S2C详情面板

#### Scenario: 显示配置的S2C响应列表
- **WHEN** 配置的S2C面板加载
- **THEN** 显示当前选中C2S已配置的S2C响应列表，列表列包括：顺序、协议名称、类型、条件说明，并提供上移、下移、设置条件、删除按钮

#### Scenario: 选择配置面板的左右分区
- **WHEN** 选择配置面板加载
- **THEN** 左侧显示所有包含S2C的dnet文件列表，右侧显示选中dnet文件的S2C协议列表

#### Scenario: 双击S2C添加到配置
- **WHEN** 用户在选择配置面板右侧的S2C列表中双击某个S2C
- **THEN** 该S2C被添加到上方配置的S2C面板中

#### Scenario: 显示S2C详情
- **WHEN** 用户在S2C列表中点击选中某个S2C
- **THEN** S2C详情面板显示该协议的完整信息（协议名称、描述、字段列表）

### Requirement: 配置保存功能
系统SHALL提供配置保存功能，支持菜单按钮和快捷键操作。

#### Scenario: 通过菜单保存配置
- **WHEN** 用户点击菜单栏"文件 -> 保存配置"
- **THEN** 系统保存当前编辑的所有配置到对应的JSON文件

#### Scenario: 通过快捷键保存配置
- **WHEN** 用户按下Ctrl+S快捷键
- **THEN** 系统保存当前编辑的所有配置到对应的JSON文件

#### Scenario: 保存成功提示
- **WHEN** 配置保存成功
- **THEN** 在状态栏或弹出提示框显示"配置已保存"消息

#### Scenario: 保存失败提示
- **WHEN** 配置保存失败（如文件权限问题）
- **THEN** 弹出错误对话框，显示失败原因

### Requirement: 批量操作支持
系统SHALL支持批量导入和导出配置文件。

#### Scenario: 导出当前配置
- **WHEN** 用户点击导出按钮
- **THEN** 系统将当前编辑的配置导出为JSON文件

#### Scenario: 批量导入配置
- **WHEN** 用户选择一个或多个JSON配置文件导入
- **THEN** 系统加载这些配置并更新GUI显示，如果有冲突则提示用户选择覆盖或合并

### Requirement: JSON配置文件格式
配置文件SHALL使用标准JSON格式，结构清晰，易于人工阅读和编辑，包含响应顺序、类型和条件信息。

#### Scenario: JSON文件结构
- **WHEN** 系统保存配置文件
- **THEN** JSON文件包含以下结构：文件名、协议描述、C2S映射对象，每个C2S包含描述和响应数组，每个响应包含协议名、顺序、类型和条件

#### Scenario: JSON文件示例格式
```json
{
  "dnet_file": "nethero.dnet",
  "description": "英雄相关协议",
  "c2s_mappings": {
    "C2SUpdateHeroName": {
      "description": "更新英雄名称",
      "responses": [
        {
          "protocol": "S2CUpdateHero",
          "order": 1,
          "type": "必然回包",
          "condition": ""
        },
        {
          "protocol": "S2CAddHero",
          "order": 2,
          "type": "按条件回包",
          "condition": "如果英雄不存在则创建新英雄"
        }
      ]
    }
  }
}
```
- **WHEN** 保存nethero.dnet的C2SUpdateHeroName配置
- **THEN** 生成上述格式的JSON文件，responses数组按order字段排序
