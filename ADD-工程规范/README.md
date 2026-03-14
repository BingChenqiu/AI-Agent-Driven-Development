# ADD 工程规范

> 代码库不仅是跑在服务器上的程序，更是喂给 AI 的提示词。

本规范帮助你打造 **AI 原生 (AI-Native)** 的工程项目，让 AI Agent 高效理解、介入和生成高质量代码。

**定位**：本规范作为项目的一部分存在，是团队开发约定，而非外部调用的工具。

---

## 核心原则

```
代码质量 = 上下文清晰度 × Agent 能力
```

Agent 能力你无法控制，**上下文清晰度**是你唯一能控制的变量。

### 三大工程特质

| 特质 | 核心思想 | 一句话 |
|------|---------|--------|
| 显性化上下文 | 文档即 System Prompt | AI 没有"隐性知识"，所有逻辑必须写下来 |
| 原子化与令牌经济 | 小文件、扁平目录 | AI 只能处理有限上下文，每个文件要自包含 |
| 强类型护栏 | 类型 > 注释 > 自然语言 | 类型是最精确的约束，能直接消灭幻觉 |

### ADD 开发循环

```
锚定 (Anchor)   → 人类：编写规范/Spec + 类型定义
生成 (Generate)  → AI：基于上下文实现逻辑
审视 (Review)    → 人机：共同验收，迭代改进
```

---

## 文档结构

```
ADD-工程规范/
├── README.md                          ← 你在这里（核心原则 + 导航）
├── spec.md                            ← 完整规范（结构 + 编码 + 文档 + 审查 + 知识库）
└── templates/
    ├── ai-context-project.md          ← 项目级上下文模板
    └── ai-context-module.md           ← 模块级上下文模板
```

---

## 规范亮点（v3.0 新增）

### 知识库持久化

大型项目推荐创建 `.ai-context/` 目录，让 AI 会话间"传递记忆"：

```
.ai-context/
├── INDEX.md            # 冷启动入口（< 2000 tokens）
├── systems.md          # 系统边界
├── dependencies.md     # 依赖关系图
└── concept_model.json  # 机器可读图谱
```

### Provenance 标注

所有知识库文件必须标注信息来源：

```markdown
> generated_by: 团队维护
> verified_at: 2026-03-10
> provenance: code-verified
```

### 不确定性表达

禁止裸写模糊词，必须指出缺失的是哪一类证据：

```markdown
✅ evidence gap: 未发现入口文件直接引用，暂不标记为主系统
❌ 待确认
```

### 质疑机制

防止"第一眼假设变结论"，AI 生成重要代码前应自检验证。

---

## 快速开始

### 新项目

```bash
# 1. 复制模板到项目根目录
cp templates/ai-context-project.md  your-project/.ai-context.md

# 2. 填写占位符，删除不适用的章节

# 3. 为每个核心模块创建上下文文件
cp templates/ai-context-module.md  your-project/src/users/.ai-context.md
```

### 现有项目

1. 阅读 [spec.md](spec.md) 了解规范要求
2. 优先为核心模块补充 `.ai-context.md`
3. 大型项目考虑创建 `.ai-context/` 持久化知识库

### 给 AI Agent 的指令

```
按照 ADD 工程规范开发此项目：
1. 如果 .ai-context/INDEX.md 存在，先阅读恢复全局上下文
2. 每个核心模块有 .ai-context.md
3. 单文件不超过 500 行
4. 使用强类型，避免 any / 隐式类型
5. 先写类型和文档，再写实现
6. 证据不足时明确写出 evidence gap
```

---

_版本：3.0 | 更新日期：2026-03-10_
