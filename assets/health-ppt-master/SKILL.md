---
name: health-ppt-master
description: >
  Medical & hospital presentation generator for doctors and clinical/research staff.
  Forks ppt-master's document→native-editable-PPTX pipeline and injects medical scenario
  playbooks (clinical case report, research grant / NSFC proposal, academic conference talk,
  journal club, teaching rounds, title-promotion & accreditation, drug/device filing),
  hospital-styled layout templates, and clinical-research charts (Kaplan–Meier survival,
  forest plot, CONSORT, ROC). Use for medical decks — "把病例做成汇报PPT", "做个基金标书的汇报幻灯",
  "文献汇报PPT", "学术大会发言PPT", "医学科普PPT", "做PPT", "制作演示文稿", "create medical presentation",
  "grant proposal slides", "journal club deck". Non-medical decks are handled in-skill via the
  Strategist §0 free-design fallback — no need to switch skills.
registry:
  homepage: https://github.com/hugohe3/ppt-master
  author: Hugo He (upstream, MIT); medical fork by health-hermes-agent
  license: MIT
  upstream_version: 2.7.0
  fork_of: ppt-master (upstream, MIT) — medical scenario injection; core pipeline unchanged. Now the sole PPT skill (the vendored generic ppt-master was removed; non-medical decks fall back to free design in-skill).
---

# Health PPT Master Skill（医生 / 医院端医疗演示生成）

> Medical fork of ppt-master. Same document→SVG→native-editable-PPTX pipeline, with medical
> scenario playbooks, hospital-styled layouts, and clinical-research charts injected at the
> template / Strategist / charts layers. The execution pipeline below is unchanged from upstream.

> [!IMPORTANT]
> ## DSH pilot runtime note
>
> The directory reported in `<skill_resources>` is `<skill-dir>` in every command below; substitute its exact absolute path before execution. `<document-parser-dir>` names an external deployment resource and is not part of this package.
>
> Before entering the pipeline, run `python3 -B <skill-dir>/scripts/dsh_preflight.py --require core --workspace <workspace>`. The core group covers the local SVG-to-editable-PPTX path. If it is missing and the active DSH permission policy allows dependency installation, create a virtual environment under `<workspace>/.health-ppt-master/venv`, install `<skill-dir>/requirements-core.txt` into it, rerun the check with that environment's Python, and use the same interpreter for later core commands. In DSH, treat every `python3 ...` example below as `<ppt-python> -B ...`; `-B` prevents bytecode caches from modifying installed skill resources. Never install into the package directory or mutate the host's global Python environment.
>
> Require optional groups only when the selected workflow needs them: `ingestion`, `preview`, `audio`, `office`, or `document-parser` (the last also needs `--document-parser-dir <path>`). This bundle does not inject system binaries, provider credentials, browser/editor access, or Hermes frontend delivery behavior. If a selected capability is unavailable, stop and report the exact failed preflight group instead of inventing a tool or path. Store project state under the current DSH session workspace, not a Hermes home directory. Tool names such as `read_file` and `run_in_background` describe the source workflow and must be mapped to capabilities actually exposed by the active DSH composition.

**Core Pipeline**: `Source Document → Create Project → [Template] → Strategist → [Image_Generator] → Executor Live Preview → Quality Check → Post-processing → Export`

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order; the output of each step is the input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **ONE USER-APPROVAL GATE — `APPROVAL_BUDGET = 1`** — The Step 4 **Final Build Confirmation** is the only ⛔ BLOCKING user-approval gate before formal deck generation. It is one complete, revisable package: content/medical boundary + deck plan/outline + Eight Execution Specs + generation note. Never confirm those parts separately. A user-requested revision stays inside the same gate until accepted; it does not create a second gate
> 3. **AFTER APPROVAL, NO MORE CONFIRMATION** — Once Final Build Confirmation is accepted, set the logical state `BUILD_APPROVED` and automatically complete design spec, image acquisition, SVG generation, speaker notes, quality gates, post-processing, and export. Do not call `clarify`, ask “continue/start generation?”, or wait for user approval again. Only a non-preference hard blocker (missing required file, privacy/safety issue, deterministic gate failure with no safe repair, or unavailable required tool with no fallback) may stop execution; report the blocker as a fact, not as another routine confirmation
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE) listed at the top; these MUST be verified before starting that Step
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN (e.g., writing SVG code during the Strategist phase)
> 6. **NO SUB-AGENT SVG GENERATION** — Executor Step 6 SVG generation is context-dependent and MUST be completed by the current main agent end-to-end. Delegating page SVG generation to sub-agents is FORBIDDEN
> 7. **SEQUENTIAL PAGE GENERATION ONLY** — In Executor Step 6, after the global design context is confirmed, SVG pages MUST be generated sequentially page by page in one continuous pass. Grouped page batches (for example, 5 pages at a time) are FORBIDDEN
> 8. **SPEC_LOCK RE-READ PER PAGE** — Before generating each SVG page, Executor MUST `read_file <project_path>/spec_lock.md`. All colors / fonts / icons / images MUST come from this file — no values from memory or invented on the fly. Executor MUST also look up the current page's `page_rhythm` (`anchor` / `dense` / `breathing`), `page_layouts` (which template SVG to inherit, if any), and `page_charts` (which chart template to adapt, if any). Empty / absent entries are intentional Strategist signals — see executor-base.md §2.1. This rule exists to resist context-compression drift on long decks and to break the uniform "every page is a card grid" default
> 9. **SVG MUST BE HAND-WRITTEN, NOT SCRIPT-GENERATED** — Every SVG page is written by the main agent directly, one page at a time (see rules 6 and 7). Writing or running a Python / Node / shell script that produces the SVG files in batch — looping over pages, templating from data, or emitting them via a generator — is FORBIDDEN, including under "save tokens", "quick draft", or "user is in a hurry" pretexts. The script-generation path was tried on a feature branch and abandoned: cross-page visual consistency depends on per-page authoring with full upstream context, which a generator script cannot reproduce
> 10. **NEVER HAND-ROLL RAW python-pptx TO BUILD A DECK** — Writing ad-hoc `python-pptx` code (`Presentation()` + `add_slide` / manual shapes / manual fonts & colors) to assemble slides is FORBIDDEN. It discards any uploaded template's real design and produces a generic, low-quality deck (this is exactly how a prior session failed: "没按模板 / 内容差"). There are exactly two sanctioned paths: to honor an **uploaded `.pptx` template** → `template_fill_pptx.py` (clones the template's real slides + replaces text); to **generate fresh designed pages** → the SVG pipeline (Steps 4–7). Hand-written python-pptx deck construction = execution failure.

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **Response language**: match the user's input and source materials. Explicit user override (e.g., "请用英文回答") takes precedence.
> - **Template format**: `design_spec.md` MUST follow its original English template structure (section headings, field names) regardless of conversation language. Content values may be in the user's language.

> [!IMPORTANT]
> ## 🔌 Compatibility With Generic Coding Skills
>
> - `ppt-master` is a repository-specific workflow, not a general application scaffold
> - Do NOT create `.worktrees/`, `tests/`, branch workflows, or generic engineering structure by default
> - On conflict with a generic coding skill, follow this skill unless the user explicitly says otherwise

