---
description: Medical fork — turn a doctor's own hospital/department PPT or logo into a reusable medical deck/brand
---

# Bring-Your-Own Hospital Template Workflow (医生自带模板逆向)

> **Medical fork add-on.** This wraps the upstream [`create-template.md`](./create-template.md) (deck/layout)
> and [`create-brand.md`](./create-brand.md) (identity-only) flows with medical guidance: de-identification,
> where to save, and how the result is reused like a preset. It does **not** re-implement reverse-engineering —
> it routes to the existing creators.

A doctor often already has a hospital / department template (a branded `.pptx`, slide screenshots, or just a
logo + brand colors). Instead of forcing one of the four preset medical decks
(`clinical_report` / `research_academic` / `medical_education` / `institutional_official`), reverse-engineer
**their** asset into a reusable library template, then use it exactly like a preset.

## When to enter this workflow

Triggered from SKILL.md Step 3/4 or the Strategist Medical Scenario Pre-scan when the doctor:
- attaches / points to an existing branded deck ("用我们医院的模板", "这是科室的 PPT 模板", "按这个模板做"), or
- supplies a hospital / department **logo** + brand colors and wants future decks to match.

> **Disambiguate one-off fill vs register-as-preset first.** This workflow exists to **register a reusable asset** (the doctor wants their template available as a preset *for future decks*). If the doctor just wants to **fill this one deck now** from their uploaded `.pptx` + content ("按这个模板生成这次的 ppt / 把讲解词填进这个模板"), that is a one-off — use [`template-fill-pptx.md`](./template-fill-pptx.md) instead (clone the deck's slides + replace text, no registration). Only enter here when reuse across future sessions is the goal.

If the doctor just wants a good-looking medical deck and has no asset of their own → do **not** enter here;
recommend a preset deck from [`../references/medical-scenarios.md`](../references/medical-scenarios.md).

## Decision — deck vs brand

| Output kind | Choose when | Result dir |
|---|---|---|
| **deck** (default) | The doctor wants the *whole look* preserved (their cover/section/content pages, logo, colors) | `templates/decks/<hospital_or_dept>/` |
| **brand** | The doctor only wants identity locked (logo / colors / fonts) but free page layout | `templates/brands/<hospital_or_dept>/` |

Lean **deck** when a real branded `.pptx` or slide images exist; lean **brand** when only a logo + palette are given.
See [`create-template.md`](./create-template.md) "Kind decision" for the full rule.

## Process

1. **Intake.** Identify the source type and hand off to the right creator:
   - Branded `.pptx` → run [`create-template.md`](./create-template.md) (type A; `<skill-dir>/scripts/pptx_template_import.py "<file.pptx>"`), kind **deck**.
   - Slide screenshots / images / PDF pages → [`create-template.md`](./create-template.md) (type C, `standard` mode), kind **deck**.
   - Logo + colors only → [`create-brand.md`](./create-brand.md), kind **brand**.
2. **🩺 De-identify (mandatory before saving).** The source may contain real patient data or example slides.
   When extracting the *template* (identity + structure), **strip all clinical content**: patient names /
   住院号 / 正脸 / real lab values / case specifics must not survive into the reusable asset. The library
   template carries only brand + structure + `{{PLACEHOLDER}}` slots — never baked-in patient data.
3. **Name & save.** Use a stable id (e.g. the hospital or department slug). The creator writes
   `design_spec.md` + SVG roster (+ logo assets for a deck) under `templates/decks/<id>/` or
   `templates/brands/<id>/`, then registers it:
   ```bash
   python3 <skill-dir>/scripts/register_template.py <id> --kind deck    # or --kind brand
   ```
4. **Reuse.** From then on the doctor's template is a first-class preset:
   - explicit path at SKILL.md Step 3 (`templates/decks/<id>/`), or
   - the Strategist may recommend it for matching medical scenarios just like a built-in deck.
   A user-supplied logo can also be fused onto a preset deck (brand wins on identity) — see SKILL.md Step 3
   fusion table.

## Guardrails

- Respects SKILL.md Step 3 discipline: nothing is copied into a project without user confirmation.
- No fabricated clinical data enters the template (step 2 is a hard gate).
- This workflow only **creates / registers** a reusable asset; producing an actual deck still runs the normal
  7-step pipeline with that template selected.
