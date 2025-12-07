# Design: package-exe-app

## Architecture Overview

### 打包结构
```
dist/
└── 协议配置工具/
    ├── 协议配置工具.exe    # 主程序
    ├── gui_settings.json   # 运行时生成的设置文件
    └── _internal/          # PyInstaller内部依赖
```

### PyInstaller配置要点

#### 1. 入口点
- 主程序入口: `clientscript/main.py`
- 应用名称: `协议配置工具`

#### 2. 数据文件处理
- gui_settings.json: 运行时在exe同级目录生成，无需打包

#### 3. 隐式导入
当前项目使用标准库，无需额外配置隐式导入：
- tkinter (Python标准库，自动包含)
- json (Python标准库)
- dataclasses (Python标准库)

#### 4. 路径处理
打包后需要正确处理路径，当前代码使用 `os.path.dirname(os.path.abspath(__file__))` 已经兼容。

对于PyInstaller打包，需要处理 `sys._MEIPASS` 的情况：
```python
def get_base_path():
    if getattr(sys, 'frozen', False):
        # 打包后运行
        return os.path.dirname(sys.executable)
    else:
        # 开发环境运行
        return os.path.dirname(os.path.abspath(__file__))
```

## Trade-offs

### 单文件 vs 文件夹模式
| 模式 | 优点 | 缺点 |
|------|------|------|
| 单文件(--onefile) | 分发简单，只有一个exe | 启动慢，需解压到临时目录 |
| 文件夹(--onedir) | 启动快，便于调试 | 文件较多，需要打包zip分发 |

**选择**: 文件夹模式，启动速度更快，用户体验更好

### 控制台窗口
- 使用 `--noconsole` 隐藏控制台窗口
- GUI程序不需要显示命令行窗口

## Implementation Notes

### spec文件关键配置
```python
a = Analysis(
    ['main.py'],
    pathex=['clientscript'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    ...
)

exe = EXE(
    ...
    name='协议配置工具',
    console=False,  # 隐藏控制台
    icon='icon.ico',  # 可选图标
)
```

### 打包命令
```bash
pyinstaller protocol_config_gui.spec
```

或使用简化命令：
```bash
pyinstaller --noconsole --name "协议配置工具" clientscript/main.py
```
