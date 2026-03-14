# Agent 驱动开发：如何打造 AI 原生的工程项目

> 代码库不仅是跑在服务器上的程序，更是喂给 AI 的提示词。

## 第一部分：方法论篇 —— 重新定义开发范式

### 一、 开篇：什么是 ADD (AI-Driven Development)
我们正站在一个转折点上。过去二十年，我们习惯了这样的开发流程：产品经理写需求文档 → 架构师设计系统 → 工程师写代码 → 测试写用例 → 上线。每个环节都在努力"翻译"意图，但信息在传递中不断丢失。

现在，AI Agent 已经具备成为项目"核心开发成员"的能力。它不仅能补全代码，还能理解业务规范、生成实现逻辑、自主验收质量。但这带来一个直击灵魂的新问题：**你的代码库，是为人类设计的，还是为 AI 设计的？**

**为什么是现在？**
1. **上下文窗口爆发**：从 4K tokens 到 200K+（部分模型已达 1M+），AI 现在能"读完"整个代码库。
2. **工具链完善**：AI 不再只是聊天，它能读取文件、执行代码、运行测试、操作浏览器。
3. **协作模式验证**：越来越多的团队证实，人机配对编程的效率确实高于纯人工。

### 二、 ADD 的核心循环与第一性原理
在实际工程项目中，ADD 不是要颠覆传统的 RD 开发 + QA 测试流程，而是让 AI 成为 RD 的"配对程序员"。其核心循环为：
`锚定 (Anchor) → 生成 (Generate) → 审视 (Review)`

1. **锚定**：RD 编写高密度的规范/Spec，清晰描述"要什么"。
2. **生成**：AI 基于上下文实现逻辑，填充"怎么做"。
3. **审视**：RD 审查代码逻辑，QA 进行功能测试验证。

这里推导出一个核心公式：**代码质量 = 上下文清晰度 × Agent 能力**
当 Agent 能力固定时，**上下文清晰度**就成了决定性因素。这就要求我们的工程项目必须具备以下三大"AI 原生"特质。

### 三、 AI 原生项目的三大工程特质

#### 特质一：显性化的上下文 (Explicit Context)
**痛点**：AI 没有人类的"隐性知识"——团队约定、历史决策、未成文的"潜规则"，这些对人是常识，对 AI 却是盲区。
**方法**：Docs-as-System-Prompt（文档即系统提示词）。将隐性知识显性化，为项目及核心模块建立专属的上下文文件（如 `.ai-context.md`、`AGENTS.md`），明确告知 AI 模块的职责边界、业务意图与关键约束。
**关键手段**：
- 项目级 `AGENTS.md` 定义全局规则（禁止操作、命名约定、技术栈约束）
- 模块级 `.ai-context.md` 描述职责边界、核心文件、设计决策
- 所有上下文文件标注 `generated_by`、`verified_at`、`provenance`，确保可追溯

#### 特质二：原子化与令牌经济 (Atomicity & Token Economics)
**痛点**：巨型文件会迅速耗尽 LLM 的上下文窗口，增加 AI 理解修改影响的难度；即使窗口足够大，**成本与速度**依然是不可忽视的约束。
**方法**：极端模块化 + 单一职责原则。将文件保持在合理规模（推荐 < 500 行），让每个文件"自包含"，AI 或人类都可以独立理解其职责。
**关键手段**：
- 单文件 < 500 行（CI 可自动检查），超出即拆分
- 目录嵌套不超过 3 层，避免"深处"代码被遗忘
- 模块边界清晰，依赖关系单向，减少上下文交叉污染
- **上下文压缩**：Claude Code 的 `/compact` 命令可在长对话中压缩历史，节省 token 消耗

#### 特质三：自我验证机制 (Self-Verification)
**痛点**：AI 加载大量上下文时，细节出现幻觉的概率会大大提升。人类有直觉能快速发现"不对劲"，但 AI 缺乏这种"感觉"——它需要显式的验证机制来发现自己错了。
**方法**：为 AI 设计"自我纠错"的闭环，让它在生成后能自动发现问题、修正错误。核心原则：**让机器可验证的，就不要依赖人眼审查**。
**关键手段**：
- 强类型护栏：TypeScript / Rust / Pydantic，编译期拦截错误
- 测试驱动生成：先写测试用例，AI 生成实现后自动运行，失败即反馈
- Lint + Schema 验证：ESLint / Clippy 拦截风格问题，JSON Schema / Protobuf 校验数据结构
- **置信度评分**：Anthropic 官方的 code-review 插件对每个问题评分 0-100，只输出置信度 ≥80 的问题，有效过滤误报
- **多 Agent 并行审查**：从不同视角（simplicity/DRY、bugs/correctness、conventions）并行审查，交叉验证结果

