---
deck_id: research_academic
kind: deck
summary: 学术大会发言 / SCI 成果汇报 / 文献汇报 Journal Club — 藏青+teal 数据前置成品级科研模板.
canvas_format: ppt169
page_count: 5
primary_color: "#1A3A5C"
---

# Research Academic (科研学术) — Design Specification

> Finished, ready-to-use **deck** for medical research talks: academic-conference oral presentations, SCI / research-result reporting, and journal club. Clean, data-forward, restrained — the figure does the talking (KM / forest / ROC / CONSORT); **for journal club that figure is the paper's own original image, not a redraw**. Navy + teal, a pulse mark, and data-node decoration.
>
> **Generic-medical deck**: the brand mark is a drawn pulse emblem (placeholder identity). To stamp a real institution logo, run [`workflows/medical-byo-template.md`](../../workflows/medical-byo-template.md).

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | research_academic (科研学术) |
| **Use Cases** | 学术年会发言 / oral report、SCI 成果汇报、研究进展、文献汇报 / Journal Club |
| **Design Tone** | Clean, rigorous, evidence-driven, data-forward, calm |
| **Theme Mode** | Light theme (white background + navy header + teal accents) |
| **Maps playbooks** | `academic_conference`, `journal_club` (see [`references/medical-scenarios.md`](../../references/medical-scenarios.md)) |

### Design Features
1. **Data-node motif** — teal circles + connectors suggest data points; used sparingly on cover/chapter/toc.
2. **One-figure-one-message** content page — a generous canvas hosts a single primary figure (the paper's original when journal club) + a take-home bar.
3. **Restraint** — thin navy rules, no heavy color blocks; whitespace lets charts breathe.

---

## II. Canvas Specification

| Property | Value |
| --- | --- |
| **Format** | Standard 16:9 |
| **Dimensions** | 1280 × 720 px |
| **viewBox** | `0 0 1280 720` |
| **Page Margins** | Left/right 40px, bottom 35px |
| **Content Safe Area** | x: 40-1240, y: 135-650 |

## III. Color Scheme

| Role | HEX | Usage |
| --- | --- | --- |
| Primary (navy) | `#1A3A5C` | Header, titles, rules |
| Chapter background | `#11293F` | Section dividers, gradient dark end |
| Accent (teal) | `#0E8C8C` | Left bars, data nodes, emblem |
| Key-message background | `#E3F1F1` | Take-home bar |
| Light surface | `#EAF1F4` | TOC tiles |
| Body text | `#1F2937` | Content |
| Muted text | `#5A6B7B` | Captions, source |
| Light border | `#DCE3EA` | Card borders, dashed placeholders |
| Footer background | `#F4F7F9` | Cover/ending footer |

## IV. Typography

**Font Stack**: `"Microsoft YaHei", "微软雅黑", "PingFang SC", Arial, sans-serif`

| Level | Usage | Size | Weight |
| --- | --- | --- | --- |
| H1 | Cover title | 50px | Bold |
| H2 | Page title | 26px | Bold |
| H3 | Chapter title | 52px | Bold |
| H4 | Card/TOC title | 22px | Bold |
| P | Body | 17px | Regular |
| Sub | Source/notes | 12-14px | Regular |

## V. Page Structure

| Area | Position | Description |
| --- | --- | --- |
| Header | y=0, h=70px | Navy bar + teal left bar + page title + emblem |
| Key-message bar | y=70, h=50px | Light teal; page take-home / core finding |
| Content area | y=135, h=515px | One primary figure + supporting text. **journal_club `Extracted` 原图按其原生比例居中于此区、不拉伸填满整槽**（`meet` no-crop）；正文 / caption 环绕图的实际占位重排，避免大片空白信箱边。 |
| Footer | y=665 | 来源/引用, 章节名, 页码 |

### Decorative DNA
- Teal data-node dots + thin connectors on cover/chapter/toc.
- Teal left vertical bar (6px) on header and cards.
- Thin navy rules as dividers — restrained.

## VI. Page Types

1. **Cover** (`01_cover.svg`) — emblem + title/subtitle + node divider + 作者/单位/会议 + date footer.
2. **TOC** (`02_toc.svg`) — Background/Methods/Results/... cards + optional dashed slots.
3. **Chapter** (`02_chapter.svg`) — deep-navy gradient bg, large chapter number, teal rule, white title/desc.
4. **Content** (`03_content.svg`) — header + teal key-message bar + single-figure content + footer.
5. **Ending** (`04_ending.svg`) — large emblem, thank-you, acknowledgement/disclosure card, footer.

## VII. SVG Page Roster

| File | Role | Description |
| --- | --- | --- |
| `01_cover.svg` | cover | 题目 / 作者与单位 / 会议名 |
| `02_toc.svg` | toc | 主要章节 (IMRaD) |
| `02_chapter.svg` | chapter | 章节分隔 |
| `03_content.svg` | content | 单图 + take-home |
| `04_ending.svg` | ending | 致谢 / 利益冲突声明 |

## VIII. SVG Technical Constraints

Follows [`references/shared-standards.md`](../../references/shared-standards.md). viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; gradients via `<linearGradient>` in `<defs>`; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*` / `rgba()` / `<g opacity>`; `clipPath` only on `<image>`.

## IX. Placeholder Specification

`{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`

## X. Research Reminders (baked into the playbook)

- One slide, one message; put the take-home in the key-message bar / title.
- Results pages host the paper's **own figures** — for **journal club**, embed the *original extracted* figure image (`Extracted` status, document-parser `<stem>_files/*.png`, `no-crop`, **sized to the figure's native ratio — not stretched to fill the slot**), **never a redrawn chart or a 示意图 substitute**. Confirm each extracted figure is the *complete* figure (not a legend/axis fragment) before embedding. Only reconstruct a chart when no clean original is obtainable, using the paper's exact reported values, and label it a reconstruction. Never fabricate p-values, CIs or citations.
- Always include a limitations slide and a disclosure / 利益冲突 line.
