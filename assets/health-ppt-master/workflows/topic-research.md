---
description: Gather source materials via web search when the user supplies only a topic or requirements without source files. Produces a Markdown document and an image folder that feed SKILL.md Step 2's import-sources.
---

# Topic Research Workflow

> Standalone pre-processing step. Run before SKILL.md Step 1 when the user supplies only a topic or requirements with no source files. Output is a research document + image folder, both shaped to feed `project_manager.py import-sources` directly.

This workflow is **independent**: it owns the source-acquisition step when no file exists; subsequent SKILL.md steps proceed normally with the produced materials as input.

## When to Run

| User-supplied input | Action |
|---|---|
| Topic name only (e.g. "做一个关于宫崎骏的 PPT") | Run this workflow |
| Requirement description without facts (e.g. "介绍我们公司新产品") | Run this workflow |
| ≥1 page of substantive content already in chat | Skip — feed chat content into SKILL.md Step 1 directly |
| Source file attached (PDF / DOCX / URL / Markdown) | Skip — go to SKILL.md Step 1 source converter |

---

## Step 1: Resolve a provisional research scope (NON-BLOCKING)

Do **not** ask the user to confirm topic/scope here. This workflow is preparation for the single
`Final Build Confirmation` in SKILL.md Step 4, not an independent approval gate.

Resolve each field from the user's message; when absent, use the defaults below. Record the result as a
**provisional research scope** and carry it into Step 4's Content Contract so the user sees and can modify it
as part of the one complete confirmation package.

| Item | Default if user did not specify |
|---|---|
| Topic | (from user input) |
| Scope / focus | Broad overview |
| Depth | General-knowledge level |
| Output language | Match user input |
| Slug for files (`<topic_slug>`) | snake_case English identifier derived from topic |

**Forbidden — any confirmation here**: do NOT ask the rows separately or as a bundle. If the topic has
multiple plausible interpretations, gather a broad evidence base covering the leading interpretation and
list the ambiguity + recommended boundary in the Final Build Confirmation. Do not stop before research.

---

## Step 2: Gather via web search

**Tools** — use the web search and web fetch tools the current IDE provides:

| IDE | Web search | Web fetch |
|---|---|---|
| Claude Code | `WebSearch` | `WebFetch` |
| Cursor / Codebuddy / VS Code + Copilot | provider-equivalent built-in | provider-equivalent built-in |
| None available | — | fallback below |

**Fallback when no IDE web tools** — do not open a separate question. Put the missing evidence source in the
Final Build Confirmation as an unresolved required field, recommend that the user attach 2–4 authoritative
URLs (guideline / regulator / official institution / peer-reviewed source), and keep any supplied URLs inside
the same gate's revision loop. Do not start formal generation from unverified remembered medical facts.

```bash
python3 <skill-dir>/scripts/source_to_md/web_to_md.py <URL>
```

**Search strategy**:

| Phase | Action |
|---|---|
| Landscape | One broad search; identify authoritative sources |
| Deep fetch | Pull 2–4 highest-signal pages in full |
| Targeted fill | Search for subtopics the deep fetch flagged |

**Source priority**:

| Tier | Source |
|---|---|
| 1 | Wikipedia / Wikimedia Commons |
| 2 | Official sites, institutional releases |
| 3 | Reputable news / academic articles |
| Avoid | Stock-aggregator watermarked images, social-media reposts without source |

**Stop condition**: stop when gathered material covers overview / history / key aspects / impact / sources with concrete facts and named entities. Endless searching produces noise.

---

## Step 3: Save materials

Two artifacts under `projects/`:

| Artifact | Path |
|---|---|
| Research document | `projects/<topic_slug>.md` |
| Image folder | `projects/<topic_slug>/` |

**Hard rule — naming**: filename (without `.md`) and folder name MUST match. **Hard rule — location**: under `projects/`, never the repository root.

**Document structure** — section layout follows the topic: person → biography / works / impact; technology → background / mechanism / applications / outlook; company → overview / products / market / culture. The file MUST end with a `## Sources` section listing the URLs used.

**Content density** — concrete facts (dates, names, numbers, quotes). Skip filler prose; the Strategist composes final slide copy.

**Images**:

| Decision | Rule |
|---|---|
| Quantity | Cover the deck's likely scenes (cover, key aspects, key entities); the Strategist decides the final cut |
| Resolution | Prefer originals. Wikimedia: strip `/thumb/` and the `Npx-` prefix from the URL to get full resolution |
| License | Wikimedia / public-domain / CC-licensed; avoid stock-aggregator watermarks and unsourced uploads |
| Filename | descriptive English snake_case (`joe_hisaishi_concert.jpg`, not `image1.jpg`) |

```bash
mkdir -p "projects/<topic_slug>"
curl -L -o "projects/<topic_slug>/<descriptive_name>.<ext>" "<image_url>"
```

---

## Hand-off

Output a checkpoint, then continue with the main pipeline. The artifacts feed directly into Step 2's `import-sources`:

```markdown
## ✅ Topic Research Complete
- [x] Document: `projects/<topic_slug>.md` (N sections)
- [x] Images: `projects/<topic_slug>/` (N files)
- [ ] **Next**: SKILL.md Step 2 →
  `project_manager.py init <project_name> --format <format>`
  `project_manager.py import-sources projects/<project_name> projects/<topic_slug>.md projects/<topic_slug>/*.* --move`
```

`<project_name>` is the user's chosen project identifier (typically `<format>_<topic_slug>`, e.g. `ppt169_joe_hisaishi`); `--move` removes the research artifacts from `projects/<topic_slug>` after they are imported.