### 四、 人类角色的进化
在 ADD 模式下，人类从"Coder（码农）"进化为：
- **🏗️ Architect（架构师）**：设计系统边界、接口定义与数据流向。
- **📋 Product Owner（产品负责人）**：定义业务意图与验收标准，用自然语言描述需求。
- **🔍 Reviewer（审查者）**：人机共同验收，检查 AI 逻辑的正确性与边界覆盖。
**人类的核心工作：维护语义契约和验收标准。**

### 五、 边界与局限：ADD 的冷思考
ADD 并非银弹，推行前需认清其边界：
1. **复合错误率**：AI 单步准确率虽高，但在长链路任务中误差会放大。ADD 更适合探索性开发和非关键路径，而非核心系统的全部托付。
2. **文档腐化风险**：上下文文档若与代码脱节，会引发更致命的"逻辑幻觉"。
3. **隐形成本**：频繁加载庞大上下文会带来显著的 API 成本和响应延迟。
4. **企业合规**：将核心业务规则传给云端大模型可能面临数据隐私和监管风险。
5. **认知负荷与人才断层**：审查 AI 完美风格下潜藏的 Bug 极耗心力；若只让初级工程师做"监工"，将失去培养未来架构师的土壤。
6. **遗留系统阻力**：对高度耦合的遗留系统强推 ADD 成本极高，需采取渐进式策略。

---

## 第二部分：实践篇 —— AI 原生项目的搭建与改造

### 场景一：从零开始 —— 用工程规范驱动 Agent 开发

新项目是最好的 ADD 实践场景。你不需要与遗留代码抗争，可以从第一天就建立 AI 友好的工程结构。

> **快速决策**：如果是**全新项目**，从场景一开始；如果是**现有项目改造**，跳转到场景二。

#### 步骤 1：准备工程规范

将 ADD 工程规范复制到项目根目录：

```
project/
├── ADD-工程规范/
│   ├── README.md          # 核心原则 + 快速开始
│   ├── spec.md            # 完整规范
│   └── templates/         # 上下文模板
│       ├── ai-context-project.md
│       └── ai-context-module.md
```

#### 步骤 2：编写项目级上下文

基于模板填写 `.ai-context.md`（放在项目根目录）：

```markdown
# 任务管理平台 - AI 开发指南

> generated_by: 团队维护
> verified_at: 2026-03-11
> provenance: 人工编写/AI辅助生成

## 核心架构
- 入口：`src/index.ts`
- 主要模块：tasks / users / notifications

## 技术栈
- 语言：TypeScript (ESM)
- 框架：Fastify
- 数据库：PostgreSQL + Prisma

## 关键约定
- API 响应格式：`{ code, data, message }`
- 错误处理：统一抛出 `AppError`
- 认证方式：JWT

## AI 开发规则
1. 按照 ADD-工程规范/spec.md 开发
2. 单文件不超过 500 行
3. 禁止 any，使用严格类型
4. 先写类型和接口，再写实现
5. 每个模块必须有 .ai-context.md
```

> **提示**：项目级上下文可由 AI 辅助生成。提供项目的功能描述和技术栈，让 AI 基于模板生成初稿，人工审核后补充即可。

#### 步骤 3：让 Agent 理解规范

在 Claude Code 或 Cursor 中，提供初始指令：

```
请阅读以下文件，理解项目规范后开始开发：
1. ADD-工程规范/spec.md - 完整的工程规范
2. .ai-context.md - 项目上下文和开发规则

任务：基于以上规范，创建项目脚手架，包括：
- 目录结构（按 spec.md 1.1 节）
- 全局类型定义
- 核心模块的 .ai-context.md
```

#### 步骤 4：增量开发循环

每次开发新模块时：

1. **锚定**：先编写该模块的 `.ai-context.md`（可由 AI 基于功能描述辅助生成）
2. **生成**：让 Agent 基于上下文生成代码
3. **审视**：检查是否符合规范（文件大小、类型定义、文档完整性）

