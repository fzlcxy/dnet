## Context
当前工具的C2S模式是从C2S角度配置回包情况。但实际工作中，开发者有时需要从S2C角度反向查看：某个S2C会被哪些C2S触发，以及是否有其他非C2S触发条件。

## Goals / Non-Goals
- Goals:
  - 提供S2C视角的配置查看和编辑
  - 支持遍历现有C2S配置获取触发关系
  - 支持用户自定义非C2S触发条件
  - 配置信息和C2S模式一致（一次/多次、必然/条件回包等）
- Non-Goals:
  - 不修改现有C2S配置JSON格式
  - 不需要自动同步修改C2S配置（S2C模式下C2S触发关系为只读展示）

## Decisions
1. **模式切换方式**: 使用Notebook（Tab）切换C2S模式和S2C模式，保持两个独立面板
2. **S2C触发条件存储**:
   - C2S触发关系：从现有c2s配置JSON中遍历读取（只读）
   - 自定义触发条件：存储到dnet对应的JSON文件中（如`nethero.json`同时包含C2S配置和S2C自定义触发条件）
3. **数据结构**: 新增S2CTrigger类，包含触发条件名称、配置信息（type/count/condition等）

## Risks / Trade-offs
- 遍历所有C2S配置文件获取S2C触发关系可能有性能问题 → 首次加载时缓存
- 自定义触发条件与C2S触发关系分开存储可能造成管理混乱 → 界面上明确区分显示

## Migration Plan
- 无需迁移，新增功能

## Open Questions
- 无
