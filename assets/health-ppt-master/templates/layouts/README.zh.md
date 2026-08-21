# 布局模板

[English](README.md) | 中文

**Layout = 仅定义结构的模板。** 它记录画布、页面结构、页面类型和 SVG 清单，但**不含标识部分**（色彩／字体／logo／表达语气／图标风格）。分层标识来自 `templates/brands/`，或由 Strategist 在每个 deck 的 Eight Confirmations 中决定。特定 PPT 的完整标识仿制品请改用 [`templates/decks/`](../decks/)。

现有布局的唯一真源是 [`layouts_index.json`](./layouts_index.json)（`layout_id → { summary, canvas_format, page_count, page_types }`）。本 README 解释该类型，**不会**枚举布局。

完整数据模型见 [`docs/zh/templates-architecture.md`](../../docs/zh/templates-architecture.md)。

---

## 触发规则

布局选择通过**显式路径主动启用**。主工作流默认自由设计。只有用户在首条消息中提供明确目录路径（例如 `skills/ppt-master/templates/layouts/academic_defense/`）时才会使用布局。只有名称不会触发。见 [`SKILL.md`](../../SKILL.md) 第 3 步。

`layouts_index.json` 是**发现辅助工具**，而不是触发器；AI 可以用它列出 id 和路径来回答「有哪些布局？」。只进行列举绝不会推进流水线。

---

## design_spec.md schema

布局只写入**仅结构部分**。不得包含标识章节（Color Scheme／Typography／Logo／Voice／Icon Style），这些内容属于品牌和 deck。最低 schema：

```markdown
---
layout_id: <slug>
kind: layout
summary: <one-line use cases>
canvas_format: ppt169
page_count: 5
page_types: [cover, toc, chapter, content, ending]
---

# [Template Name] - Design Specification

## I. Template Overview         # Use cases / Design intent
## II. Canvas Specification     # Format / Dimensions / viewBox / Margins
## III. Page Structure          # Layout grid / Decorative DNA / Navigation
## IV. Page Types               # Per-page role descriptions
## V. SVG Page Roster           # File list + per-file purpose
```

布局可以包含其他辅助章节（Layout Patterns、Spacing Guidelines、SVG Technical Constraints、Placeholder Specification、Usage Notes）。**不要**包含 Color Scheme 或 Typography 章节；这些标识部分字段由 `templates/brands/` 和 `templates/decks/` 所有。

---

## 每个布局目录的标准文件集

| 文件名 | 必需 | 用途 |
|----------|----------|---------|
| `design_spec.md` | 是 | 布局 schema 规范（frontmatter + 结构章节） |
| `01_cover.svg` | 是 | 封面页 |
| `02_toc.svg` | 可选 | 目录页 |
| `02_chapter.svg` | 是 | 章节页 |
| `03_content.svg` | 是 | 内容页 |
| `04_ending.svg` | 是 | 结束页 |

所有 SVG 对 ppt169 均使用 `viewBox="0 0 1280 720"`。

---

## 占位符约定

模板使用 `{{PLACEHOLDER}}` 标记可替换内容。新布局应使用 [`references/template-designer.md`](../../references/template-designer.md#4-placeholder-reference-canonical-convention-overridable-per-template) 中记录的规范占位符集合。刻意使用不同词汇的模板需要在 `design_spec.md` frontmatter 中声明 `placeholders:` 块，以消除提示性警告。

---

## 创建新布局

1. 运行 [`workflows/create-template.md`](../../workflows/create-template.md)（默认生成 deck；明确选择「仅结构／无标识」时生成布局）
2. 生成的目录位于 `templates/layouts/<id>/`
3. 校验：`python3 skills/ppt-master/scripts/svg_quality_checker.py templates/layouts/<id> --template-mode --format ppt169`
4. 注册：`python3 skills/ppt-master/scripts/register_template.py <id> --kind layout`

注册步骤会更新 [`layouts_index.json`](./layouts_index.json)，即布局发现的唯一真源。

---

## SVG 技术约束

权威禁用项清单（PPT 不兼容项、原始字符规则、clipPath 条件性允许规则等）见 [`shared-standards.md`](../../references/shared-standards.md)。布局必须遵守这些规则。
