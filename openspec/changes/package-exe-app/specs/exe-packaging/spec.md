# Capability: exe-packaging

## Overview
支持将协议配置GUI工具打包成Windows可执行文件。

## ADDED Requirements

### Requirement: 提供PyInstaller打包配置
系统 MUST 提供PyInstaller spec配置文件，用于打包应用程序。

#### Scenario: 使用spec文件打包
- Given 已安装PyInstaller
- When 执行 `pyinstaller protocol_config_gui.spec`
- Then 在dist目录生成可执行文件

### Requirement: 提供打包脚本
系统 MUST 提供一键打包脚本，简化打包流程。

#### Scenario: 运行打包脚本
- Given 已安装Python和PyInstaller
- When 执行 `build.bat`
- Then 自动完成打包并输出到dist目录

### Requirement: 打包后程序可独立运行
打包生成的exe MUST 能在无Python环境的Windows系统上运行。

#### Scenario: 在无Python环境运行
- Given 目标机器未安装Python
- And 已复制dist目录到目标机器
- When 双击运行exe文件
- Then 程序正常启动并显示GUI界面

### Requirement: 设置文件路径兼容
打包后的程序 MUST 正确处理设置文件的保存和加载路径。

#### Scenario: 打包后保存设置
- Given 运行打包后的exe程序
- When 修改设置目录并保存
- Then 设置文件保存在exe同级目录
- And 下次启动时能正确加载设置
