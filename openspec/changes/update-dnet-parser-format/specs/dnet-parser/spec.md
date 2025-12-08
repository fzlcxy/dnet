# Capability: dnet-parser

## Overview
更新dnet文件解析器以支持新的文件格式。

## MODIFIED Requirements

### Requirement: 解析dnet文件头部信息
解析器 MUST 支持解析新格式的头部信息，包括VERSION、DESC、CMODULE、SMODULE字段。

#### Scenario: 解析新格式头部
- Given 一个新格式的dnet文件包含VERSION:1.0.0
- And 包含CMODULE:netfile.nethero
- And 包含SMODULE:netheroxx
- When 解析该文件
- Then 正确提取模块名称和描述信息

### Requirement: 解析协议段落
解析器 MUST 支持解析GS2C和C2GS段落标识符。

#### Scenario: 解析GS2C段落
- Given dnet文件包含GS2C:0xd1:0x1:段落
- When 解析该文件
- Then 识别为S2C协议列表

#### Scenario: 解析C2GS段落
- Given dnet文件包含C2GS:0xd1:段落
- When 解析该文件
- Then 识别为C2S协议列表

### Requirement: 解析协议定义
解析器 MUST 支持使用冒号分隔的协议定义格式。

#### Scenario: 解析协议定义
- Given 协议定义行为 "1:S2CAddHero:添加英雄"
- When 解析该行
- Then 提取协议序号为1
- And 提取协议名称为S2CAddHero
- And 提取协议描述为添加英雄

### Requirement: 解析字段定义
解析器 MUST 支持使用逗号分隔的字段定义格式。

#### Scenario: 解析字段定义
- Given 字段定义行为 "iHeroID,4,英雄ID"
- When 解析该行
- Then 提取字段名为iHeroID
- And 提取字段类型为4
- And 提取字段描述为英雄ID

## REMOVED Requirements

### Requirement: 旧格式点号分隔支持
移除对旧格式使用点号分隔的协议和字段定义的支持。

#### Scenario: 不再支持旧格式
- Given 一个旧格式dnet文件使用S2C.0xd1.段落
- When 解析该文件
- Then 无法识别协议列表
