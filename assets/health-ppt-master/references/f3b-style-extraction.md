# F3b Style-Gene Extraction (Reverse-Redesign Path)

> Concrete recipe for `workflows/reference-template-generate.md` Path B step 2:
> "Reconstruct a clean template design_spec.md (+ SVG roster + assets)".
> The workflow says WHAT to do; this file says HOW to extract the template's
> identity + structure DNA from the import artifacts so you can write that spec
> without guessing.

## When to use

- F3b (逆向重设计) Path B, after `pptx_template_import.py <uploaded.pptx>` has
  produced `manifest.json` + `summary.md` + `svg/` + `assets/`.
- Also feeds the G2 fit-assessment: the same quick read tells you whether the
  template's visuals are generic (→ F3a viable) or project-specific (→ lean F3b).

## Prefer the import manifest for G2

G2 allows `template_fill_pptx.py analyze` OR `pptx_template_import.py
--manifest-only`. If you are already leaning toward F3b (reverse-redesign),
prefer the **import manifest** — its `summary.md` carries canvas / theme colors /
theme fonts / page-type candidates / layout reuse, which you will reuse in step 2
anyway. One call serves both G2 assessment and F3b spec reconstruction;
`template_fill analyze` would need a second import later.

## Extraction procedure (3 reads)

### Read 1 — `summary.md` (canvas + theme + page-types)

```
read_file <import_dir>/summary.md
```

Capture:
- **Canvas**: size (e.g. 1280×720), format (16:9)
- **Theme colors**: named theme palette (accent1…dk1…lt1) — first approximation
  of the palette; **see pitfall below, slide SVGs override these frequently**
- **Theme fonts**: majorLatin / minorLatin — declared fonts (often overridden)
- **Page-Type Candidates**: which slides are cover / toc / content / ending —
  the template's structural vocabulary
- **Layout Reuse**: which slideLayouts are actually used and by how many slides
  — a layout used by 20+ slides is the workhorse content layout to inherit

### Read 2 — representative slide SVGs (actual colors + fonts + layout DNA)

Pick 3 slides spanning the template's page-types: cover (`slide_01`), toc
(`slide_02`), one content page (`slide_03`). Read each via `read_file`; for a
compact summary, run an `execute_code` regex pass:

```python
import re
content = read_file('<import_dir>/svg/slide_01.svg')['content']
colors = set(re.findall(r'#[0-9A-Fa-f]{6}\b', content))
fonts  = set(re.findall(r'font-family[:=]["\']?([^"\';\s,]+)', content))
sizes  = set(re.findall(r'font-size[:=]["\']?(\d+)', content))
```

What to extract from the three slides:
- **HEX colors**: the recurring deep blue / red / white across all three IS the
  template's palette. Filter out one-off decoration colors.
- **font-family**: actual fonts in use (may differ from theme fonts — real
  session: theme declared Calibri, every slide used 微软雅黑).
- **font-size**: size range, anchors the typography ramp.
- **Structural DNA** (read the SVG elements, not regex): header bar pattern
  (full-width rect at top? color/height?), chapter-numbering style (大写中文
  一二三四? Arabic? circled?), footer (page number position, bottom bar), any
  recurring decorative motif (gradient strips, corner shapes). These are the
  template's "look" that F3b must inherit.

### Read 3 — `ppt_to_md` output (content + visual-type audit)

The markdown conversion (run during Step 1, lands in `sources/` after
import-sources) gives the template's actual text. Skim to confirm:
- Whether baked-in images/diagrams are **project-specific** (放疗靶区勾画, 产品
  截图, 专利证书) or **generic** (logos, decorative shapes). Project-specific
  visuals on many pages = strong F3b signal (F3a would carry wrong-project
  images — the "保真复用 reuse trap").
- The chapter structure the template uses (研究意义→研究内容→工作基础→…) —
  structure DNA, even though F3b will re-map it to the new content's chapters.

## Output: a style-gene summary

Write a 6–10 line summary that becomes the locked identity + structure segments
of the reconstructed `design_spec.md`:

```
Style genes (from <template_filename>):
- Canvas: 1280×720 (16:9)
- Palette: primary #0050AC/#030B81 (deep blue), accent #C00000 (red),
  secondary #4471C4/#9DC3E6/#BDD7EE (blue family), bg #FFFFFF/#F5F5F5,
  body text #0D0D0D/#595959
- Fonts: 微软雅黑 (CJK), Times New Roman (numerals/Latin emphasis)
- Structure DNA: full-width deep-blue header bar (~80px) with white chapter
  number (一二三四五) + section title; bottom deep-blue thin bar + right-aligned
  page number; cover = top red title + mid deep-blue block + bottom info table;
  toc = vertical "目录" + deep-blue horizontal chapter bars
- Visuals: project-specific diagrams dominate → F3b confirmed
```

This feeds directly into `design_spec.md §III` (colors) / `§IV` (fonts) and
`spec_lock.md colors` / `typography` rows, plus Executor's per-page
`page_layouts` / `page_rhythm` decisions.

## Pitfall: theme colors ≠ actual slide colors

`summary.md` lists theme colors (accent1…lt2) but slides frequently override
them with hardcoded HEX. Always cross-check Read 1 against Read 2 — the slide
SVGs are the source of truth for what the template actually looks like.