## Main Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `<document-parser-dir>/scripts/pdf_dispatcher.py` | **统一源→Markdown 入口**（ADR-0044/0048）。接受 PDF / DOCX / XLSX / PPTX / HTML / EPUB / URL / 图片，自动分派到对应抽取器；扫描件/图片转 WiseOCR。产出 `<stem>.md` + `<stem>_files/*.png`（抽取的**原文原图**，含矢量图 200dpi render）+ `image_manifest.json`。**取代**旧的 `scripts/source_to_md/*.py`（后者保留但不再是入口）。 |
| `<skill-dir>/scripts/project_manager.py` | Project init / validate / manage |
| `<skill-dir>/scripts/analyze_images.py` | Image analysis |
| `<skill-dir>/scripts/latex_render.py` | LaTeX formula rendering (manifest-driven PNG assets) |
| `<skill-dir>/scripts/image_gen.py` | AI image generation (multi-provider) |
| `<skill-dir>/scripts/svg_quality_checker.py` | SVG quality check |
| `<skill-dir>/scripts/total_md_split.py` | Speaker notes splitting |
| `<skill-dir>/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `<skill-dir>/scripts/svg_to_pptx.py` | Export to PPTX |
| `<skill-dir>/scripts/update_spec.py` | Propagate a `spec_lock.md` color / font_family change across all generated SVGs |

For complete tool documentation, see `<skill-dir>/scripts/README.md`.

> **Windows note**: if a `python3 ...` command fails (common on python.org installs, which provide `python.exe` but not `python3.exe`), rerun the same command with `python` instead.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layout templates | `<skill-dir>/templates/layouts/layouts_index.json` | Query available page layout templates |
| Brand presets | `<skill-dir>/templates/brands/brands_index.json` | Query available brand identity presets (color / typography / logo / voice) |
| Visualization templates | `<skill-dir>/templates/charts/charts_index.json` | Query available visualization SVG templates (charts, infographics, diagrams, frameworks) |
| Icon library | `<skill-dir>/templates/icons/` | See `<skill-dir>/templates/icons/README.md`; search icons on demand with `ls templates/icons/<library>/ \| grep <keyword>` |

## Standalone Workflows

| Workflow | Path | Purpose |
|----------|------|---------|
| `topic-research` | `workflows/topic-research.md` | Pre-pipeline — gather broad web sources without a separate approval gate when the user supplies only a topic; inferred scope is surfaced in the single Final Build Confirmation |
| `template-fill` | `workflows/template-fill-pptx.md` | Give a native PPTX template deck plus source material; select fitting pages (a page may be reused for several output slides) and fill text back without SVG conversion |
| `reference-template-generate` 🩺 | `workflows/reference-template-generate.md` | **F3 functional scenario** — analyze the uploaded template, recommend fidelity-reuse vs reverse-redesign, and include intent/path/mapping in the single Final Build Confirmation before dispatching. Engines reused; pipeline unchanged (ADR-0037, amended by ADR-0078). F3b Path B step 2 ("reconstruct template design_spec") has a concrete style-gene extraction recipe in [`references/f3b-style-extraction.md`](references/f3b-style-extraction.md) |
| `create-template` | `workflows/create-template.md` | Standalone layout template creation workflow |
| `create-brand` | `workflows/create-brand.md` | Standalone brand-only template creation (identity preset; no SVG page roster) |
| `medical-byo-template` 🩺 | `workflows/medical-byo-template.md` | Medical fork — turn a doctor's own hospital / department deck or logo into a reusable medical **deck** / **brand** (reverse-engineer + de-identify), so it can be reused like a preset |
| `resume-execute` | `workflows/resume-execute.md` | Phase B entry — resume execution in a fresh chat after Phase A (Step 1–5) completed in another session (split mode) |
| `verify-charts` | `workflows/verify-charts.md` | Chart coordinate calibration — run after SVG generation if the deck contains data charts |
| `customize-animations` | `workflows/customize-animations.md` | Object-level PPTX animation customization — run only when the user explicitly asks to tune animation order/effects/timing |
| `live-preview` | `workflows/live-preview.md` | Browser-based live preview — auto-started during generation and re-enterable any time the user mentions "live preview", "preview", "看效果", or wants to click/select a slide element |
| `visual-review` | `workflows/visual-review.md` | Per-page rubric-based visual self-check — run only when the user explicitly asks for a visual re-pass on the generated SVGs (between Executor and post-processing). Opt-in only; never invoked by the main pipeline. |

> 🩺 **F3 front-door (参照上传模板生成)**: when the user uploaded a PPT to **reference as a template / style for a NEW deck** (not the from-scratch flow, and not "fill this exact deck verbatim"), enter [`workflows/reference-template-generate.md`](workflows/reference-template-generate.md) first. Analyze the source deck and content before asking; put the recommended **保真复用 (fidelity-reuse)** vs **逆向重设计 (reverse-redesign)** path and page mapping inside the same Step 4 Final Build Confirmation. Do not run a separate clarify spine. The source fork records this behavior in ADR-0037 and ADR-0078; those repository-level records are not package resources.

---

## Workflow

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

> [!IMPORTANT]
> ## 🎯 Uploaded a `.pptx`? Decide its ROLE before doing anything else
>
> An uploaded `.pptx` can play three different roles. Mis-reading the role is the #1 failure mode (a real session free-designed a generic deck because it treated a **template** as a content source). Decide first:
>
> | User signal | The `.pptx` is a… | Go to |
> |---|---|---|
> | "按这个模板 / 用这个模板 / 套用这个 ppt / fill into this deck / 按这个 ppt 的样式做" — i.e. reuse its DESIGN, usually with separate content (讲解词 / 文档 / 主题) | **TEMPLATE** (a slide library) | [`template-fill-pptx`](workflows/template-fill-pptx.md) workflow — **stop here, do not continue Step 1's conversion table for this file** |
> | "把这个 ppt 的内容重做 / 基于这份 ppt 的内容生成新 ppt"，design doesn't matter | **CONTENT source** | convert with `ppt_to_md.py` below → normal pipeline |
> | "把我院/科室的模板存成可复用的预设 / 以后都用这个模板" | **REUSABLE ASSET** | [`medical-byo-template`](workflows/medical-byo-template.md) (reverse-engineer + register) |
>
> For a **TEMPLATE** job, the *content* to fill may come from (a) a separate uploaded file (md / docx / text — e.g. a "讲解词" document), or (b) the template pptx's **own speaker notes** — extract them with `python3 <document-parser-dir>/scripts/pdf_dispatcher.py -i <file> -o <dir> -n <stem>` (dispatcher routes `.pptx` to the PPTX extractor) and use the `### Speaker Notes` (讲解词) as the content. The template's own topic may differ entirely from the content — that is normal; reuse the design, replace the copy.

> **No source content?** When the user supplies only a topic name or requirements without any file or substantive description, run the [`topic-research`](workflows/topic-research.md) workflow first, then return here with its products as input.

