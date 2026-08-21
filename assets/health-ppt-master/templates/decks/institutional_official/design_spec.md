---
deck_id: institutional_official
kind: deck
summary: 院内/科室工作汇报 / 等级评审·质控 / 基金标书 / 职称·科技奖 / 药械(NMPA)申报 — 机构蓝+绛红权威型成品级申报评审模板.
canvas_format: ppt169
page_count: 5
primary_color: "#13315C"
---

# Institutional Official (管理·申报) — Design Specification

> Finished, ready-to-use **deck** for formal institutional medical decks: hospital / department work reports, discipline & grade accreditation, quality-control reports, research-grant (NSFC) proposals, title-promotion & award applications, and drug/device (NMPA) filing. Authoritative, dense, structured: institutional blue + crimson accent + a thin gold rule.
>
> **Generic-medical deck**: the brand mark is a drawn cross emblem (placeholder identity). To stamp a real hospital / institute logo, run [`workflows/medical-byo-template.md`](../../workflows/medical-byo-template.md).

---

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | institutional_official (管理·申报) |
| **Use Cases** | 工作汇报、等级评审 / 学科评估、质控汇报、基金标书 / 开题 / 中期 / 结题、职称晋升 / 科技奖、药械 NMPA 申报 |
| **Design Tone** | Authoritative, formal, dense, evidence-and-metrics driven |
| **Theme Mode** | Light theme (white background + institutional-blue header + crimson accents) |
| **Maps playbooks** | `nsfc_grant`, `title_promotion`, `hospital_accreditation`, `drug_device_filing` (see [`references/medical-scenarios.md`](../../references/medical-scenarios.md)) |

### Design Features
1. **Double top rule** — institutional blue band + thin crimson + thin gold; conveys formality / authority.
2. **Seal ring** — a thin ring around the cover emblem suggests an official stamp.
3. **Metrics-dense cards** — kpi / 指标对标 / 进度 sit in tight structured cards.

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
| Primary (institutional blue) | `#13315C` | Header, titles, emblem, rules |
| Chapter background | `#0C2342` | Section dividers, gradient dark end |
| Accent (crimson) | `#B5121B` | Emphasis, active node, seal |
| Gold rule | `#B8902F` | Thin formal rule only |
| Key-message background | `#EEF1F6` | Conclusion / 结论 bar |
| Light surface | `#EAEEF4` | TOC tiles, metric cards |
| Body text | `#1F2733` | Content |
| Muted text | `#5A6675` | Captions, source |
| Light border | `#D3DAE4` | Card borders, dashed placeholders |
| Footer background | `#F3F5F9` | Cover/ending footer |

## IV. Typography

**Font Stack**: `"Microsoft YaHei", "微软雅黑", "PingFang SC", Arial, sans-serif`

| Level | Usage | Size | Weight |
| --- | --- | --- | --- |
| H1 | Cover title | 48px | Bold |
| H2 | Page title | 26px | Bold |
| H3 | Chapter title | 52px | Bold |
| H4 | Card/TOC title | 22px | Bold |
| P | Body | 17px | Regular |
| Sub | Source/notes | 12-14px | Regular |

## V. Page Structure

| Area | Position | Description |
| --- | --- | --- |
| Header | y=0, h=70px | Blue bar + crimson left tab + page title + emblem |
| Conclusion bar | y=70, h=50px | Light blue-gray; 结论 / 核心结论 |
| Content area | y=135, h=515px | Metric cards / 对标表 / 技术路线 / gantt |
| Footer | y=665 | 来源, 章节名, 页码 |

### Decorative DNA
- Double top rule (blue + crimson + gold) on cover/ending.
- Crimson left tab (6px) on header and active cards.
- Seal ring on cover emblem.

## VI. Page Types

1. **Cover** (`01_cover.svg`) — sealed emblem + title/subtitle + crimson/gold divider + 申报人/单位/类别 + date footer.
2. **TOC** (`02_toc.svg`) — numbered cards (立项依据/技术路线/创新点/...) + optional dashed slots.
3. **Chapter** (`02_chapter.svg`) — deep-blue gradient bg, large chapter number, crimson rule, white title/desc.
4. **Content** (`03_content.svg`) — header + conclusion bar + metric-dense content + footer.
5. **Ending** (`04_ending.svg`) — sealed emblem, thank-you, unit/compliance card, footer.

## VII. SVG Page Roster

| File | Role | Description |
| --- | --- | --- |
| `01_cover.svg` | cover | 项目/汇报名 / 申报人 / 单位 / 类别 |
| `02_toc.svg` | toc | 申报/汇报结构 |
| `02_chapter.svg` | chapter | 章节分隔 |
| `03_content.svg` | content | 指标卡 / 对标表 / 技术路线 / gantt |
| `04_ending.svg` | ending | 致谢 / 合规声明 |

## VIII. SVG Technical Constraints

Follows [`references/shared-standards.md`](../../references/shared-standards.md). viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; gradients via `<linearGradient>` in `<defs>`; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*` / `rgba()` / `<g opacity>`; `clipPath` only on `<image>`.

## IX. Placeholder Specification

`{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`

## X. Compliance Reminders (baked into the playbook)

- Metrics must be traceable to the source; 对标评审标准条款.
- Grant 前期数据 must come from the applicant's own work — cite provenance.
- NMPA filing: distinguish 已完成数据 vs 计划数据; cite specific 法规/指导原则; never overstate efficacy or downplay safety.
