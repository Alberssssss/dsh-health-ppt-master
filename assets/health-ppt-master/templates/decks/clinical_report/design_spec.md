---
deck_id: clinical_report
kind: deck
summary: 临床病例汇报 / 疑难病例讨论 / MDT / 教学查房 — 医蓝+生命绿成品级医院汇报模板.
canvas_format: ppt169
page_count: 5
primary_color: "#0066B3"
---

# Clinical Report (临床汇报) — Design Specification

> Finished, ready-to-use **deck** for clinical case reports, difficult-case / MDT discussions and teaching rounds. Warm, trustworthy clinical look: medical blue + life green, a heartbeat motif, and rounded data cards. Doctors pick this deck and fill content — no design decisions needed.
>
> **Generic-medical deck**: the brand mark is a drawn cross emblem (a placeholder identity, not a specific hospital's). To stamp a real hospital/department logo, run [`workflows/medical-byo-template.md`](../../workflows/medical-byo-template.md) and reverse-engineer the deck/brand from the institution's own template.

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | clinical_report (临床汇报) |
| **Use Cases** | 病例汇报、疑难病例讨论、MDT、晨会病例、住培病例汇报、教学查房 |
| **Design Tone** | Clinical, trustworthy, warm-professional, data-card driven |
| **Theme Mode** | Light theme (white background + medical-blue header + life-green accents) |
| **Maps playbooks** | `clinical_case`, `teaching_rounds` (see [`references/medical-scenarios.md`](../../references/medical-scenarios.md)) |

### Design Features
1. **Heartbeat motif** — an ECG/pulse line used on cover/ending as the signature clinical mark.
2. **Rounded data cards** — vital signs / lab values / differential comparison sit in soft cards.
3. **Critical-red accent** (`#FF6B35`) — reserved for 危急值 / red-flag emphasis only.

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
| Primary (medical blue) | `#0066B3` | Header, titles, emblem, rules |
| Deep blue | `#004C87` | Chapter background, gradient dark end |
| Accent (life green) | `#00A86B` | Left tabs, dividers, key-message bar |
| Critical accent | `#FF6B35` | 危急值 / red-flag only |
| Light blue surface | `#EAF3FB` | Cards, toc tiles |
| Key-message background | `#E6F6EF` | Take-home / page核心 bar |
| Body text | `#1F2A37` | Content |
| Muted text | `#5A6B7B` | Captions, source |
| Light border | `#D5E2EE` | Card borders, dashed placeholders |
| Footer background | `#F4F8FC` | Cover/ending footer |

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
| Header | y=0, h=70px | Medical-blue bar + green left tab + page title + emblem |
| Key-message bar | y=70, h=50px | Light-green; page take-home (诊断要点/转归) |
| Content area | y=135, h=515px | Cards / timeline / image-text |
| Footer | y=665 | 来源, 章节名, 页码 |

### Decorative DNA
- Heartbeat polyline (`#00A86B`) on cover + ending.
- Green left tab (6px) on header and cards.
- Soft diagonal corner blocks (blue/green, low opacity) on cover.

## VI. Page Types

1. **Cover** (`01_cover.svg`) — emblem + title/subtitle + heartbeat divider + 汇报人/科室/医院 + date footer.
2. **TOC** (`02_toc.svg`) — 2×2 numbered cards + optional dashed slots.
3. **Chapter** (`02_chapter.svg`) — deep-blue gradient bg, large chapter number, green rule, white title/desc.
4. **Content** (`03_content.svg`) — header + green key-message bar + flexible content + footer.
5. **Ending** (`04_ending.svg`) — large emblem, thank-you, institution card, de-identification reminder footer.

## VII. SVG Page Roster

| File | Role | Description |
| --- | --- | --- |
| `01_cover.svg` | cover | 病例标题 / 汇报人 / 科室 / 日期 |
| `02_toc.svg` | toc | 汇报结构(病史→查体→辅检→诊断→诊疗→转归→讨论) |
| `02_chapter.svg` | chapter | 章节分隔 |
| `03_content.svg` | content | 正文：数据卡 / timeline / 图随报告 |
| `04_ending.svg` | ending | 小结 / 致谢 |

## VIII. SVG Technical Constraints

Follows [`references/shared-standards.md`](../../references/shared-standards.md). viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; gradients via `<linearGradient>` in `<defs>`; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*` / `rgba()` / `<g opacity>`; `clipPath` only on `<image>`.

## IX. Placeholder Specification

`{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`

## X. Clinical Reminders (baked into the playbook)

- **去标识化** — no patient name / 住院号 / 正脸. Use age-sex + diagnosis.
- **危急值** uses the critical accent (`#FF6B35`), nothing else does.
- Never fabricate doses, lab values or outcomes — empty slots stay `待补充`.
