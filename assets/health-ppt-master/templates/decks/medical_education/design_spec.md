---
deck_id: medical_education
kind: deck
summary: 继续医学教育 CME / 进修培训课件 / 专业科普讲座 — 教学绿+琥珀友好型成品级教培模板.
canvas_format: ppt169
page_count: 5
primary_color: "#1F8A5B"
---

# Medical Education (教学培训) — Design Specification

> Finished, ready-to-use **deck** for continuing medical education (CME), fellowship / staff training, and professional health-science lectures. Friendly, clearly structured, section-driven: teaching green + amber, rounded step cards, learning-objective bars. Built to teach, not to impress.
>
> **Generic-medical deck**: the brand mark is a drawn cross emblem (placeholder identity). To stamp a real institution logo, run [`workflows/medical-byo-template.md`](../../workflows/medical-byo-template.md).

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | medical_education (教学培训) |
| **Use Cases** | 继续医学教育 (CME)、进修 / 规培培训课件、专业讲座、深度医学科普 |
| **Design Tone** | Friendly, clear, structured, teaching-oriented, approachable |
| **Theme Mode** | Light theme (white background + teaching-green header + amber accents) |
| **Maps playbooks** | `cme_course` (see [`references/medical-scenarios.md`](../../references/medical-scenarios.md)) |

### Design Features
1. **Learning-objective bar** — the key-message bar carries 学习目标 / 本节要点 in light amber.
2. **Rounded step cards** — numbered sections read as a learning path; amber underline marks the active node.
3. **Approachable green** — calmer than clinical blue; suited to teaching and lay-professional audiences.

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
| Primary (teaching green) | `#1F8A5B` | Header, titles, emblem, rules |
| Deep green | `#15633F` | Chapter background, gradient dark end |
| Accent (amber) | `#E8A33D` | Active node, underlines, objective bar |
| Light green surface | `#EAF5EF` | TOC tiles, cards |
| Key-message background | `#FBF1DD` | Learning-objective / 要点 bar |
| Body text | `#1E2A24` | Content |
| Muted text | `#5B6B62` | Captions, source |
| Light border | `#D6E5DC` | Card borders, dashed placeholders |
| Footer background | `#F3F8F5` | Cover/ending footer |

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
| Header | y=0, h=70px | Green bar + amber left tab + page title + emblem |
| Objective bar | y=70, h=50px | Light amber; 学习目标 / 本节要点 |
| Content area | y=135, h=515px | Section teaching: 要点 → 图示 → 案例 → 小结 |
| Footer | y=665 | 来源, 章节名, 页码 |

### Decorative DNA
- Amber underline accents + amber step dots.
- Green left tab (6px) on header and cards.
- Soft green diagonal corner block on cover.

## VI. Page Types

1. **Cover** (`01_cover.svg`) — emblem + course title/subtitle + amber divider + 讲者/学分信息 + date footer.
2. **TOC** (`02_toc.svg`) — numbered learning-step cards + optional dashed slots.
3. **Chapter** (`02_chapter.svg`) — deep-green gradient bg, large chapter number, amber rule, white title/desc.
4. **Content** (`03_content.svg`) — header + amber objective bar + teaching content + footer.
5. **Ending** (`04_ending.svg`) — large emblem, thank-you, 小结/自测 reminder card, footer.

## VII. SVG Page Roster

| File | Role | Description |
| --- | --- | --- |
| `01_cover.svg` | cover | 课程名 / 讲者 / 学分信息 |
| `02_toc.svg` | toc | 课程大纲（学习路径） |
| `02_chapter.svg` | chapter | 章节分隔 |
| `03_content.svg` | content | 分节讲授：要点/图示/案例/小结 |
| `04_ending.svg` | ending | 总结 / 自测 / 致谢 |

## VIII. SVG Technical Constraints

Follows [`references/shared-standards.md`](../../references/shared-standards.md). viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; gradients via `<linearGradient>` in `<defs>`; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*` / `rgba()` / `<g opacity>`; `clipPath` only on `<image>`.

## IX. Placeholder Specification

`{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`

## X. Teaching Reminders (baked into the playbook)

- Every section ends with a 小结; add an interaction / 思考题 page.
- Distinguish professional CME depth from lay science-communication depth.
- Cite guideline grades from the source only — never invent recommendation levels.