When the user provides non-Markdown content, convert it via the **unified document-parser dispatcher** — one entry point for every format (it auto-detects and routes internally, OCR-falls-back for scanned PDFs/images):

```bash
python3 <document-parser-dir>/scripts/pdf_dispatcher.py -i <file-or-URL> -o <out_dir> -n <clean-stem>
```

| User Provides | Notes |
|---------------|-------|
| PDF file | Text PDF → figures/tables extracted to `<stem>_files/*.png`; scanned PDF → auto WiseOCR |
| DOCX / Word / Office document | DOCX/HTML/EPUB/IPYNB native; legacy .doc/.odt/.rtf/.tex via pandoc |
| XLSX / XLSM / Excel workbook | .xlsx/.xlsm; legacy .xls should be resaved as .xlsx |
| CSV / TSV | Read directly as plain-text table source (no dispatcher needed) |
| PPTX / PowerPoint deck | **only when the pptx is a CONTENT source** (see role gate above; a pptx used as a TEMPLATE goes to `template-fill-pptx`, not here) |
| EPUB / HTML / LaTeX / RST / other | dispatcher routes to the document extractor |
| Web link / WeChat / high-security site | pass the `<URL>` as `-i`; WeChat needs `curl_cffi` (in `requirements.txt`) |
| Markdown | Read directly (no dispatcher needed) |

> **⚠️ 抽取的原文原图是一等资产 — 必须消费，不得即席另抽。**
> dispatcher 同时产出 `<out_dir>/<stem>_files/*.png`（原文图/表的抽取原图，含用 `page.get_drawings()` 渲染的矢量图）+ `image_manifest.json`。
> Step 2 `import-sources --move` 会把它们连同 md 一起搬进项目并传播到 `images/`（`source: pdf-raster|pdf-vector` 标记出处）。
> **禁止**用 `python3 -c "import fitz … page.get_text()"` 之类的即席脚本自己读 PDF —— 那样丢掉所有图、绕过统一出口，正是文献汇报重绘失真的根因（run `mrcwdt1hh3rhsn`）。需要文字就 `read_file` 生成的 `<stem>.md`。
> **journal_club（文献汇报）另有图表保真硬要求**，见 [`references/medical-scenarios.md`](references/medical-scenarios.md) §5。

> **Office vector assets (EMF/WMF) from DOCX/PPTX sources**:
> `doc_to_md.py` / `ppt_to_md.py` extract embedded Office vector images (.emf/.wmf)
> alongside bitmap images. After `import-sources`, these land in `images/`
> together with `image_manifest.json` and are first-class assets in §VIII Image Resource List.
>
> **Do NOT convert EMF/WMF to PNG.** The PPT Master pipeline preserves them as external
> references (`finalize_svg.py` skips them) and `svg_to_pptx.py` embeds them as
> PPTX-native media via `image/x-emf` / `image/x-wmf` MIME — PowerPoint renders them at full vector fidelity.
> Converting via LibreOffice/Inkscape introduces CJK font substitution drift and
> rasterization loss; the original EMF/WMF is always higher fidelity than the converted PNG.
>
> Browser-based live preview cannot render EMF (will show blank) — this is expected;
> the PPTX output is the source of truth.

