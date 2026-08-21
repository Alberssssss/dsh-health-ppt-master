---
description: F3 — generate a NEW deck by analyzing an uploaded PPT as template/style, recommending fidelity-reuse vs reverse-redesign, and folding the path, mapping, content boundary, and execution specs into the single Final Build Confirmation. Reuses template-fill / pptx_template_import / the main pipeline as engines.
---

# Reference-Template Generate Workflow (F3 · 参照上传模板生成)

> **Medical fork · functional-interaction layer (ADR-0037, amended by ADR-0078).** The user uploaded a
> PPT (or slide images) as a template/style reference for a **new** deck. Analyze the carrier and available
> content first, then present exactly one complete **Final Build Confirmation**. After acceptance, run the
> selected existing engine straight through. This workflow does not re-implement any engine.

> [!CAUTION]
> ## 🚨 Hard guardrails (read first)
> - ❌ **Do not change the pipeline or core.** This workflow only orchestrates existing scripts/workflows.
> - ❌ **No fabricated medicine.** Doses / lab values / statistics / citations come only from user material
>   (same rule as `references/medical-scenarios.md`).
> - 🩺 **De-identification is a HARD gate** (see Step F3-2). The uploaded template may carry real patient
>   data; it must **never** survive into the new deck.
> - **Single approval budget**: `APPROVAL_BUDGET = 1`. Do not call `clarify` before or after the Final Build
>   Confirmation. Intent, reuse path, content source, mapping, and any escalation recommendation belong in
>   that one package. User modifications revise the same gate.
> - **After acceptance**: set `BUILD_APPROVED`; generate, validate, and export without another question or
>   wait. Only a genuine hard blocker may stop execution.
> - **Response language**: render the confirmation package in the user's language.

## The paradigm — 先分析 + 单一确认 + 一次性生成

| Layer | What | Mode |
|---|---|---|
| **分析汇总** | infer intent, inspect the carrier, assess fit, resolve content source, draft mapping | non-blocking |
| **外层护栏** | node order · de-id hard gate · which script + where artifacts land · quality gate · facts-only | hard — violating = failure |
| **单一确认** | intent + F3a/F3b recommendation + content contract + mapping + Eight Execution Specs | one revisable gate |
| **一次性生成** | after acceptance, fill/author/export runs continuously | no more approval waits |

## When to enter

Enter when the user uploaded a `.pptx` (or slide images / a deck screenshot set) **as a template/style to
reference for new content**, e.g. "按这个 ppt 的样式做一份新的" / "参照这个模板做我的病例汇报" /
"仿照这份 ppt 用这些资料做一版". If the user instead wants to **fill this exact deck unchanged** that is
still F3a below; if they want to **register the template for future reuse**, that is F3c (→
[`medical-byo-template.md`](./medical-byo-template.md)).

---

## Pre-confirmation analysis (NON-BLOCKING)

### A1 — Resolve intent (F3 / F2 / F3c)

Infer the macro-intent from the request. If the user explicitly wants F2 (optimize the existing deck) or F3c
(register a reusable template), route directly to the applicable workflow; those are different deliverables,
not extra confirmation steps for F3. If wording is ambiguous, retain F3 as the recommended interpretation
and list F2/F3c as alternatives inside the Final Build Confirmation. Do not ask a preliminary intent question.

### A2 — Assess reuse mode (F3a 保真复用 vs F3b 逆向重设计)

**First read the template cheaply, then assess fit — do NOT default to 保真复用.** Run
`template_fill_pptx.py analyze` (or `pptx_template_import.py … --manifest-only`) to learn the template's
page-types/slots, read the user's content shape, then compute a **fit assessment** before recommending:

1. **Page-type coverage** — count *distinct usable* source page-types vs the number of new pages the content
   needs. If new pages **> distinct usable source pages** (i.e. you'd have to **reuse one source slide for
   several different-topic pages**), that is a red flag for 保真复用 (see the reuse trap below).
2. **Visual portability** — do the source slides carry **topic-specific** baked-in graphics (architecture
   diagrams, flow charts, photos, data charts)? Template-fill **swaps text only — it never replaces images
   (v1)**. If a source page's diagram is about the *old* project, the new copy keeps that *wrong* diagram.
3. **Missing visuals** — does the new content need a chart/page-type the template lacks (KM/forest/CONSORT…)?

