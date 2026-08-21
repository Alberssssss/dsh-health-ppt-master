---
layout_id: medical_research
kind: layout
summary: Medical research presentations — academic conference talks, journal club, SCI result reporting, IMRaD structure decks.
canvas_format: ppt169
page_count: 5
page_types: [cover, toc, chapter, content, ending]
---

# Medical Research Template (Navy / Teal, Data-Forward) - Design Specification

> Suitable for academic conference oral talks, journal club / literature review, SCI / research result reporting, and other IMRaD-structured medical research decks. Clean, data-forward, restrained — the figure does the talking.

---

## I. Template Overview

| Property          | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| **Template Name** | medical_research (Medical Research / Academic)                       |
| **Use Cases**     | Academic conference talks, journal club, SCI result reporting, research progress |
| **Design Tone**   | Clean, rigorous, evidence-driven, data-forward, calm                 |
| **Theme Mode**    | Light theme (white background + navy header + teal accents)          |

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
| **Header**          | y=0, h=70px     | Navy background + teal left vertical bar + page title |
| **Key Message Bar** | y=70, h=50px    | Take-home / core finding (light teal background) |
| **Content Area**    | y=135, h=515px  | Main content / figures                        |
| **Footer**          | y=665, h=55px   | Source / citation, section name, page number  |

### Decorative DNA

- **Teal left vertical bar** (`#0E8C8C`, 6px): header and card accent
- **Thin navy rules** (`#1A3A5C`, 1.5px): section dividers — restrained, no heavy blocks
- **Data-node dots** (`#0E8C8C` circles, r=4-6): suggest data points; used sparingly on cover/chapter
- Generous whitespace; the deck is built to host charts (KM / forest / ROC / CONSORT)

---

## IV. Page Types

### 1. Cover Page (01_cover.svg)
- White background; thin navy top rule + teal node accent
- Centered navy main title + muted subtitle
- Teal divider with data-node dots
- Author / affiliation / conference info block
- Bottom thin footer with date

### 2. Table of Contents (02_toc.svg)
- Standard navy header
- Two-column numbered card list; teal/navy left bars; optional dashed items

### 3. Chapter Page (02_chapter.svg)
- Deep navy full-screen background (`#11293F`)
- Large semi-transparent chapter number
- Teal accent rule + white chapter title + light description
- Minimal geometric data-node motif at right

### 4. Content Page (03_content.svg)
- White background; standard navy header
- Light-teal key-message bar (take-home of the page)
- Flexible content area sized to host one primary figure + supporting text
- Footer: source/citation, section name, page number

### 5. Ending Page (04_ending.svg)
- White background; navy top rule
- Centered thank-you + take-home line
- Affiliation / acknowledgement / disclosure block
- Footer with page number

---

## V. SVG Page Roster

| File | Role | Description |
|------|------|-------------|
| `01_cover.svg` | cover | Title slide; study title, authors, affiliation, conference |
| `02_chapter.svg` | chapter | Section divider (large number + section title) |
| `02_toc.svg` | toc | Outline of major sections (Background/Methods/Results/...) |
| `03_content.svg` | content | Main content page; figure + take-home |
| `04_ending.svg` | ending | Closing / acknowledgement / disclosure |

## VI. Layout Patterns (Recommended)

| Pattern | Applicable | Notes |
|---|---|---|
| Single figure + take-home | Results pages | Chart dominant, one-line conclusion in key-message bar |
| Two-column comparison | Methods, this-study-vs-prior | Symmetric, easy contrast |
| Timeline / flow | Study design, enrollment (CONSORT) | Sequential |
| Data cards | Baseline characteristics, endpoints | Multiple metrics |

---

## VII. Color Scheme

| Role | HEX | Usage |
|---|---|---|
| Primary (navy) | `#1A3A5C` | Header, titles, rules |
| Chapter background | `#11293F` | Section dividers |
| Accent (teal) | `#0E8C8C` | Left bars, data nodes, emphasis |
| Key-message background | `#E3F1F1` | Take-home bar |
| Body text | `#1F2937` | Content |
| Muted text | `#5A6B7B` | Captions, source |
| Light border | `#DCE3EA` | Card borders, dashed placeholders |
| Footer background | `#F4F7F9` | Cover/ending footer |

## VIII. SVG Technical Constraints

Follows `references/shared-standards.md`. viewBox fixed `0 0 1280 720`; inline styles only; HEX colors; `fill-opacity`/`stroke-opacity` for transparency; no `mask` / `<style>` / `class` / `foreignObject` / `textPath` / `animate*`; `clipPath` only on `<image>` per shared-standards §1.2.

## IX. Placeholder Specification

Canonical placeholders: `{{LOGO}}` `{{TITLE}}` `{{SUBTITLE}}` `{{AUTHOR}}` `{{DEPARTMENT}}` `{{ADVISOR}}` `{{INSTITUTION}}` `{{DATE}}` `{{SECTION_NUM}}` `{{PAGE_TITLE}}` `{{KEY_MESSAGE}}` `{{CONTENT_AREA}}` `{{SOURCE}}` `{{SECTION_NAME}}` `{{PAGE_NUM}}` `{{CHAPTER_NUM}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_DESC}}` `{{TOC_ITEM_N_TITLE}}` `{{TOC_ITEM_N_DESC}}` `{{THANK_YOU}}` `{{ENDING_SUBTITLE}}` `{{CONTACT_INFO}}`.