**✅ Internal checkpoint — Verify source content is ready, then proceed to Step 2 without asking the user.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
python3 <skill-dir>/scripts/project_manager.py init <project_name> --format <format>
```

Format options: `ppt169` (default), `ppt43`, `xhs`, `story`, etc. For the full format list, see `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `python3 <skill-dir>/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User provided text directly in conversation | No import needed — content is already in conversation context; subsequent steps can reference it directly |

> ⚠️ **MUST use `--move`** (not copy): all source files — Step 1's generated Markdown, original PDFs / MDs / images — go into `sources/` via `import-sources --move`. After execution they no longer exist at the original location. Intermediate artifacts (e.g., `_files/`) are handled automatically.
>
> **Extracted original figures**: the dispatcher's `<stem>_files/*.png` + `image_manifest.json` are moved into `sources/<stem>_files/` **and propagated into `images/`** (namespaced `<stem>__<file>.png`, `image_manifest.json` merged, `source: pdf-raster|pdf-vector` preserved) — so the paper's own figures become first-class §VIII Image Resource List assets you embed, not redraw. Confirm `images/` is non-empty when the source had figures.

**✅ Internal checkpoint — Verify project structure exists, `sources/` contains all source files, and converted materials are ready. Proceed to Step 3 without asking the user.**

---

### Step 3: Template Option

🚧 **GATE**: Step 2 complete; project directory structure is ready.

**Default — free design.** Proceed directly to Step 4. Do NOT query any `*_index.json` unless triggered. Do NOT ask the user. Do NOT proactively suggest, hint at, or fuzzy-match any template based on content, slug-like words, or vague style descriptions.

**Template flow triggers ONLY on explicit directory paths** supplied by the user in their initial message. The trigger rule is mechanical, not interpretive:

| User input contains | Step 3 action |
|---|---|
| One or more explicit template directory paths (each resolves to a directory containing `design_spec.md` with `kind: brand` / `kind: layout` / `kind: deck` in its YAML frontmatter) | Read each spec's `kind`, dispatch per the kind matrix below, fuse if multiple |
| Anything else — bare template names ("用 academic_defense"), style descriptions ("麦肯锡风格"), brand mentions ("招商银行风格"), vague intent ("想用个模板"), or silence | Skip Step 3, free design |

There is no slug matching, no name lookup, no fuzzy resolution. A name without a path does not trigger — the user must give a path the AI can `cd` into.

> Style descriptions ("麦肯锡风格" / "Keynote 风" / "极简风" / etc.) never trigger Step 3. They flow into the Final Build Confirmation as a style brief (color / typography / tone in items e–g).

> Bare names ("academic_defense", "招商银行", "anthropic") do NOT trigger Step 3 even if a matching directory exists in the library. The user must give a path. AI must not "helpfully" resolve a name to a path.

> "What templates exist?" is out-of-band Q&A — answer by listing entries from `brands_index.json` / `layouts_index.json` / `decks_index.json` together with their paths. Listing alone does not advance the pipeline; the user must send a path back to trigger Step 3.

> To create a new layout or deck, read [`workflows/create-template.md`](workflows/create-template.md). To create a new brand, read [`workflows/create-brand.md`](workflows/create-brand.md).

> 🩺 **Medical fork note**: the strict "explicit path only / never suggest" rule above still governs Step 3. The one medical exception is handled later: in Step 4 the Strategist runs a **Medical Scenario Pre-scan** and may *recommend* a finished, ready-to-use **deck** (`templates/decks/clinical_report` / `research_academic` / `medical_education` / `institutional_official`) — preferred for "上手即用" — or, when only structure is wanted, a hospital-styled **layout** (`templates/layouts/medical_university` / `medical_research` / `medical_official`), by naming its path and copying it only after the single Final Build Confirmation is accepted. If the user already gave an explicit medical template path here, dispatch it normally. If the user is bringing **their own** hospital/department `.pptx` or logo, resolve intent inside that same package: **one-off "按这个模板生成这次的 ppt"** → [`workflows/template-fill-pptx.md`](workflows/template-fill-pptx.md) (fill content into a clone of their deck — see Step 1 role gate); **"把它存成以后可复用的预设"** → [`workflows/medical-byo-template.md`](workflows/medical-byo-template.md) (reverse-engineer + register a reusable deck/brand).

#### Three template kinds

The architecture has three independent reference bundles. Full schema in [`docs/zh/templates-architecture.md`](docs/zh/templates-architecture.md). Summary:

| Kind | Physical dir | Contains | Frontmatter |
|---|---|---|---|
| **brand** | `templates/brands/<id>/` | identity-only segment: color / typography / logo / voice / icon style | `kind: brand` |
| **layout** | `templates/layouts/<id>/` | structure-only segment: canvas / page structure / page types / SVG roster | `kind: layout` |
| **deck** | `templates/decks/<id>/` | full replica: identity + structure + middle (template overview) segments | `kind: deck` |

**Segment ownership** (governs fusion override priority):

| Segment | Sections | Owner kind on fusion |
|---|---|---|
| Identity | Color Scheme / Typography / Logo / Voice & Tone / Icon Style | brand |
| Structure | Canvas / Page Structure / Page Types / SVG Roster | layout |
| Middle | Template Overview (use cases / design intent) | deck (no other kind writes this) |

#### Single-path dispatch

| User path's `kind` | Step 3 action |
|---|---|
| `kind: brand` | Copy `design_spec.md` + logo files + asset subdirs (`images/` / `illustrations/` / `icons/`) into `<project>/templates/`. Strategist locks identity segment as truth; structure stays free. |
| `kind: layout` | Copy `design_spec.md` + SVG roster + asset files into `<project>/templates/`. Strategist locks structure; identity is decided in Final Build Confirmation items e–g. |
| `kind: deck` | Copy everything (`design_spec.md` + SVGs + logos + assets) into `<project>/templates/`. Strategist locks all segments; the Final Build Confirmation labels locked fields and focuses editable values on audience / page count / outline / tone tweaks. |

```bash
TEMPLATE_DIR=<user-supplied path>
cp -r ${TEMPLATE_DIR}/* <project_path>/templates/
```

The single-line copy suffices for all three kinds — the spec's `kind` field tells Strategist how to read it; downstream code doesn't distinguish.

#### Multi-path fusion

When the user gives two or more paths of **different kinds**, Step 3 fuses them into a single `<project>/templates/design_spec.md`. **Default granularity is segment-level integer replacement** — entire identity / structure / middle segments are taken from the highest-priority source for that segment, no implicit field-level mixing.

Override priority by segment:

| Combination | Identity from | Structure from | Middle from |
|---|---|---|---|
| brand only | brand | (free design) | (none) |
| layout only | (free design) | layout | (none) |
| deck only | deck | deck | deck |
| brand + layout | brand | layout | (none) |
| brand + deck | brand (overrides deck) | deck | deck |
| layout + deck | deck | layout (overrides deck) | deck |
| brand + layout + deck | brand | layout | deck |

Field-level micro-adjustment (e.g. "use anthropic brand but primary changed to #FF0000") is **not** part of Step 3 fusion — it flows into Final Build Confirmation items e–g as a normal user request.

#### Same-kind multiple paths — conflict resolution

When the user gives two paths of the **same kind** (e.g. `brands/anthropic` + `brands/google`), Step 3 records the segment conflicts and prepares a recommended resolution. Do **not** prompt here; put the conflict summary, recommended winner, and alternatives into the Step 4 Final Build Confirmation:

```
Final Build Confirmation / Template conflict:
    你给了两个 brand，检测到段级冲突：
    - Color Scheme（Anthropic 橙红 vs Google 多色）
    - Typography（Styrene/AnthropicSans vs GoogleSans/Roboto）
    - Logo（Anthropic 标 vs Google 标）
    - Voice & Tone（restrained vs friendly）
    - Icon Style（stroke vs filled）

    推荐：(a) 全部按 Anthropic（<一句内容适配理由>）
    可改为：(b) 全部按 Google / (c) 逐段挑
```

Rules:
- Default: no implicit ordering — every cross-source segment difference is reported as a conflict, with one evidence-backed recommendation
- If the user chooses `(c)`, revise the same Final Build Confirmation package with the selected segments; do not open a second approval gate
- Field-level conflicts are out of scope — segment-level only
- Three or more same-kind paths are not supported — recommend the best two in the Final Build Confirmation and list the excluded paths; do not ask beforehand

#### Fused spec provenance

When fusion happens (any multi-path case), the resulting `<project>/templates/design_spec.md` carries a provenance block immediately under its H1:

```markdown
> **Fused from:**
> - deck: `templates/decks/招商银行/` （base）
> - brand: `templates/brands/anthropic/` （identity override）
> - layout: `templates/layouts/academic_defense/` （structure override）
> - conflicts resolved: Color Scheme from anthropic（user picked a）
```

Single-path Step 3 does **not** add provenance (the source is self-evident from the copied files).

**✅ Internal checkpoint — Default path proceeds to Step 4 without user interaction. If explicit template paths were supplied, their dispatch/fusion plan and any unresolved same-kind conflict are ready for the single Final Build Confirmation.**

---

### Step 4: Strategist Phase (MANDATORY — cannot be skipped)

🚧 **GATE**: Step 3 complete; default free-design path taken, or (if triggered) template files copied into the project.

First, read the role definition:
```
Read references/strategist.md
```

> 🩺 **Medical Scenario Pre-scan (this fork)**: also `Read references/medical-scenarios.md`. Before drafting the Final Build Confirmation, classify the source / topic into one of its scenarios (clinical case, NSFC grant, academic conference, journal club, teaching rounds, CME, title-promotion, accreditation, drug/device filing). When one matches:
> - Seed §IX Content Outline from the playbook's **outline skeleton** (confirmation c/d), and recommend its **palette** (confirmation e) and **charts** (§VII / `templates/charts/` — `survival_curve_km` / `forest_plot` / `consort_flow` / `roc_curve` for research scenarios).
> - **Recommend the mapped finished DECK by naming its directory path** (NOT a layout) inside the bundled confirmations — a deck is ready-to-use (identity + structure + look bundled), so it is the only "上手即用" preset; a layout is a bare skeleton that loses the deck's finished polish. Scenario→deck: clinical case / teaching rounds → `templates/decks/clinical_report/`; academic conference / journal club → `templates/decks/research_academic/`; CME / training → `templates/decks/medical_education/`; **work report / QC / accreditation / grant / title-promotion / drug-device filing → `templates/decks/institutional_official/`**. ⚠️ The official deck is `institutional_official`, **not** the layout `medical_official` — name the deck. This is a recommendation, not an auto-copy — it does not bypass the ⛔ BLOCKING gate. **Only after the user confirms**, copy it into the project exactly as Step 3 would (`cp -r templates/decks/<id>/* <project_path>/templates/`), then continue. The structure-only **layout** (`templates/layouts/medical_*/`) is the fallback only when the doctor wants just the structure or is bringing their own brand.
> - If the doctor is bringing **their own** hospital / department `.pptx` or logo, do not force a preset. Disambiguate: a **one-off "按这个模板做这次的 deck"** goes to [`workflows/template-fill-pptx.md`](workflows/template-fill-pptx.md) (fill into a clone); only "**存成可复用预设**" routes to [`workflows/medical-byo-template.md`](workflows/medical-byo-template.md) to reverse-engineer it into a reusable deck/brand, then lock that.
> - This is a deliberate, documented softening of Step 3's "never proactively suggest a template" rule, scoped to medical scenarios only. The source fork records the rationale in ADR-0034 and ADR-0035; those repository-level records are not package resources. If **no** scenario matches, do NOT force-fit one — drop back to generic free design.

> ⚠️ **Mandatory gate**: before writing `design_spec.md`, Strategist MUST `read_file templates/design_spec_reference.md` and follow its full I–XI section structure. See `strategist.md` Section 1.

## Final Build Confirmation — the only user approval gate

⛔ **BLOCKING USER APPROVAL — FINAL BUILD CONFIRMATION**: present exactly one complete recommendation package and wait for explicit acceptance or modification. This is the only user-approval gate for the entire task (`APPROVAL_BUDGET = 1`). If the user changes an item, revise this same package until accepted. Never ask for content-boundary approval and PPT-spec approval separately.

The package MUST contain all four sections:

1. **Content Contract** — topic; matched medical scenario (or no match); scope/focus and explicit exclusions; source/evidence boundary; output language; target audience/occasion; core message; missing facts marked `待补充` rather than invented. For `journal_club`, include its five levers here with recommended defaults: audience/setting, duration/page count, critique focus, must-embed original figures/tables, and prior-evidence extension on/off.
2. **Deck Plan** — functional mode (F1/F3a/F3b/etc.); chosen/recommended template or free design; any template conflict resolution; recommended chapter/page outline; page count. For F3, this section also includes inferred intent, recommended reuse path, content source, page mapping, de-identification handling, and any escalation policy.
3. **Eight Execution Specs** — include all eight items below, prefilled with professional recommendations.
4. **Execution Note** — continuous vs split mode. When AI images are used, also include the recommended rendering × palette choice, alternatives, hero-page list, and embedded-vs-editable title policy here; there is no later image-style or hero-page confirmation.

**Eight Execution Specs** (full template: `templates/design_spec_reference.md`):

1. Canvas format
2. Page count range
3. Target audience
4. Style objective
5. Color scheme
6. Icon usage approach
7. Typography plan, including formula rendering policy
8. Image usage approach

**Mandatory — split-mode note** (not a ninth confirmation): after listing the eight confirmation details, you MUST append exactly one short line (rendered in the user's language, prefixed with 💡) about generation mode. Pick the variant by qualitative read of Phase A signals — recommended page count, source-material bulk, whether `topic-research` ran with substantial web-fetch accumulation:

| Signal read | Line content |
|---|---|
| Heavy (long page count / bulky sources / heavy web-fetch accumulation) | State estimated page count and large source size; recommend switching to [split mode](workflows/resume-execute.md) after Step 5 — stop this chat, open a fresh window and input `继续生成 projects/<project_name>` to enter Phase B (SVG generation + export); no response or "continue" = default continuous mode. |
| Normal (default) | State scale is moderate, default continuous mode generates in one go; if mid-way window switch is desired, input `继续生成 projects/<project_name>` after Step 5 to switch to [split mode](workflows/resume-execute.md). |

This line is required inside the Final Build Confirmation every run — the user must always see the mode choice exists. Whether to modify it is part of this same approval gate.

**Formula rendering policy lives inside item 7 (Typography plan)**:

| Policy | Behavior |
|---|---|
| `mixed` (default) | Strategist renders complex formula-worthy expressions as PNG assets; simple inline expressions remain editable text / Unicode |
| `render-all` | Strategist renders every formula-worthy expression as PNG assets |
| `text-only` | No formula rendering; formulas remain editable text / Unicode |

After the Final Build Confirmation is approved and **before outputting `design_spec.md` / `spec_lock.md`**, if the confirmed formula policy is `mixed` or `render-all` and the content contains formula-worthy expressions, Strategist MUST:

1. Identify explicit LaTeX and any source expressions that should be faithfully structured as formulas.
2. Write `<project_path>/images/formula_manifest.json` with only the formulas selected for rendering.
3. Run:
   ```bash
   python3 <skill-dir>/scripts/latex_render.py <project_path>
   ```
4. Include the rendered formula PNGs as `Acquire Via: formula`, `Status: Rendered`, `Type: Latex Formula` rows in `design_spec.md §VIII Image Resource List`; also list them in `spec_lock.md images` with `| no-crop`.

The formula renderer uses a provider fallback chain by default: `codecogs,quicklatex,mathpad,wikimedia`. The first three are color-aware; Wikimedia is an availability fallback. Formula PNGs are transparent by default: manifest `background` is the temporary render matte and transparency-removal reference, not a retained final background unless `transparent: false` is set for that item. Do not scan `spec_lock.md` for `$...$` or `$$...$$`. Dollar-delimited math in source material is only a signal for Strategist; the renderer consumes the explicit manifest.

If the user provided images or formula PNGs were rendered, run analysis **before outputting the design spec**:
```bash
python3 <skill-dir>/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **Image handling**: NEVER directly read / open / view image files (`.jpg`, `.png`, etc.). All image info comes from `analyze_images.py` output or the Design Spec's Image Resource List.

