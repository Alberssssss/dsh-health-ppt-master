# @deepseek-ai/dsh-experimental-health-ppt-master

English | [中文](README.zh.md)

Private experimental profile bundle that installs the `health-ppt-master` skill provider and its `agent/pre-step` soft router as one Cordis plugin. The bundle contributes one `health-ppt-master` row, so installation, disablement, reload, and removal apply to both contributions together.

A bundle is a deployment unit, not a complete application context. This pilot proves installation and lifecycle, not Hermes behavior equivalence.

## Installation and lifecycle

Install the tagged, prebuilt bundle into the Web profile:

```sh
dsh plugin --profile web add github:Alberssssss/dsh-health-ppt-master#v0.1.0-rc.8
```

When running dsh from a source checkout, use `pnpm dsh` in place of `dsh`. Restart a running Web app after installation, then verify the layer with `dsh --profile web --dump-config`.

This repository commits the runtime `lib/` files and defines no package lifecycle scripts. GitHub installation does not build the package or ask pnpm to execute package-owned installation code.

To stop both the provider and router without uninstalling the package, add this override to the profile's `cordis.patch.yml`:

```yaml
- id: health-ppt-master
  disabled: true
```

Remove the override, or set `disabled: false`, to start both again. Remove the installed bundle and its layer with:

```sh
dsh plugin --profile web remove @deepseek-ai/dsh-experimental-health-ppt-master
```

The plugin owns no persistent state. Cordis disposal removes the provider registration and router listener; project output remains in the user-selected workspace and is not package state.

## Trial profile isolation

Run lifecycle acceptance in a dedicated `DSH_HOME`. Web sessions receive workspace instructions from the selected agent preset, while the Web host's `agent-instructions` row is disabled. Configure the `agent-instructions` row in the user-owned preset's `agent.cordis.yml` with the complete trial config below so repository `CLAUDE.md` files and local overlays do not enter model context:

```yaml
- id: agent-instructions
  config:
    maxBytes: 65536
    instructionFileCandidates: [AGENTS.md]
    localInstructionFileCandidates: []
```

The bundle does not modify presets and does not include or register `AGENTS.md`, `CLAUDE.md`, or `SOUL.md`. A deployment may supply a scoped `AGENTS.md` for its intended medical or research role; that preset-owned instruction is application context, not skill content.

## Runtime behavior

The immutable provider publishes the packaged `assets/health-ppt-master/` directory as the skill resource base and removes YAML frontmatter before returning the skill body. The runtime assets contain `SKILL.md`, `requirements.txt`, `docs/`, `references/`, `scripts/`, `templates/`, and `workflows/`. Source-checkout projects, tests, `.env.example`, Python caches, credentials, and runtime state are excluded.

The router is a narrow extraction of the Hermes `research-skill-router` presentation route:

- Deck creation, modification, optimization, template reuse, explicit PPT/slide terms, and established presentation deliverables route to `health-ppt-master`.
- Medical or research role markers route only when paired with a presentation deliverable such as a department report, lecture deck, defense, or conference talk.
- Reading, extracting, summarizing, exporting, or converting an existing PPT/PPTX without producing a deck stays outside the route.
- Only text from messages whose source is `user` is inspected. The listener delegates through `next()` and appends its instruction only to an accepted downstream batch; the hint does not prove that the model loaded the skill.

The Hermes router's manuscript routes, project-resume state, output transforms, slash command, and `pre_tool_call` block for a generic `powerpoint` skill are not part of this package.

## External requirements

Discovery and routing are self-contained. Executing the presentation workflow is not self-contained and still requires deployment work for all applicable items below:

- The external `document-parser` dispatcher used for PDF, Office, image, URL, and OCR ingestion.
- Python requirements and system programs such as LibreOffice, Chromium/Playwright, FFmpeg/ffprobe, fonts, and rendering libraries used by the selected workflow.
- Trusted credential injection for image, search, and narration providers. The package contains no `.env` or key and does not rely on parent-process environment inheritance.
- DSH mappings for source-workflow tool names such as `read_file` and `run_in_background`, plus browser reachability and preview-process ownership.
- A DSH workspace/state policy for projects and resumable work. Packaged `projects/` examples and Hermes home paths are not used.
- Product-specific delivery presentation. The Hermes frontend's bare-path parsing and any external output-governance plugin do not accompany this bundle.

Missing external resources do not prevent the plugin from loading. They do prevent a functional-equivalence claim and may block an actual deck workflow at its first unmet prerequisite.

## Model Experience

### Soft router instructions

#### What the model sees

A matching authentic user message adds this durable user-role instruction after downstream pre-step context:

##### Verbatim soft route

```markdown
<health-ppt-master-router>
这是软路由提示，不表示 skill 已加载。本轮用户请求可能要求新建、修改、优化或参照模板生成一份 PPT/deck。采取任务动作前，先调用 `skill` 工具并使用精确名称 `health-ppt-master` 加载完整说明；只有加载后的说明才是执行依据。仅阅读、提取、总结、导出或转换现有 PPT/PPTX 且不产出 deck 时不要使用此 skill。该试点只绑定发现、路由与生命周期，不表示 Hermes 的 Python 依赖、document-parser、浏览器预览、图片提供方或交付治理已经迁移。
</health-ppt-master-router>
```

#### Token effect

Conditional and fixed: one matching pre-step appends the verbatim reminder once. Nonmatching requests and a disabled bundle add no router tokens.

#### KV Cache effect

The appended user-role message preserves the earlier request prefix and extends it at the pre-step insertion point. Enabling, disabling, or changing the fixed reminder changes the prefix from that point onward.

### Bundled skill discovery and load

#### What the model sees

When `@deepseek-ai/dsh-tool-skill` renders this package's registry contribution, the model sees the fixed catalog summary and, after a `skill` tool call, the frontmatter-free instruction body with the packaged resource directory.

#### Token effect

The catalog adds one fixed summary while the bundle is enabled. Loading the skill adds its complete body only in the tool result selected by the model; the large template and script trees are resource paths rather than prompt attachments.

#### KV Cache effect

The catalog preserves the stable prefix for a fixed enabled composition. The loaded body is appended later in the conversation; package content or enablement changes invalidate reuse at their respective insertion points.

## Known Limitations and Deferred Work

- The package is private and experimental; it is available for local profile installation, not an official release dependency.
- The deterministic router is a recommendation, not a dispatcher or proof of skill use; session evidence must distinguish the route hint from the later `skill` tool call.
- This phase does not validate real document ingestion, image generation, preview interaction, editable PPTX export, visual fidelity, medical correctness, output governance, or final-answer parity with Hermes.
- Functional migration requires explicit owners for external tools, credentials, workspace state, browser lifecycle, delivery presentation, and keyless plus real-model deck snapshots.
