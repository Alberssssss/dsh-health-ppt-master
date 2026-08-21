# @deepseek-ai/dsh-experimental-health-ppt-master

English | [中文](README.zh.md)

Private experimental profile bundle that installs the `health-ppt-master` skill provider and its `agent/pre-step` soft router as one Cordis plugin. The bundle contributes one `health-ppt-master` row, so installation, disablement, reload, and removal apply to both contributions together. The repository contains auditable source, standalone tests, a self-contained Git build, and committed runtime artifacts.

A bundle is a deployment unit, not a complete application context. This pilot proves installation and lifecycle, not Hermes behavior equivalence.

## Installation and lifecycle

Install the tagged, prebuilt bundle into the Web profile over HTTPS. This is the recommended one-line path because it uses the committed runtime files and requires no install-time build permission:

```sh
dsh plugin --profile web add --fetch-timeout=300000 https://codeload.github.com/Alberssssss/dsh-health-ppt-master/tar.gz/refs/tags/v0.1.0-rc.10
```

When running dsh from a source checkout, use `pnpm dsh` in place of `dsh`. Restart a running Web app after installation, then verify the layer with `dsh --profile web --dump-config`.

The fixed-tag GitHub archive uses HTTPS and the explicit five-minute fetch timeout accommodates slow links without relying on Git or SSH transport. This repository commits the runtime `lib/` files, so archive installation does not need to compile TypeScript.

The repository is also a self-building Git package. A direct Git install runs its `prepare` script from `src/`. pnpm 11 resolves the GitHub dependency through codeload and keys the build permission by that canonical tarball URL, while the dependency argument remains the pinned Git URL. Replace both `<commit>` values with the same trusted release commit:

```sh
dsh plugin --profile web add --fetch-timeout=300000 --allow-build='@deepseek-ai/dsh-experimental-health-ppt-master@https://codeload.github.com/Alberssssss/dsh-health-ppt-master/tar.gz/<commit>' 'git+https://github.com/Alberssssss/dsh-health-ppt-master.git#<commit>'
```

The Git command deliberately pins an immutable commit. Its build permission allows repository code to execute on the host during installation, outside the agent sandbox; use the prebuilt archive unless source rebuilding is specifically required.

pnpm stores that exact source-build permission in the profile's `pnpm-workspace.yaml`. Removing the package removes the plugin and bundle row but does not remove this trust record. After a source-build trial, delete only the matching `allowBuilds` entry and run `pnpm install` in the profile directory if the profile must return to its pre-install state. The recommended prebuilt archive creates no build-permission record.

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

## Source and validation

The repository keeps the auditable TypeScript source, tests, and `tsconfig.json` beside the prebuilt `lib/` used at installation time. A source change must update and validate the corresponding prebuilt files before release.

Run the standalone source checks with Node 22.19 or later and pnpm 11:

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm typecheck
pnpm test
pnpm test:coverage
```

The `prepare` script invokes a dedicated tsdown configuration and declaration build directly from this repository. It has no project references, sibling checkout assumptions, or `workspace:` dependency specifiers. The tests exercise provider registration and disposal, positive and negative routing, authentic-message filtering, waterfall rejection and abort behavior, Loader export handling, the package-owned session invariant, distribution metadata, and runtime preflight behavior.

After installation, inspect local capabilities without printing credential values:

```sh
dsh plugin --profile web exec dsh-health-ppt-master-doctor --json
```

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

The immutable provider publishes the packaged `assets/health-ppt-master/` directory as the skill resource base and removes YAML frontmatter before returning the skill body. The runtime assets contain `SKILL.md`, `requirements-core.txt`, `requirements.txt`, `docs/`, `references/`, `scripts/`, `templates/`, and `workflows/`. Source-checkout projects, tests, `.env.example`, Python caches, credentials, and runtime state are excluded.

The router is a narrow extraction of the Hermes `research-skill-router` presentation route:

- Deck creation, modification, optimization, template reuse, explicit PPT/slide terms, and established presentation deliverables route to `health-ppt-master`.
- Medical or research role markers route only when paired with a presentation deliverable such as a department report, lecture deck, defense, or conference talk.
- Reading, extracting, summarizing, exporting, or converting an existing PPT/PPTX without producing a deck stays outside the route.
- Only text from messages whose source is `user` is inspected. The listener delegates through `next()` and appends its instruction only to an accepted downstream batch; the hint does not prove that the model loaded the skill.

The Hermes router's manuscript routes, project-resume state, output transforms, slash command, and `pre_tool_call` block for a generic `powerpoint` skill are not part of this package.

## External requirements

Discovery, routing, skill loading, preflight, project initialization, quality checking, and the local SVG-to-editable-PPTX path are packaged. The core export path requires Python 3 plus the packages in `requirements-core.txt`; the skill installs them only into a workspace-owned virtual environment when the active DSH permission policy allows it. It never modifies the package directory or host-global Python installation.

Run only the capability checks required by the selected workflow. The following features still require deployment resources outside the plugin:

- The external `document-parser` dispatcher used for PDF, Office, image, URL, and OCR ingestion.
- Optional Python requirements and system programs such as LibreOffice, a Playwright Chromium browser, FFmpeg/ffprobe, fonts, and rendering libraries used by the selected workflow.
- Trusted credential injection for image, search, and narration providers. The package contains no `.env` or key and does not rely on parent-process environment inheritance.
- DSH mappings for source-workflow tool names such as `read_file` and `run_in_background`, plus browser reachability and preview-process ownership.
- A DSH workspace/state policy for projects and resumable work. Packaged `projects/` examples and Hermes home paths are not used.
- Product-specific delivery presentation. The Hermes frontend's bare-path parsing and any external output-governance plugin do not accompany this bundle.

Missing optional resources do not prevent the plugin or core export path from loading. The packaged preflight fails only groups explicitly required for the selected workflow and names the missing module, program, or path. External resources still prevent a complete Hermes-equivalence claim.

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
- The package does not make document ingestion, image generation, browser preview, narration, LibreOffice conversion, provider credentials, medical correctness, output governance, or final-answer behavior self-contained.
- Core editable PPTX export is tested independently; complete visual fidelity and real-model deck quality still require representative source documents, rendered-slide comparison, and application-level snapshots.
- Full Hermes equivalence requires explicit owners for external tools, credentials, workspace state, browser lifecycle, and delivery presentation.