**Output**:
- `<project_path>/design_spec.md` — human-readable design narrative
- `<project_path>/spec_lock.md` — machine-readable execution contract (skeleton: `templates/spec_lock_reference.md`); Executor re-reads before every page

**✅ Checkpoint — Phase deliverables complete, auto-proceed to next step**:
```markdown
## ✅ Strategist Phase Complete
- [x] Final Build Confirmation accepted (Content Contract + Deck Plan + Eight Execution Specs + Execution Note)
- [x] Split-mode note appended below the eight items (heavy or normal variant)
- [x] Design Specification & Content Outline generated
- [x] Execution lock (spec_lock.md) generated
- [ ] **Next**: Auto-proceed to [Image_Generator / Executor] phase
```

---

### Step 5: Image Acquisition Phase (Conditional)

🚧 **GATE**: Step 4 complete; Final Build Confirmation accepted (`BUILD_APPROVED`); Design Specification & Content Outline generated. Any formula rows already have `Acquire Via: formula` and `Status: Rendered`.

> **Trigger**: At least one row in the resource list has `Acquire Via: ai` and/or `Acquire Via: web`. If every row is `user`, `formula`, or `placeholder`, skip to Step 6.

**Always load the common framework**:

```
Read references/image-base.md
```

Then **lazy-load the path-specific reference** for each row that actually needs it:

