# Deck 模板

[English](README.md) | 中文

**Deck = 完整 PPT 仿制品。** 每个 deck 都会逆向分析某个组织的品牌演示文稿，并把其**标识 + 结构 + 中间**部分组合成一项原子资源。当你希望完整保留某个机构的整体风格（色彩、字体、logo、页面结构、表达语气）时，请使用 deck。

现有 deck 的唯一真源是 [`decks_index.json`](./decks_index.json)（`deck_id → { summary, canvas_format, page_count, primary_color }`）。本 README 解释该类型，**不会**枚举 deck。

完整数据模型见 [`docs/zh/templates-architecture.md`](../../docs/zh/templates-architecture.md)。

---

## 触发规则

Deck 选择通过**显式路径主动启用**。主工作流默认自由设计。只有用户在首条消息中提供明确目录路径（例如 `skills/ppt-master/templates/decks/招商银行/`）时才会使用 deck。只有名称不会触发。见 [`SKILL.md`](../../SKILL.md) 第 3 步。

`decks_index.json` 是**发现辅助工具**，而不是触发器；AI 可以用它列出 id 和路径来回答「有哪些 deck？」。只进行列举绝不会推进流水线。

---

## design_spec.md schema

Deck 包含完整的部分集合（标识 + 结构 + 中间）。最低 schema：

```markdown
---
deck_id: <slug>
kind: deck
summary: <one-line use cases>
canvas_format: ppt169
page_count: 5
primary_color: "#XXXXXX"
---

# [Brand / Organization Name] - Design Specification

## I. Template Overview          # Middle — Use cases / Design intent
## II. Canvas Specification      # Structure
## III. Color Scheme             # Identity — role / HEX / provenance / notes
## IV. Typography                # Identity — role / family / weight
## V. Logo                       # Identity — file / form / usage rules (if logo bundled)
## VI. Page Structure            # Structure — layout grid / decorative DNA
## VII. Page Types               # Structure — per-page roles
## VIII. SVG Page Roster         # Structure — file list + per-file purpose
```

Deck 可以包含其他辅助章节（Voice & Tone、Icon Style、Layout Modes、Spacing Specification、SVG Technical Constraints、Placeholder Specification、Asset Specification、Usage Notes）。当这些内容对仿制品有意义时再使用。

---

## 第 3 步的融合行为

用户**只**提供 deck 路径时，Strategist 会锁定所有部分；Eight Confirmations 会收窄到 deck 内容字段（目标受众／页数／大纲／语气微调）。

用户提供 deck 路径的**同时**还提供品牌路径或布局路径时，标识／结构部分会由更高优先级的来源覆盖（品牌决定标识，布局决定结构）。见 [`SKILL.md`](../../SKILL.md) 第 3 步的融合表。

---

## 创建新 deck

1. 运行 [`workflows/create-template.md`](../../workflows/create-template.md)（默认类型为 `deck`）
2. 生成的目录位于 `templates/decks/<id>/`
3. 校验：`python3 skills/ppt-master/scripts/svg_quality_checker.py templates/decks/<id> --template-mode --format ppt169`
4. 注册：`python3 skills/ppt-master/scripts/register_template.py <id> --kind deck`

注册步骤会更新 [`decks_index.json`](./decks_index.json)，即 deck 发现的唯一真源。

---

## 另请参阅

- [`templates/layouts/`](../layouts/)：不含标识、仅定义结构的模板
- [`templates/brands/`](../brands/)：不含页面清单、仅定义标识的预设
- [`docs/zh/templates-architecture.md`](../../docs/zh/templates-architecture.md)：三类数据模型与融合规则
