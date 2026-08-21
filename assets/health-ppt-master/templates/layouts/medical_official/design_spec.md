---
layout_id: medical_official
kind: layout
summary: Formal medical institutional decks — research grant / NSFC proposals, title-promotion & award applications, discipline/grade accreditation, hospital work reports, drug/device (NMPA) filing.
canvas_format: ppt169
page_count: 5
page_types: [cover, toc, chapter, content, ending]
---

# Medical Official Template (Institutional Blue / Crimson, Formal) - Design Specification

> Suitable for research grant / NSFC proposals, title-promotion and science-award applications, discipline / grade accreditation, hospital work reports, and drug / device (NMPA) regulatory filing — anywhere an authoritative, dense, evidence-backed institutional tone is required.

---

## I. Template Overview

| Property          | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| **Template Name** | medical_official (Formal Medical / Institutional)                    |
| **Use Cases**     | Grant / NSFC proposals, title-promotion & award applications, accreditation, work reports, NMPA filing |
| **Design Tone**   | Authoritative, formal, rigorous, dense, accountable                  |
| **Theme Mode**    | Light theme (white background + deep institutional blue header + crimson accents) |

---

## II. Canvas Specification

| Property              | Value                       |
| --------------------- | --------------------------- |
| **Format**            | Standard 16:9               |
| **Dimensions**        | 1280 × 720 px               |
| **viewBox**           | `0 0 1280 720`              |
| **Page Margins**      | Left/right 40px, top 0px, bottom 35px |
| **Content Safe Area** | x: 40-1240, y: 70-665       |

---

## III. Page Structure

### General Layout

| Area                | Position/Height | Description                                   |
| ------------------- | --------------- | --------------------------------------------- |
| **Header**          | y=0, h=78px     | Deep-blue band + crimson left bar + double bottom rule + page title |
| **Key Message Bar** | y=78, h=46px    | Conclusion / key claim (light blue-gray background) |
| **Content Area**    | y=135, h=515px  | Main content (dense, structured)              |
| **Footer**          | y=665, h=55px   | Source, section name, page number             |

### Decorative DNA

- **Crimson left vertical bar** (`#B5121B`, 6px): header / emphasis card accent — used sparingly for gravitas
- **Double rule under header** (deep blue + crimson hairline): signals formal/official tone
- **Deep-blue chapter background** (`#0C2342`) with crimson accent rule
- Restrained palette, high text density tolerance — built for proposal / report content

---

## IV. Page Types

### 1. Cover Page (01_cover.svg)
- White background; deep-blue top band + crimson left bar + double rule
- Top-right institution/logo placeholder
- Centered deep-blue main title + subtitle
- Applicant / category / institution block
- Bottom band with date

### 2. Table of Contents (02_toc.svg)
- Standard deep-blue header
- Two-column numbered card list; blue/crimson left bars; optional dashed items

### 3. Chapter Page (02_chapter.svg)
- Deep-blue full-screen background (`#0C2342`)
- Large semi-transparent chapter number
- Crimson accent rule + white chapter title + light description

### 4. Content Page (03_content.svg)
- White background; standard deep-blue header + double rule
- Light blue-gray key-message bar (the page's claim)
- Dense flexible content area (cards, tables, roadmap, gantt)
- Footer: source, section name, page number

### 5. Ending Page (04_ending.svg)
- White background; deep-blue band
- Centered closing line
- Institution / contact / compliance block
- Footer with page number

---

## V. SVG Page Roster

| File | Role | Description |
|------|------|-------------|
| `01_cover.svg` | cover | Title slide; project/applicant, category, institution, date |
| `02_chapter.svg` | chapter | Section divider (large number + section title) |
| `02_toc.svg` | toc | Outline of major sections |
| `03_content.svg` | content | Main content page; dense structured body |
| `04_ending.svg` | ending | Closing / compliance / contact |

## VI. Layout Patterns (Recommended)

| Pattern | Applicable | Notes |
|---|---|---|
| Technical roadmap / flow | Grant technical route, study flow | Single full-width figure — proposal centerpiece |
| KPI cards | Work-report metrics, endpoints | Quantified achievements |
| Comparison table | Benchmark vs target, vs prior product | Dense, accountable |
| Gantt / roadmap | Project schedule, next-step plan | Sequential |
| Numbered claim list | Innovation points, aims | One claim per row |

---

## VII. Color Scheme

| Role | HEX | Usage |
|---|---|---|
| Primary (institutional blue) | `#13315C` | Header, titles |
| Chapter background | `#0C2342` | Section dividers |
| Accent (crimson) | `#B5121B` | Left bars, emphasis, claim markers |
| Key-message background | `#EEF1F6` | Claim bar |
| Body text | `#1F2933` | Content |
| Muted text | `#5B6775` | Captions, source |
| Light border | `#D5DCE6` | Card borders, dashed placeholders |
| Footer background | `#F2F4F8` | Cover/ending footer |

## VIII. SVG Technical Constraints

Follows `references/shared-standards.md`. viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*`; `clipPath` only on `<image>` per shared-standards §1.2.

## IX. Placeholder Specification

Canonical placeholders: `{{LOGO}}` `{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{ADVISOR}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`.
