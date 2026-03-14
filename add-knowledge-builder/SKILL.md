---
name: add-knowledge-builder
description: ADD 知识库构建工具。用于：(1) 分析项目结构识别 AI 友好改造点，(2) 为模块生成 .ai-context.md 上下文，(3) 创建项目级知识库 .ai-context/，(4) 识别需要重构的大文件和深层嵌套，(5) 帮助 AI Agent 快速理解现有项目。基于 Nexus-skills PROBE 协议与 ADD 工程规范设计。
---

# ADD Knowledge Builder - 现有项目 AI 原生化改造工具

将现有项目改造为 AI 友好的工程结构，基于 ADD (Agent-Driven Development) 工程规范。

## 核心流程：PROBE-ADD 协议

改造遵循五阶段协议，防止"第一眼假设变结论"：

```
P (Profile)   → 收集项目原始数据（文件结构、Git 热点、依赖关系）
R (Reason)    → 分析代码，推断系统边界和模块职责
O (Object)    → 提出质疑点，标记证据不足的推断
B (Benchmark) → 验证推断，校验所有结论
E (Emit)      → 输出上下文文件和知识库
```

**阶段不可跳过**，每个阶段必须完成后才能进入下一阶段。

## 快速开始

### 1. 分析项目

```bash
uv run {baseDir}/scripts/analyze_project.py /path/to/project
```

输出：
- 文件大小统计（识别 >1000 行的文件）
- 目录嵌套深度（识别 >3 层的路径）
- 模块边界推断
- Git 热点文件（如有 Git 历史）

### 2. 生成模块上下文

```bash
uv run {baseDir}/scripts/generate_context.py /path/to/module --type module
```

为指定模块生成 `.ai-context.md`。

### 3. 生成项目级知识库

```bash
uv run {baseDir}/scripts/generate_context.py /path/to/project --type project
```

创建 `.ai-context/` 目录结构，包含 INDEX.md 等文件。

## 输出产物

### 模块级上下文 (`.ai-context.md`)

每个核心模块根目录下的上下文文件：

```markdown
# 模块名称

## 职责
- [推断的职责]

## 设计决策
- [识别的决策]

## 约束
- [发现的约束]

## Evidence Gaps
- [证据不足的部分]
```

### 项目级知识库 (`.ai-context/`)

```
.ai-context/
├── INDEX.md            # 冷启动入口（< 2000 tokens）
├── systems.md          # 系统边界 + 代码位置
├── dependencies.md     # 依赖关系图
└── concept_model.json  # 机器可读知识图谱
```

## 改造检查清单

使用分析结果，按优先级改造：

### P0 - 必须改造
- [ ] 拆分 >1000 行的文件
- [ ] 为核心模块添加 `.ai-context.md`
- [ ] 创建项目级 `.ai-context/INDEX.md`

### P1 - 建议改造
- [ ] 消除 >5 层嵌套的函数
- [ ] 补充缺失的类型定义
- [ ] 扁平化 >3 层的目录结构

### P2 - 持续改进
- [ ] 同步代码与文档
- [ ] 补充公共 API 文档
- [ ] 增加测试覆盖

## 模板文件

位于 `assets/templates/`：

- `ai-context-module.md` - 模块上下文模板
- `ai-context-project.md` - 项目上下文模板
- `INDEX.md` - 知识库入口模板

## 详细规范

完整的 ADD 工程规范见 [references/spec.md](references/spec.md)，包含：

- 项目结构规范
- 代码编写规范
- 文档规范
- 审查清单
- 知识库管理规范
- 不确定性表达规范

## Provenance 标注规范

所有生成的上下文文件必须标注信息来源：

```markdown
> generated_by: add-transformer v1.0
> verified_at: YYYY-MM-DD
> provenance: <来源说明>
```

**provenance 值**：
- `ast-analyzed` - AST 分析得出
- `git-inferred` - Git 历史推断
- `docs-inferred` - 文档推断
- `manual-review` - 人工审查确认
- `partial-coverage` - 部分覆盖（需说明缺口）

## 诚实的证据缺口

当证据不足时，必须明确写出 `evidence gap`，而非使用模糊词：

```markdown
✅ 推荐：
evidence gap: 未发现入口文件直接引用，暂不标记为主系统

❌ 禁止：
待确认 · 可能是 · 疑似 · 也许 · 待定
```