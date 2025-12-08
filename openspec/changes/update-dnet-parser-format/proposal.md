# Proposal: update-dnet-parser-format

## Summary
更新dnet解析器以支持新的文件格式，并删除旧格式支持。

## Motivation
- proto目录增加了新的dnet文件格式（xxx_new.dnet）
- 新格式使用逗号分隔符、新的段落标识符和版本号
- 需要统一使用新格式，删除旧格式文件

## Scope
- 更新 `dnet_parser.py` 解析器支持新格式
- 删除旧格式的dnet文件
- 重命名新格式文件（去掉_new后缀）

## 新旧格式对比

### 旧格式
```
#DNET
C2SMODULE：netfile.nethero.py
S2CMODULE:nethero.py
DESC:英雄相关协议

S2C.0xd1.
	1.S2CAddHero.添加英雄
		iHeroID.4b.英雄ID

C2S.0xd1.
	1.C2SUpdateHeroName.更新英雄名称
		iHeroID.4b.英雄ID
```

### 新格式
```
VERSION:1.0.0
DESC:英雄相关协议
CMODULE:netfile.nethero
SMODULE:netheroxx

GS2C:0xd1:0x1:
	1:S2CAddHero:添加英雄
		iHeroID,4,英雄ID
		forlist characterList:
			iCharID,2,个性ID

C2GS:0xd1:
	1:C2SUpdateHeroName:更新英雄名称
		iHeroID,4,英雄ID
```

### 主要变化
| 项目 | 旧格式 | 新格式 |
|------|--------|--------|
| 版本号 | 无 | VERSION:1.0.0 |
| 模块名 | C2SMODULE/S2CMODULE | CMODULE/SMODULE |
| S2C段落 | S2C.0xd1. | GS2C:0xd1:0x1: |
| C2S段落 | C2S.0xd1. | C2GS:0xd1: |
| 协议定义 | 1.Name.Desc | 1:Name:Desc |
| 字段定义 | name.type.desc | name,type,desc |
| 嵌套结构 | 不支持 | forlist xxx: |

## Status
draft