| Acquire Via | Load reference (only if any such row exists) | Run |
|---|---|---|
| `ai` | `references/image-generator.md` | `python3 <skill-dir>/scripts/image_gen.py --manifest <project_path>/images/image_prompts.json` |
| `web` | `references/image-searcher.md` | `python3 <skill-dir>/scripts/image_search.py ...` |
| `user` / `placeholder` | (skip) | (skip) |

A deck with only `ai` rows never loads `image-searcher.md`; a deck with only `web` rows never loads `image-generator.md`. A mixed deck loads both, processes each row through its own path, and writes both `image_prompts.json` and `image_sources.json`.

> ⚠️ **In-pipeline ai path MUST use manifest mode** — even when only 1 ai row exists. Write `images/image_prompts.json` first, then run `image_gen.py --manifest`, then `image_gen.py --render-md` to produce the `image_prompts.md` sidecar. The positional form (`image_gen.py "prompt" ...`) is reserved for **out-of-pipeline one-off testing / single-image fixups** — it skips manifest + sidecar, leaving no audit trail.

Workflow:

1. Extract all rows with `Status: Pending` and `Acquire Via ∈ {ai, web}` from the design spec
2. Generate prompts (ai rows) and/or run search (web rows) per [image-base.md](references/image-base.md) §2 dispatch table
3. Verify every row reaches a terminal status: `Generated` (ai success), `Sourced` (web success), or `Needs-Manual`

**✅ Internal checkpoint — Verify acquisition was attempted for every row; do not ask the user**:
```markdown
## ✅ Image Acquisition Phase Complete
- [x] image_prompts.json created (when any ai rows processed)
- [x] image_prompts.md sidecar rendered (when any ai rows processed)
- [x] image_sources.json created (when any web rows processed)
- [x] Each row: status is `Generated` / `Sourced` / `Needs-Manual` (no `Pending` remaining)
```

**Default — auto-proceed to Step 6.** Only when the user's Step 4 response explicitly opted into split mode (in reply to the optional hint), output the Phase A hand-off below and stop this conversation:

  ```markdown
  ## ✅ Phase A Complete
  - [x] Spec: `design_spec.md`, `spec_lock.md`
  - [x] Resources: `sources/`, `images/`, `templates/`
  - [ ] **Next**: open a fresh chat window and input `继续生成 projects/<project_name>` to enter Phase B via the [`resume-execute`](workflows/resume-execute.md) workflow.
  ```

> On acquisition failure, do NOT halt — follow the Failure Handling rule in [image-base.md](references/image-base.md) §5: retry once, then mark the row `Needs-Manual`, report to user, and continue to the checkpoint above.

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete; all prerequisite deliverables are ready.

Read the role definition based on the selected style:
```
Read references/executor-base.md          # REQUIRED: common guidelines
Read references/shared-standards.md       # REQUIRED: SVG/PPT technical constraints
Read references/executor-general.md       # General flexible style
Read references/executor-consultant.md    # Consulting style
Read references/executor-consultant-top.md # Top consulting style (MBB level)
```

> Only read executor-base + shared-standards + one style file.

**Execution Parameter Receipt (Mandatory, NON-BLOCKING)**: before the first SVG, output key design parameters already approved in the spec (canvas dimensions, color scheme, font plan, body font size). This is an audit receipt, not a question: do not ask the user to confirm and do not wait. See executor-base.md §2.

**Live Preview Auto-Startup (Mandatory)**: before the first SVG, automatically start the browser editor in live mode and keep it running continuously through Executor + Step 7 export:
```bash
python3 <skill-dir>/scripts/svg_editor/server.py <project_path> --live --no-browser
```
- **Launch it non-blocking** (run it as a background process — the harness `run_in_background` option, or `nohup … &`). `server.py` calls `app.run(...)`, which blocks the foreground until the server stops; if you run it in the foreground the Executor will hang and never generate a page.
- **`--no-browser` is required on this deployment** (headless remote Linux, no X / no desktop): the default auto-opens a browser, which fails or does nothing here. `http://localhost:5050` is only reachable after the user sets up an SSH port-forward — so treat the preview as best-effort, not a precondition for generating pages.
- Start it immediately when Executor begins; `svg_output/` may be empty. Port conflict → `--port <other>` and report the actual URL.
- Do not wait for the server to exit and do not wait for user confirmation after startup; proceed straight to page generation. If startup fails, log it and continue — the PPTX output is the source of truth, not the live preview.
- **Service must keep running** until one of: (a) the user clicks **Exit preview** in the browser, or (b) the user explicitly asks in chat to stop it. Generation continues even if the user closes the editor.
- **Do NOT read or apply submitted annotations during generation.** Users may annotate at any time, but Executor proceeds without touching them. The window to apply annotations opens only after Step 7 completes — see [`workflows/live-preview.md`](workflows/live-preview.md).
- The editor also supports **staged direct edits** (text content + SVG element attributes previewed immediately, then written to `svg_output/` only when the user clicks **Apply changes**; `Ctrl+Z` / Undo drops staged edits) alongside annotation; re-export stays chat-driven. Full scope and editor details: see [`workflows/live-preview.md`](workflows/live-preview.md) Notes.

**Pre-generation Batch Read (Mandatory)**: before the first SVG, batch-read every distinct layout SVG referenced in `spec_lock.page_layouts` and every distinct chart SVG referenced in `spec_lock.page_charts` (plus any §VII backup charts). One read per file, up front — do not re-read these during page generation. See executor-base.md §1.0.

**Per-page spec_lock re-read (Mandatory)**: before **each** SVG page, `read_file <project_path>/spec_lock.md` and use only its colors / fonts / icons / images, plus the per-page `page_rhythm` / `page_layouts` / `page_charts` lookups (resolves to template SVGs already loaded in the batch read above). Resists context-compression drift on long decks. See executor-base.md §2.1.

> ⚠️ **Main-agent only**: SVG generation MUST stay in the current main agent — page design depends on full upstream context. Do NOT delegate to sub-agents.
> ⚠️ **Generation rhythm**: generate pages sequentially, one at a time, in the same continuous context. Do NOT batch (e.g., 5 per group).

**Resume awareness (Mandatory) — never regenerate completed pages (ADR-0053)**: before the first SVG, run
```bash
python3 <skill-dir>/scripts/resume_status.py <project_path>
```
It reads the `design_spec.md §IX` roster + `svg_output/` and reports **DONE** (present & well-formed) / **INVALID** (present but broken — a page a dropped session wrote half-way) / **MISSING**. Generate **ONLY** the pages it lists under `RESUME` (INVALID + MISSING), in that order; **do NOT regenerate a DONE page**. On this deployment long sessions drop — this makes a 20-page deck that died at page 14 resume from 14, not restart from 1. If it says `COMPLETE`, skip straight to the Quality Check Gate. (Resuming from a gap is still sequential one-at-a-time — it is NOT the forbidden batching. For visual consistency, `read_file` 1–2 DONE pages before resuming.)

**Visual Construction Phase**: generate the pages from the resume list above sequentially, one at a time, in one continuous pass → `<project_path>/svg_output/`

