# Capability: protocol-config-gui

## MODIFIED Requirements

### Requirement: 设置持久化
GUI工具 MUST 将用户设置保存到本地文件，使用相对路径格式以支持项目迁移。

#### Scenario: 保存设置为相对路径
- Given 用户选择了proto目录为 "F:\AI\dnet\proto"
- And 应用程序位于 "F:\AI\dnet\clientscript"
- When 保存设置
- Then gui_settings.json中保存相对路径 "../proto"

#### Scenario: 加载相对路径设置
- Given gui_settings.json包含相对路径 "../proto"
- And 应用程序位于 "F:\AI\dnet\clientscript"
- When 加载设置
- Then proto_dir转换为绝对路径 "F:\AI\dnet\proto"

#### Scenario: 项目迁移后设置仍有效
- Given 项目从 "F:\AI\dnet" 迁移到 "D:\projects\dnet"
- And gui_settings.json包含相对路径 "../proto"
- When 在新位置启动应用
- Then proto_dir正确解析为 "D:\projects\dnet\proto"