> 🚨 **The 保真复用 reuse trap (2026-06-18 真实事故).** Forcing 20 new pages onto a 25-page deck where only
> ~11 page-types fit → the model reused source slide 8 for *三* unrelated topics; the same baked-in diagram
> appeared on all three, and 37 original-project images carried over under new captions = a "保真但语义错位"
> frankenstein with 54 capacity warnings. **保真复用 ≈ in-place text swap; it cannot fix project-specific
> visuals or invent missing layouts.** When the source's value *is* its custom diagrams and they don't match
> the new content, 保真复用 is the **wrong** call — recommend 逆向重设计.

| Recommend | When (ALL of) |
|---|---|
| **F3a 保真复用** | new content maps ~1:1 onto **distinct** source page-types (little/no reuse of one slide for different topics); source visuals are **generic/reusable** (layout shells, not topic-specific diagrams); user prioritizes speed/fidelity over per-page coherence |
| **F3b 逆向重设计** (lean here when in doubt) | new pages > usable source page-types (would force topic-mismatched reuse); source carries topic-specific diagrams/photos that won't suit new content; content needs charts/pages the template lacks; user wants "参考风格、重新设计" |

Record the fit evidence and a recommended path. Do not ask the user here. Include both paths and the concise
reasoning inside the Final Build Confirmation.

### A3 — Resolve content source

Use attached/user-provided material when available. Otherwise use source-deck notes only when the request
clearly says to adapt them; for a stated topic, run `topic-research.md` non-blockingly. If neither a topic nor
content exists, mark the missing source as an unresolved required field in the Final Build Confirmation and
recommend the least-assumptive option. Supplying or changing it is a revision of the same gate, not a new gate.

> **Content drives the deck, not the template's page count/order.** A 20-section content against a 25-page
> template means select/reorder/reuse the best-fit pages, never pad or truncate.

---

## F3-2 — 🩺 De-identification hard gate (before any generation)

Scan the uploaded template (and, for F3a, the slides you will clone) for residual patient identity — names /
住院号 / 正脸照片 / real case specifics / real lab values in **non-replaced** shapes, headers, footers,
masters. Strip or replace all of it; the new deck and any persisted template carry only structure + brand +
`{{PLACEHOLDER}}`-style slots. This is a hard gate — do not proceed with patient data in the carrier.

For F3a specifically, **patient photos/images are enforced mechanically**: every cloned `<p:pic>` must have an
`image_edit` (`clear` deletes the picture *and its media bytes*, so the photo is removed from the file, not
merely hidden). `template_fill_pptx.py apply` **refuses (exit 2)** while any picture is un-handled. Do not pass
`--allow-source-images` over a patient image — only over generic logos/decoration.

## F3-3 — Medical Scenario Pre-scan (content × functional crossing)

Once content is in hand, run the normal Pre-scan ([`../references/strategist.md`](../references/strategist.md) §0 /
[`../references/medical-scenarios.md`](../references/medical-scenarios.md)): classify the content into a
medical scenario → seed §IX outline skeleton, charts (KM/forest/CONSORT/ROC…), and palette **for the new
deck's content**. The template governs *look/structure*; the Pre-scan governs *medical content shape*. This
is where the functional scenario (F3) and the content scenario meet.

---

## F3-4 — Final Build Confirmation (the only user-approval gate)

Prepare enough analysis to recommend a path and page mapping before presenting the package. Then use the
single Step 4 gate defined by [`SKILL.md`](../SKILL.md) and [`strategist.md`](../references/strategist.md).
The package must include:

1. **Content Contract** — intent, topic/medical scenario, content source and evidence boundary, audience,
   exclusions, de-identification treatment, and unresolved required fields;
2. **Deck Plan** — recommended F3a/F3b path with fit evidence, selected source pages or reconstructed style
   genes, page↔content mapping, missing-visual handling, outline, and alternatives;
3. **Eight Execution Specs** — show every item a–h; mark source-template-locked values as inherited instead of
   silently omitting them;
4. **Execution Note** — generation mode, AI-image rendering/palette choices when applicable, and export path.

⛔ **BLOCKING USER APPROVAL — FINAL BUILD CONFIRMATION**: wait for acceptance or modifications to this one
package. A modification revises the same package. Once accepted, set `BUILD_APPROVED`. Do not show another
Strategist confirmation when dispatching F3b, and do not ask for a plan confirmation before applying F3a.

---

## Path A — F3a 保真复用 (fidelity reuse)

Hand off to [`template-fill-pptx.md`](./template-fill-pptx.md) and follow it:
`template_fill_pptx.py analyze → scaffold → (build fill_plan by semantic page↔content mapping) → check-plan`.

