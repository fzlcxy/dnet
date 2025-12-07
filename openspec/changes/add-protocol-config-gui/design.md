# 协议配置GUI工具设计文档

## 上下文
当前项目使用.dnet文件定义网络协议，包含C2S（客户端到服务器）和S2C（服务器到客户端）两种协议类型。开发者需要明确知道每个C2S请求会收到哪些S2C响应，以及这些响应的顺序和条件。

## 目标 / 非目标

### 目标
- 提供直观的GUI界面，方便配置C2S到S2C的映射关系
- 支持S2C响应的顺序管理和条件配置
- 自动验证配置的有效性
- 配置文件与proto目录结构保持一致

### 非目标
- 不修改或生成.dnet协议文件本身
- 不提供协议的运行时测试功能
- 不支持协议字段级别的详细配置

## 技术决策

### GUI框架选择
**决策**: 使用Tkinter
**原因**:
- Python标准库，无需额外依赖
- 跨平台支持
- 足够满足表单和树形控件需求
- 项目组熟悉度高

**备选方案**: PyQt5（更现代但需要额外依赖）

### 配置文件格式
**决策**: JSON格式
**原因**:
- 易于解析和生成
- 支持嵌套结构（C2S -> 多个S2C）
- 人类可读，便于手动编辑
- 支持顺序数组和条件配置

**JSON结构设计**:
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

### GUI界面布局设计

#### 整体布局
主窗口分为左右两部分，左侧占40%宽度，右侧占60%宽度。

#### 左侧 - C2S部分（从上到下）

1. **dnet过滤栏** (高度: 30px)
   - 输入框：用户输入关键字过滤dnet文件
   - 单选按钮："仅显示包含C2S的dnet" - 选中时过滤掉纯S2C的dnet文件

2. **dnet文件选择面板** (高度: 30%)
   - 树形控件（Treeview）
   - 显示proto目录下所有.dnet文件
   - 支持目录层级结构（如proto/x_huodong/nethuodong.dnet）
   - 点击选中某个dnet文件

3. **C2S协议面板** (高度: 40%)
   - 列表控件（Listbox或Treeview）
   - 显示选中dnet文件的所有C2S协议
   - 显示格式：协议名称 - 协议描述
   - 点击选中某个C2S协议

4. **C2S详情面板** (高度: 30%)
   - 只读文本框
   - 显示选中C2S协议的详细信息：
     - 协议名称
     - 协议描述
     - 字段列表（字段名、类型、描述）

#### 右侧 - S2C部分（从上到下）

1. **配置的S2C面板** (高度: 35%)
   - 标题："当前C2S的响应配置"
   - 列表控件，显示列：顺序 | 协议名称 | 类型 | 条件说明
   - 每行S2C可选中操作：
     - "上移"/"下移"按钮 - 调整响应顺序
     - "设置条件"按钮 - 弹出对话框选择类型（必然回包/按条件回包）并输入条件说明
     - "删除"按钮 - 从配置中移除
   - 支持拖拽排序

2. **选择配置面板** (高度: 40%)
   - 分为左右两部分：
     - **左侧** (宽度: 35%)
       - 标题："包含S2C的dnet文件"
       - 列表控件，显示所有包含S2C协议的dnet文件
       - 点击选中某个dnet文件
     - **右侧** (宽度: 65%)
       - 标题："S2C协议列表"
       - 列表控件，显示选中dnet文件的所有S2C协议
       - 显示格式：协议名称 - 协议描述
       - **双击**某个S2C协议，自动添加到上方"配置的S2C面板"

3. **S2C详情面板** (高度: 25%)
   - 只读文本框
   - 显示选中S2C协议的详细信息：
     - 协议名称
     - 协议描述
     - 字段列表（字段名、类型、描述）

#### 顶部菜单栏
- **文件**
  - 保存配置 (Ctrl+S)
  - 导入配置
  - 导出配置
  - 退出
- **编辑**
  - 撤销 (Ctrl+Z)
  - 重做 (Ctrl+Y)
- **工具**
  - 验证所有配置
  - 刷新dnet文件列表
- **帮助**
  - 使用说明
  - 关于

### 目录结构设计

```
项目根目录/
├── proto/                    # 协议文件目录（已存在）
│   ├── nethero.dnet
│   ├── netmap.dnet
│   └── x_huodong/
│       └── nethuodong.dnet
├── clientconfig/             # 配置文件目录（新建）
│   ├── nethero.json
│   ├── netmap.json
│   └── x_huodong/
│       └── nethuodong.json
└── clientscript/             # GUI脚本目录（新建）
    ├── main.py              # GUI主程序入口
    ├── dnet_parser.py       # .dnet文件解析模块
    ├── config_manager.py    # 配置文件管理模块
    ├── gui_main_window.py   # 主窗口实现
    └── gui_widgets.py       # 自定义控件
```

