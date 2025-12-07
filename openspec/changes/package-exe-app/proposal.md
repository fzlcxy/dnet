# Proposal: package-exe-app

## Summary
支持将协议配置GUI工具打包成独立的Windows可执行文件(.exe)，方便用户无需安装Python环境即可直接运行。

## Motivation
- 当前工具需要Python环境才能运行，对非开发人员使用不友好
- 打包成exe可以方便分发和部署
- 提升用户体验，一键启动

## Scope
- 添加PyInstaller打包配置
- 创建打包脚本
- 处理资源文件和依赖

## Approach
使用PyInstaller将Python应用打包成单个exe文件或文件夹模式，包含所有依赖。

### 技术选型
- **PyInstaller**: 成熟稳定的Python打包工具，支持Windows/Mac/Linux
- 打包模式: 单文件夹模式（启动更快，便于调试）

### 打包内容
- main.py 主程序入口
- gui_main_window.py GUI实现
- config_manager.py 配置管理
- dnet_parser.py 协议解析器

## Out of Scope
- Mac/Linux平台打包（可后续扩展）
- 自动更新功能
- 安装程序制作（如NSIS）

## Dependencies
- PyInstaller库

## Risks
- 打包后文件体积较大（通常30-50MB）
- 杀毒软件可能误报

## Status
draft
