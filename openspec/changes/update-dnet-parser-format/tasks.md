# Tasks: update-dnet-parser-format

## Implementation Tasks

### Phase 1: 更新解析器
- [x] 修改 `dnet_parser.py` 支持新格式头部（VERSION, CMODULE, SMODULE）
- [x] 修改段落解析逻辑（GS2C/C2GS 替代 S2C/C2S）
- [x] 修改协议定义解析（冒号分隔替代点号）
- [x] 修改字段定义解析（逗号分隔替代点号）
- [x] 添加 forlist 嵌套结构支持（跳过处理）

### Phase 2: 清理旧文件
- [x] 删除旧格式dnet文件（nethero.dnet, netmap.dnet）
- [x] 重命名新格式文件（去掉_new后缀）
- [x] 转换 x_huodong/nethuodong.dnet 为新格式

### Phase 3: 验证
- [x] 测试解析器正确解析新格式
- [x] 语法检查通过

## Deliverables
- [x] 更新后的 dnet_parser.py
- [x] 清理后的 proto 目录（全部为新格式）