> **提示**：模块级 `.ai-context.md` 同样可以由 AI 生成。在开发新模块时，可让 AI 根据功能需求先创建上下文文件，人工补充业务规则和约束即可。

```
# 示例指令
请按照 ADD-工程规范 开发 users 模块：
1. 先阅读 users/.ai-context.md 理解需求
2. 在 src/modules/users/ 下创建：
   - types.ts（类型定义）
   - service.ts（业务逻辑）
   - controller.ts（API 处理）
3. 确保每个文件 < 500 行
```

#### 步骤 5：持续校验

在 CI/CD 中加入检查：

```bash
# 检查文件大小
find src -name "*.ts" -exec wc -l {} \; | awk '$1 > 1000 {print "ERROR: " $2 " has " $1 " lines"}'

# 类型检查
pnpm run typecheck

# 测试覆盖率
pnpm run test --coverage
```

**更佳实践：pre-commit hook 配置**

创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: local
    hooks:
      - id: check-file-size
        name: 检查文件大小
        entry: bash -c 'find src -name "*.ts" -exec wc -l {} \; | awk "$1 > 1000 {print \"ERROR: \" $2 \" has \" $1 \" lines\"; exit 1}"'
        language: system
        stages: [pre-commit]
        
      - id: check-types
        name: 类型检查
        entry: pnpm run typecheck
        language: system
        stages: [pre-commit]
```

#### 完整示例：从 0 创建任务管理 API

```bash
# 1. 初始化项目
mkdir task-api && cd task-api
pnpm init

# 2. 添加工程规范
mkdir ADD-工程规范
# ... 复制规范文件

# 3. 创建项目上下文
cat > .ai-context.md << 'EOF'
# 任务管理平台 - AI 开发指南

> generated_by: 团队维护
> verified_at: 2026-03-11
> provenance: 人工编写

## 核心架构
- 入口：src/index.ts
- 主要模块：tasks / users

## 技术栈
- 语言：TypeScript (ESM)
- 框架：Fastify
- 数据库：PostgreSQL + Prisma

## 关键约定
- API 响应格式：{ code, data, message }
- 错误处理：统一抛出 AppError

## AI 开发规则
1. 单文件不超过 500 行
2. 禁止 any，使用严格类型
3. 先写类型和接口，再写实现
EOF

# 4. 让 Agent 创建项目脚手架
# 在 Claude Code/Cursor 中执行：
# "请阅读 ADD-工程规范/spec.md 和 .ai-context.md，
#  然后创建 Fastify + Prisma 项目脚手架"
```

---

### 场景二：现有项目改造 —— 用 add-knowledge-builder Skill

注：谨慎对现有代码进行改造，可优先使用 [Nexus-skills](https://github.com/Haaaiawd/Nexus-skills) 对项目信息进行整理，增强AI对项目的掌握能力。

现有项目的 ADD 化改造更复杂，需要先理解代码结构，再逐步注入上下文。我们提供了 **add-knowledge-builder** skill 来自动化这个过程。

> **前置条件**：将 add-knowledge-builder skill 安装到 OpenClaw 的 skills 目录  
> 安装方式：将 skill 目录复制到 `~/.openclaw/workspace/skills/add-knowledge-builder/`

#### 改造流程：PROBE-ADD 协议

```
P (Profile)   → 收集项目原始数据（文件结构、Git 热点、依赖关系）
R (Reason)    → 分析代码，推断系统边界和模块职责
O (Object)    → 提出质疑点，标记证据不足的推断
B (Benchmark) → 验证推断，校验所有结论
E (Emit)      → 输出上下文文件和知识库
```

#### 使用方法

**1. 分析项目结构**

```bash
uv run scripts/analyze_project.py /path/to/project
```

输出分析报告，包括：
- 文件大小统计（识别 >1000 行的文件）
- 目录嵌套深度（识别 >3 层的路径）
- 模块边界推断
- Git 热点文件
- 现有 AI 上下文文件检查

**2. 生成模块上下文**

```bash
uv run scripts/generate_context.py /path/to/module --type module
```

为指定模块生成 `.ai-context.md`，包含：
- 推断的职责
- 核心文件列表
- 设计决策（待补充）
- 约束条件（待补充）
- Evidence Gaps（证据不足的部分）

**3. 生成项目级知识库**

```bash
uv run scripts/generate_context.py /path/to/project --type project
```

创建 `.ai-context/` 目录：

```
.ai-context/
├── INDEX.md            # 冷启动入口（< 2000 tokens）
├── systems.md          # 系统边界 + 代码位置
├── dependencies.md     # 依赖关系图
└── concept_model.json  # 机器可读知识图谱
```

**4. 人工校验与补充**

生成的上下文文件中标注了 `evidence gap`，需要人工确认和补充：

```markdown
## Evidence Gaps