**Quality Check Gate (Mandatory)** — after all SVGs, BEFORE annotation handling and speaker notes:
```bash
python3 <skill-dir>/scripts/svg_quality_checker.py <project_path>
```
- Any `error` (banned SVG features, viewBox mismatch, spec_lock drift, etc.) MUST be fixed before proceeding — return to Visual Construction, regenerate that page, re-run check.
- `warning` entries (low-res image, non-PPT-safe font tail, etc.): fix when straightforward, otherwise acknowledge and release.
- Run against `svg_output/` (not after `finalize_svg.py` — finalize rewrites SVG and masks violations).

**Logic Construction Phase**: generate speaker notes → `<project_path>/notes/total.md`

**✅ Internal checkpoint — Verify all SVGs and notes are fully generated and quality-checked. Proceed directly to Step 7 post-processing without asking the user**:

> **⛔ STOP — do not proceed to Step 7 until every box below is checked with the *actual command output pasted*, not asserted.** A checked box you didn't run is the "thought it was done but wasn't" failure. State each result — "0 errors" / "20/20 mapped" is a finding you must report, not an empty box.

```markdown
## ✅ Executor Phase Complete
- [ ] Live preview started and kept available at the reported URL
- [ ] All SVGs generated to svg_output/ (state the count, e.g. 20/20)
- [ ] `svg_quality_checker.py` run against svg_output/ — paste the summary line; state "0 errors" explicitly, or list and fix them. (A clean run writes the `.svgqc_pass.json` the export gate checks.)
- [ ] No unexpanded icon placeholders: `svg_quality_checker.py` reports 0 missing-icon errors (every `<use data-icon=...>` resolves in templates/icons/).
- [ ] 🩺 journal_club only: each `Extracted` source figure **completeness-verified** — `render_pdf_region.py --verify-crop … --record images/figure_fidelity.json --asset <embedded filename>` returned **PASS** (coverage ≥ 92 % + caption in crop), not a legend/axis fragment — before embed, sized to its native ratio, and the `<image>` tagged `data-fidelity="source"`. **Mechanically enforced (ADR-0051)**: `svg_quality_checker.py` ERRORs (and the export gate blocks) for any no-crop Extracted original with no recorded PASS — so this box cannot be a paper check. Deterministic gate, vision optional (executor-base.md §6). Paste each verdict.
- [ ] No letterbox on `Extracted`/`no-crop` figures: `svg_quality_checker.py` reports 0 letterbox issues (box ratio ≈ image native ratio), or each non-Extracted one is justified. **Extracted-original letterbox is now an ERROR** (ADR-0051), not a warning.
- [ ] No off-canvas content: `svg_quality_checker.py` reports 0 off-canvas `<image>` errors (nothing positioned entirely outside the viewBox → renders nothing).
- [ ] Speaker notes generated at notes/total.md — state the heading count. (After Step 7.1, state how many mapped to SVG stems, e.g. "20/20 mapped"; if the deck is intentionally note-less, say "none — note-less deck" explicitly.)
- [ ] Chart pages (if any): `verify-charts` workflow run — paste the per-page receipt (receipt line count MUST equal the §VII data-chart page count). If the deck has no data-chart pages, state "no chart pages" explicitly.
```

> **Chart pages? (MANDATORY when present.)** If this deck contains data charts (bar / line / pie / radar / etc.), you **MUST** run the standalone [`verify-charts`](workflows/verify-charts.md) workflow before Step 7 to calibrate coordinates — it is the checkpoint box above, not an optional extra. AI models routinely introduce 10–50 px errors when mapping data to pixel positions; verify-charts eliminates that class of error. Only skip — and say so — when the deck has no data-chart pages.

> **Visual self-check (opt-in)?** If the user explicitly asked for a per-page visual re-pass on the SVGs ("跑一下视觉自检 / 视觉回看", "visual review", "check pages visually", etc.), run the standalone [`visual-review`](workflows/visual-review.md) workflow before Step 7. Do NOT run it by default and do NOT recommend it based on inferred model capability or deck size — trigger is user request only.

> **⛔ Delivery honesty (ADR-0050/0051).** Never announce the deck as done/verified on the strength of a check that did not actually complete. In particular: if you dispatched a background visual-QA sub-agent and it has **not returned**, either wait for it or state plainly "视觉复核未回，以下未经视觉确认" — do NOT ship "已通过视觉检查" (real regression: a run delivered while its QA sub-agent was still running). Prefer the **deterministic** gates (`svg_quality_checker.py`, `--verify-crop`) which complete in-session without vision. `svg_quality_checker.py` prints a machine-computed **`[DELIVERY]`** line (`QC errors=… warnings=… | letterbox=… | figures: P/N Extracted --verify-crop PASS`) — **copy that line verbatim** into the final delivery message as the check summary; do not hand-write "done" or claim anything beyond what it shows.

> **📍 Final `.pptx` path format (frontend contract).** When you deliver the finished deck, output the exported `.pptx` path as a **bare absolute path on its own line** — nothing else on that line. Do NOT wrap it in code fences (` ``` ` / ` ```text `), do NOT put it in inline backticks, do NOT render it as a markdown link, and do NOT prefix it with labels like `路径：`/`file://`. The frontend parses the raw path and handles it downstream; any wrapping breaks that. Correct:
>
> <workspace>/health-ppt-master-projects/<project>/exports/<project>_<timestamp>.pptx
>
> Emit exactly the path `svg_to_pptx.py` reported on its `[Done] Saved:` line.

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; all SVGs generated to `svg_output/`; speaker notes `notes/total.md` generated; `svg_quality_checker.py` passed (0 errors → `.svgqc_pass.json` written).

> ⚠️ **Notes naming is mechanically enforced at export.** `svg_to_pptx.py` matches each note file to a slide **only** by exact SVG stem (e.g. `03_政策引领.md` ↔ `03_政策引领.svg`) or a `slideNN` name. Hand-numbered files like `01.md` map to **nothing** and the deck would otherwise ship with the speaker notes silently dropped — so the exporter now **refuses (exit 1)** when `notes/` holds per-page files that don't all map. **Always produce notes via Step 7.1 `total_md_split.py`** (it names each note to its SVG stem); never hand-create `notes/NN.md`. `--allow-missing-notes` is only for a genuinely note-less deck.

🚧 **Image readiness GATE** (when Step 5 left ai rows in `Needs-Manual`): every expected file must exist at `project/images/<filename>` before running 7.1.

> If files are missing: PAUSE, list the missing filenames, point the user to `images/image_prompts.md` (each `### Image N:` block is paste-ready for ChatGPT / Gemini / Midjourney; auto-generated from `image_prompts.json`) and the required placement `project/images/<filename>`. Resume Step 7.1 only after all expected files are in place. `finalize_svg.py` and `svg_to_pptx.py` do not detect missing files at this layer — proceeding with gaps produces a deck with broken image references.

> ⚠️ Run the three sub-steps **one at a time** — each must complete successfully before the next.
> ❌ **NEVER** combine them into a single code block or shell invocation.

Canonical three-command pipeline (mirrors `references/shared-standards.md` §5):

