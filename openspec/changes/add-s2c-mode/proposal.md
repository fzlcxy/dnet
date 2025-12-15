# Change: 增加S2C模式面板

## Why
当前工具只支持C2S模式（从C2S角度配置回包S2C）。需要增加S2C模式，从S2C角度查看和配置哪些C2S会触发该S2C回包，以及支持用户自定义的触发条件。

## What Changes
- 增加S2C模式切换功能（模式选择按钮/Tab）
- 新建S2C模式面板布局：
  - 上部：S2C dnet文件选择 + S2C协议选择（类似C2S模式）
  - 中部：触发S2C的C2S列表（从已有配置中读取）+ 自定义触发条件列表
  - 下部：选中项的详情说明（C2S详情和S2C详情）
- 增加S2CTrigger数据结构，存储用户自定义的触发条件
- S2C触发条件配置保存到dnet对应的JSON文件中（与C2S配置共存）

## Impact
- Affected specs: s2c-mode（新增）
- Affected code:
  - gui_main_window.py - 新增S2C模式面板和切换逻辑
  - config_manager.py - 新增S2C触发条件配置管理