- [ ] 模块间的依赖关系需要人工确认
- [ ] 核心业务逻辑需要补充详细说明
- [ ] 缓存策略：设计文档提到 Redis，但代码中未发现实现
```

#### 改造优先级

根据分析报告，按以下优先级改造：

| 优先级 | 改造项 | 说明 |
|--------|--------|------|
| P0 | 拆分 >1000 行文件 | 影响可维护性 |
| P0 | 创建 .ai-context.md | AI 理解入口 |
| P1 | 创建 .ai-context/ | 大型项目知识库 |
| P1 | 消除 >5 层嵌套 | 代码质量 |
| P2 | 补充类型定义 | 防止幻觉 |
| P2 | 同步文档与代码 | 持续维护 |

#### 改造示例

假设分析报告显示 `user-service.ts` 有 2000 行：

```bash
# 1. 分析当前状态
uv run scripts/analyze_project.py ./src/modules/user

# 输出：
# ❌ user-service.ts (2000 行) - 需要拆分
# ❌ 缺少 .ai-context.md
# ⚠️  目录嵌套深度：4 层

# 2. 拆分文件（由 Agent 或人工执行）
# user-service.ts → types.ts + repository.ts + service.ts + handler.ts

# 3. 生成上下文
uv run scripts/generate_context.py ./src/modules/user --type module

# 4. 人工校验和补充
# 编辑 .ai-context.md，补充业务规则和约束
```

#### Provenance 标注规范

所有生成的文件都带有溯源标注：

```markdown
> generated_by: add-knowledge-builder
> verified_at: 2026-03-11
> provenance: code-analyzed
```

**provenance 值含义**：
- `code-analyzed`：代码分析得出
- `git-inferred`：Git 历史推断
- `docs-inferred`：文档推断
- `manual-review`：人工审查确认

---

## 结语

回到开篇的那个观点：**代码库不仅是跑在服务器上的程序，更是喂给 AI 的提示词。**

在 ADD 时代，你的代码库本身就是一种"提示词工程"。你写的每一行注释、每一个类型定义、每一个模块划分，都是在告诉 AI："这是理解这个项目的方式。"

那些为 AI 设计的项目，会让 AI 更高效、更准确、更少幻觉。而那些仍为人类设计的项目，AI 会挣扎、会误解、会犯错。

选择权在你。

以上是openclaw的结语，作为本文的人类作者，我想以我对AI认知结构的三个层级作为本文的真正结尾。

- 第一层：我看AI不是人，AI干不了人干的活。

- 第二层：我看AI是人，人能干的AI也能干，对待AI像对待一个人一样。

- 第三层：我看AI还是不是人，AI和人的思考能力虽然类似，但对世界的观测方式截然不同，正如本文所提及，AI主导的项目必然是需要针对AI来特化的，其他需要agent来完成的工作类似。

---

**参考资源与工具**

| 资源 | 说明 |
|------|------|
| [Claude Code](https://github.com/anthropics/claude-code) | Anthropic 官方 AI 编程工具，支持 CLAUDE.md 上下文、Skills 系统、多 Agent 并行审查 |
| [Claude Code Plugins](https://github.com/anthropics/claude-code/tree/main/plugins) | 官方插件：code-review（置信度评分）、feature-dev（7 阶段开发流程）、security-guidance 等 |
| [Agent Skills](https://github.com/anthropics/skills) | Anthropic 官方 Skills 规范与示例，支持可重用工作流 |
| [OpenClaw](https://github.com/openclaw/openclaw) | 开源 AI 助手框架，`AGENTS.md` 是 AI 原生项目指南的绝佳示例 |
| [Nexus-skills](https://github.com/Haaaiawd/Nexus-skills) | AI 代码库知识库生成工具，PROBE 协议设计参考 |
| [**add-knowledge-builder**](https://github.com/BingChenqiu/AI-Agent-Driven-Development) | 现有项目 ADD 化改造 skill|
| [**ADD-工程规范**](https://github.com/BingChenqiu/AI-Agent-Driven-Development) | 完整的 AI 原生工程规范（见附件） |