### F3a quality gate (mechanically enforced by `apply` — not optional)

`check-plan` reports three things; the first is **enforced by the engine** (apply refuses), so you cannot
silently ship a frankenstein even if you skip this gate:

1. **Un-handled source pictures** (`IMAGES P… source=… unhandled […]` / `summary.unhandled_pictures > 0`):
   the source deck's pictures clone verbatim, so if the source deck is a **different project** (the common
   case for "参考风格做新主题"), those are the **wrong project's photos** — and possibly **patient imagery**.
   **`apply` REFUSES (exit 2, no file) until every kept `<p:pic>` has an `image_edit`.** For each picture:
   - **clear** → `{"image_id": "...", "action": "clear", "label": "［配图：…］"}` drops the old picture and
     leaves an editable placeholder box of the same size (also deletes the old media — de-id safe). Default move.
   - **replace** → `{"image_id": "...", "action": "replace", "new_image": "/path.png"}` when you have a fitting
     new image.
   - Do **not** reflexively pass `--allow-source-images` — that re-creates the 2026-06-18 wrong-image deck.
     Use it only if a kept picture is genuinely generic (logo / decorative). 患者影像绝不可保留。
2. **Reuse collisions** (`reused_sources > 0` / `REUSE …`): advisory. A reused source layout is fine once its
   pictures are handled per output page (step 1); pure text layouts reuse freely.
3. **High capacity warnings** (`warn` large relative to `ok`): the new copy doesn't fit the slots → rewrite
   shorter or remap to roomier pages. Don't apply with unresolved warnings (SKILL.md "don't think you're done").

> If most pages would need their pictures cleared AND the result would be mostly empty placeholders, the
> source deck is too project-specific to reuse — switch the **whole** deck to **F3b 逆向重设计**. But when the
> layout/style fits and only the images are wrong, F3a + `image_edits` (clear/replace) is the right, faithful
> path: original 版式 + 新文字 + 不带错图.

Before F3-4, fold every missing-visual escalation into the recommended plan: use the nearest page only when
semantically safe; otherwise recommend switching the whole deck to F3b. Do not ask about each exception.

> Per template-fill.md: do not splice clone-output and SVG-output into one file. Switching the *whole* deck
> to F3b is cleaner than per-page mixing when many pages need it.

After `BUILD_APPROVED` → `template_fill_pptx.py apply` → validate with `ppt_to_md.py` → report
`exports/<name>.pptx`, with no intervening approval wait.

## Path B — F3b 逆向重设计 (reverse + redesign)

The template becomes a **project-scoped template**, then the normal pipeline generates fresh:

1. `python3 <skill-dir>/scripts/pptx_template_import.py "<uploaded.pptx>"` → `manifest.json` + `svg/` +
   `svg-flat/` + `assets/` (per [`create-template.md`](./create-template.md) §1A read order).
2. Reconstruct a clean template `design_spec.md` (+ SVG roster + assets) into **`<project>/templates/`**
   (project-scoped, equivalent to SKILL.md Step 3 deck dispatch — not a global library register; that's F3c).
   De-identify per F3-2.
3. Enter the main pipeline after Strategist intake with the template locked: identity + structure come from
   the imported template. The accepted F3-4 package **already satisfies** SKILL.md Step 4 and sets
   `BUILD_APPROVED`; write `design_spec.md` / `spec_lock.md` from it without displaying a second confirmation.
4. Image_Generator (if needed) → Executor authors SVG pages inheriting the template → `svg_quality_checker`
   → `svg_to_pptx`. Standard pipeline, unchanged.

> F3b gives design freedom (new layouts, charts the template lacks) at the cost of being a separate
> deliverable from the source deck.

---

## Boundary / non-goals (this workflow)

| In scope | Out of scope (deferred — ADR-0037 §2 决策三) |
|---|---|
| F3a 保真复用 + F3b 逆向重设计, single approval package | Global Step 0 Mode Triage (unify F1/F2/F4 routing) |
| F3c link-out to medical-byo-template | F2「优化现有」 / `optimize-existing-deck` (F2b) |
| De-id gate, Pre-scan crossing | F5 形态转换 documentation |

## Completion

```markdown
## ✅ Reference-Template Generate (F3) Complete
- [x] F3 intent and content source resolved in Final Build Confirmation
- [x] Reuse mode and page mapping accepted in the same gate (F3a / F3b)
- [x] De-identification gate passed
- [x] Medical Pre-scan applied to new content
- [x] Generated via <template-fill | reverse+pipeline> → exports/<name>.pptx
```
