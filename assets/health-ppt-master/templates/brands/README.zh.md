# 品牌标识预设

[English](README.md) | 中文

本目录包含**仅定义品牌的模板**：由色彩、字体、logo、表达语气和图标风格组成的标识包，不含 SVG 页面清单。Strategist 把品牌的标识部分锁定为真源，Executor 则在这些约束下自由设计页面。

品牌是模板库三种模板之一，另外两种是仅定义结构的 [`layouts/`](../layouts/) 和完整 PPT 仿制品 [`decks/`](../decks/)。完整数据模型见 [`docs/zh/templates-architecture.md`](../../docs/zh/templates-architecture.md)。

## 品牌的使用方式

品牌应用在 SKILL.md 第 3 步遵循与所有模板类型**相同的显式路径规则**，并写入**同一个项目目录**（`<project_path>/templates/`）：

| 用户在 SKILL.md 第 3 步提供的输入 | 行为 |
|---|---|
| 明确的品牌目录路径（例如 `templates/brands/anthropic/`） | 把 `design_spec.md`、logo 文件和资源子目录复制到 `<project_path>/templates/`；Strategist 锁定标识部分 |
| 只有品牌名称（"use anthropic brand"）、提及品牌但没有路径，或没有输入 | 跳过；机械规则与所有模板类型相同：只有名称绝不会触发 |
| 品牌路径 + 布局路径 | 融合成一份 `design_spec.md`：品牌决定标识部分（色彩／字体／logo／语气／图标风格），布局决定结构部分（画布／页面清单）。见 `SKILL.md` 第 3 步。 |
| 品牌路径 + deck 路径 | 融合：品牌标识覆盖 deck 标识；结构与中间部分来自 deck |
| 品牌路径 + 布局路径 + deck 路径 | 三方融合：brand=identity，layout=structure，deck=middle |
| 两个品牌路径 | 融合前先提示解决冲突，由用户逐部分选择来源 |

`brands_index.json` 只用于发现；列出品牌不会推进流水线。

## 创建新品牌

运行独立工作流：

```
Read skills/ppt-master/workflows/create-brand.md
```

支持三种输入路径：品牌资源（logo／品牌网站 URL／品牌 PPTX／品牌 PDF）、用户在对话中口述的规范，或供用户稍后填写的空骨架。

## 包结构

每个品牌目录都自包含：

```
templates/brands/<brand_id>/
├── design_spec.md            # required — brand identity spec (7 sections)
├── logo.<ext>                # optional — primary brand logo (single-lockup brands)
│   …or…
├── <brand>_wordmark.<ext>    # optional — wordmark variant (dual-lockup brands)
├── <brand>_mark.<ext>        # optional — symbol / icon variant (dual-lockup brands)
├── images/                   # optional — branded photos
├── illustrations/            # optional — branded illustrations
└── icons/                    # optional — branded icon overrides
```

Logo 文件名用于描述而非形成约定；`design_spec.md` §IV 会列出确切文件及各自的使用场景。单组合标志品牌通常提供一个 `logo.<ext>`；双组合标志品牌（例如 Google 的文字标志 + G 标记）会提供分别命名的文件。

`design_spec.md` 包含具有 `kind: brand` 的 YAML frontmatter，是品牌标识的唯一真源。六个必需章节分别是：I Brand Overview／II Color Scheme／III Typography／IV Logo／V Voice & Tone／VI Icon Style。

## 发现索引

[brands_index.json](./brands_index.json) 是一份精简的机器可读映射（`brand_id → { summary, primary_color }`）。创建或编辑品牌后，`register_template.py --kind brand <brand_id>` 会刷新该文件。

列出索引不会触发任何流水线动作；无论品牌是否出现在索引中，第 3 步都只在用户提供明确目录路径时触发。