### 核心模块设计

#### 1. dnet_parser.py - 协议文件解析器
```python
class DnetParser:
    def parse_file(self, file_path: str) -> DnetProtocol:
        """解析单个.dnet文件"""

    def scan_directory(self, proto_dir: str) -> List[DnetFile]:
        """递归扫描proto目录"""

class DnetProtocol:
    """协议信息数据类"""
    file_path: str
    file_name: str
    description: str
    c2s_list: List[Protocol]
    s2c_list: List[Protocol]

class Protocol:
    """单个协议数据类"""
    name: str
    description: str
    fields: List[Field]
```

#### 2. config_manager.py - 配置管理器
```python
class ConfigManager:
    def load_config(self, dnet_file: str) -> C2SConfig:
        """加载对应的JSON配置文件"""

    def save_config(self, dnet_file: str, config: C2SConfig):
        """保存配置到JSON文件"""

    def validate_config(self, config: C2SConfig, dnet: DnetProtocol) -> List[str]:
        """验证配置的S2C是否存在于dnet文件中"""

class C2SConfig:
    """C2S配置数据类"""
    dnet_file: str
    mappings: Dict[str, C2SMapping]

class C2SMapping:
    """单个C2S的映射配置"""
    c2s_name: str
    responses: List[S2CResponse]

class S2CResponse:
    """S2C响应配置"""
    protocol: str
    order: int
    type: str  # "必然回包" 或 "按条件回包"
    condition: str
```

#### 3. gui_main_window.py - GUI主窗口
```python
class MainWindow(tk.Tk):
    def __init__(self):
        # 初始化界面组件
        self.setup_menu()
        self.setup_left_panel()  # C2S部分
        self.setup_right_panel()  # S2C部分

    def on_dnet_selected(self, dnet_file: str):
        """当用户选择dnet文件时"""

    def on_c2s_selected(self, c2s_name: str):
        """当用户选择C2S协议时"""

    def on_s2c_double_click(self, s2c_name: str):
        """当用户双击S2C协议时，添加到配置"""

    def save_current_config(self):
        """保存当前编辑的配置"""
```

## 用户交互流程

### 主要操作流程

1. **启动应用**
   - 扫描proto目录，加载所有.dnet文件
   - 在左侧显示文件树

2. **配置C2S回包**
   - 用户在左侧选择dnet文件
   - 显示该文件的所有C2S协议
   - 用户选择某个C2S协议
   - 加载已有配置（如果存在）
   - 用户在右侧下方选择包含S2C的dnet文件
   - 双击S2C协议添加到配置
   - 调整顺序、设置条件
   - 保存配置

3. **验证配置**
   - 用户点击"工具 -> 验证所有配置"
   - 系统检查所有配置文件
   - 标记无效的S2C配置（不存在于对应的dnet文件中）
   - 显示验证报告

## 风险与权衡

### 风险1: .dnet文件格式变化
**风险**: 如果.dnet文件格式发生变化，解析器需要更新
**缓解**:
- 使用正则表达式匹配，提高容错性
- 提供配置选项，允许用户手动指定解析规则

### 风险2: 配置文件冲突
**风险**: 多人同时编辑配置文件可能产生冲突
**缓解**:
- 提供配置合并功能
- 添加版本控制提示
- 保存时检测文件是否被外部修改

### 风险3: 性能问题
**风险**: 大量dnet文件时，加载和渲染可能较慢
**缓解**:
- 使用懒加载，仅在需要时解析dnet文件
- 缓存解析结果
- 提供进度提示

## 迁移计划

由于这是新增功能，不涉及数据迁移。但需要：
1. 创建clientconfig和clientscript目录
2. 提供示例配置文件和使用说明
3. 对现有proto目录进行备份（可选）

## 开放问题

1. 是否需要支持跨文件引用？（例如，C2S在file1.dnet，但S2C在file2.dnet）
   - **建议**: 第一版支持，右侧可以选择任意dnet文件的S2C

2. 条件说明是否需要结构化？
   - **建议**: 第一版使用自由文本，后续可以考虑添加条件模板

3. 是否需要支持多语言界面？
   - **建议**: 第一版仅支持中文，预留国际化接口

4. 配置文件是否需要加密或签名？
   - **建议**: 第一版使用明文JSON，便于调试和手动编辑