**Step 7.1** — Split speaker notes:
```bash
python3 <skill-dir>/scripts/total_md_split.py <project_path>
```

> This is the **only** sanctioned way to produce per-page notes — do NOT hand-create `notes/NN.md`. The splitter names each note to its SVG stem and prints a 1:1 correspondence line; it **exits non-zero** if SVGs and notes don't match (regenerate `notes/total.md` and re-run before continuing). The export step (7.3) is the mechanical backstop: it refuses if notes exist but don't map.

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
python3 <skill-dir>/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
python3 <skill-dir>/scripts/svg_to_pptx.py <project_path>
# Output (default-flow mode):
#   exports/<project_name>_<timestamp>.pptx           ← native pptx (canonical output, reads svg_output/)
#   backup/<timestamp>/svg_output/                    ← Executor SVG source backup (always written)
#
# Add --svg-snapshot to additionally emit the SVG-image preview pptx alongside the native pptx:
#   exports/<project_name>_<timestamp>_svg.pptx      ← SVG preview pptx (reads svg_final/)
```

> **📍 Deliver the path bare.** The script prints the canonical output on a `[Done] Saved: <path>` line. When you hand the deck to the user, reproduce that absolute `.pptx` path as a **bare path on its own line** — no code fences, no inline backticks, no markdown link, no `路径：`/`file://` prefix. The frontend consumes the raw path (see the Delivery honesty note above).

> The native pptx consumes `svg_output/` directly so the converter can preserve
> high-fidelity primitives (icon `<use>` placeholders, image `preserveAspectRatio`
> → `srcRect`, rounded rect `rx/ry` → `prstGeom roundRect`). The `svg_output/`
> snapshot in `backup/<timestamp>/` is always written so the project can be
> re-exported from frozen SVG sources without re-running the LLM. The SVG-rendered
> preview pptx is opt-in via `--svg-snapshot` — live preview already provides the
> SVG visual reference, so it's only needed when you want a self-contained file
> to share. Pass `-s output` or `-s final` to force a single source if you need it.

> **Paragraph editability vs line fidelity** — by default, mergeable dy-stacked
> paragraph blocks collapse into one editable PowerPoint text frame with multiple
> `<a:p>`, improving body-text editing and resize/reflow behavior. Add `--no-merge`
> only when the user explicitly asks for strict line-layout fidelity or when a
> layout-tight page must keep every dy-stacked line as its own text frame. The
> merge detector is conservative; mixed-layout text falls back to per-line frames.

**Optional animation flags** (the defaults already enable rich entrance animations — adjust only when the user asks for something different):
- `-t <effect>` — page transition. Default `fade`. Options: `fade` / `push` / `wipe` / `split` / `strips` / `cover` / `random` / `none`.
- `-a <effect>` — per-element entrance animation. Default `auto` (map effect from group id: chart→wipe, card-/step-/pillar-→fly, title/takeaway→fade; image-like ids `hero` / `figure-` / `image` / `img-` / `kpi` cycle a richer pool — zoom / dissolve / circle / box / diamond / wheel — so multiple images vary across the deck). Pass `none` to disable, a specific effect like `fade`, or `mixed` for the legacy 16-effect cycle. Requires top-level `<g id="...">` groups (already required by Executor).
- `--animation-trigger {on-click,with-previous,after-previous}` — Start mode (matches PowerPoint's animation-pane Start dropdown). Default `after-previous` (click-free cascade; pace via `--animation-stagger`). Use `on-click` for presenter-paced reveals, or `with-previous` for all-at-once.
- `--animation-config <path>` — optional object-level sidecar. Default: `<project_path>/animations.json` when present.
- `--auto-advance <seconds>` — kiosk-style auto-play.

**Optional custom animations** (only when the user asks to tune animation order/effects/timing for specific objects):

Run the standalone [`customize-animations`](workflows/customize-animations.md) workflow. Default export already has global entrance animation; do not create `animations.json` unless object-level customization was requested.

**Optional recorded narration** (only when the user asks for narrated/video export):

Run the standalone [`generate-audio`](workflows/generate-audio.md) workflow. The AI picks a narration backend (`edge` by default, or a configured cloud provider such as ElevenLabs / MiniMax / Qwen / CosyVoice for high-quality or cloned voices), asks the user once (backend + voice + rate/settings + embed-or-not, all with recommended values), then executes `notes_to_audio.py` and (if chosen) re-exports the PPTX with `--recorded-narration audio`.

Do NOT call `notes_to_audio.py` directly without going through the workflow — `--voice` / `--voice-id` is required and the workflow produces the locale/provider-aware recommendation that makes the choice meaningful.

Full effect list, anchor logic, and limits: [`references/animations.md`](references/animations.md).

> ❌ **NEVER** substitute `cp` for `finalize_svg.py` — finalize performs multiple critical processing steps
> ❌ **NEVER** force `-s output` for the legacy/preview pptx (PowerPoint's internal SVG parser drops icons and rounded corners). The default auto-split already gives native the high-fidelity source it needs without touching legacy.
> ❌ **NEVER** use `--only` (it suppresses one of the two output files)

> **Post-export annotation window**: the preview service from Step 6 typically remains running after export. If the user submitted annotations in the browser (during Executor or after export) and now asks to apply them — they may quote the browser prompt (`Changes saved to svg_output...` / `修改已保存到 svg_output...`), say "apply my annotations" / "应用注解" / equivalent — run [`live-preview`](workflows/live-preview.md) Step 2 to apply and re-export. Annotations submitted during generation are also handled here, not earlier.

> **Direct edits in the browser**: the user may also stage text / SVG attribute edits in the preview. These land in `svg_output/` only after the user clicks **Apply changes**. If they ask to "re-export" / "重新导出" after applying such edits, just re-run Step 7.2–7.3 (finalize + export); no annotation-application step is needed unless they also saved AI-needed annotations.

> **Preview not running?** Any time the user mentions "live preview", "preview", "看效果", or wants to select/click a slide element and the service is not running, run [`live-preview`](workflows/live-preview.md) Step 1 to start it. If the service is already running, just point them at the URL — do not restart.

---

## Role Switching Protocol

Before switching roles, **MUST first read** the corresponding reference file. Output marker:

```markdown
## [Role Switch: <Role Name>]
📖 Reading role definition: references/<filename>.md
📋 Current task: <brief description>
```

---

## Reference Resources

| Resource | Path |
|----------|------|
| **Medical scenario playbooks (this fork)** | `references/medical-scenarios.md` |
| Shared technical constraints | `references/shared-standards.md` |
| Canvas format specification | `references/canvas-formats.md` |
| Image-text layout patterns (Primary structures + Modifier layers — combine freely) | `references/image-layout-patterns.md` |
| Image layout sizing (math for side-by-side container dimensions) | `references/image-layout-spec.md` |
| SVG image embedding | `references/svg-image-embedding.md` |
| Icon library | `templates/icons/README.md` |

---

## Notes

- Local preview: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: on generation issues (layout overflow, export errors, blank images, etc.), check `docs/faq.md` for known solutions
