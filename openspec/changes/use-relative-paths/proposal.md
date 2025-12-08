# Change: 设置目录使用相对路径

## Why
当前设置文件(gui_settings.json)保存绝对路径，导致项目在不同机器或目录迁移后设置失效。

## What Changes
- 修改设置保存逻辑，将绝对路径转换为相对路径后存储
- 修改设置加载逻辑，将相对路径转换为绝对路径使用
- 相对路径基于应用程序所在目录计算

## Impact
- Affected specs: protocol-config-gui
- Affected code: clientscript/gui_main_window.py
