# @deepseek-ai/dsh-experimental-health-ppt-master

[English](README.md) | 中文

私有实验性 profile 组合包，把 `health-ppt-master` skill（技能）提供方及其 `agent/pre-step` 软 router 作为同一个 Cordis 插件安装。该组合包只贡献一个 `health-ppt-master` 配置项，因此安装、停用、重载和移除会同时作用于两项贡献。仓库同时包含可审计源码、独立测试、自包含 Git 构建和已提交的运行产物。

Bundle 是部署单元，不是完整应用上下文；本试点证明安装与生命周期，不证明 Hermes 行为等价。

## 安装与生命周期

通过 HTTPS 把带标签的预构建组合包安装到 Web profile。该命令直接使用已提交的运行文件，不需要授予安装期构建权限，因此是推荐的一行安装方式：

```sh
dsh plugin --profile web add --fetch-timeout=300000 https://codeload.github.com/Alberssssss/dsh-health-ppt-master/tar.gz/refs/tags/v0.1.0-rc.10
```

如果从 dsh 源码 checkout 运行，请用 `pnpm dsh` 替代 `dsh`。安装后重启正在运行的 Web 应用，再用 `dsh --profile web --dump-config` 验证配置层。

固定标签的 GitHub 归档使用 HTTPS；显式设置五分钟下载超时后，慢速链路无需依赖 Git 或 SSH 传输也能完成。本仓库提交运行所需的 `lib/` 文件，因此归档安装不需要编译 TypeScript。

本仓库也是可自构建的 Git 包。直接 Git 安装会通过 `prepare` 脚本从 `src/` 构建，因此 pnpm 11 要求 allowlist 键包含确切的 Git URL 和 commit（提交）。请把两个 `<commit>` 替换成同一个受信任发布提交：

```sh
dsh plugin --profile web add --fetch-timeout=300000 --allow-build='@deepseek-ai/dsh-experimental-health-ppt-master@git+https://github.com/Alberssssss/dsh-health-ppt-master.git#<commit>' 'git+https://github.com/Alberssssss/dsh-health-ppt-master.git#<commit>'
```

Git 命令有意固定不可变提交。该构建授权允许仓库代码在安装期间于 agent 沙箱之外的宿主机执行；除非明确需要从源码重建，否则应使用预构建归档。

pnpm 会把该源码构建授权的精确值写入 profile 的 `pnpm-workspace.yaml`。移除包会删除插件及 bundle 配置项，但不会删除这条信任记录。如果源码构建试用结束后需要让 profile 恢复到安装前状态，请只删除匹配的 `allowBuilds` 配置项，再在 profile 目录运行 `pnpm install`。推荐的预构建归档不会产生构建授权记录。

如果要保留安装但同时停止提供方和 router，请把以下覆盖项加入 profile 的 `cordis.patch.yml`：

```yaml
- id: health-ppt-master
  disabled: true
```

删除该覆盖项或设置 `disabled: false`，即可重新启动两者。使用以下命令移除已安装的组合包及其配置层：

```sh
dsh plugin --profile web remove @deepseek-ai/dsh-experimental-health-ppt-master
```

该插件不拥有持久状态。Cordis dispose（资源释放）会移除提供方注册与 router 监听器；项目产物保留在用户选择的 workspace 中，不属于包状态。

## 源码与验证

仓库在安装时使用的预构建 `lib/` 之外，同时保留可审计的 TypeScript 源码、测试和 `tsconfig.json`。源码发生变化时，发布前必须同步更新并验证对应的预构建文件。

使用 Node 22.19 或更高版本以及 pnpm 11 运行独立源码检查：

```sh
pnpm install --frozen-lockfile
pnpm build
pnpm typecheck
pnpm test
pnpm test:coverage
```

`prepare` 脚本通过专用 tsdown 配置和声明文件构建直接处理本仓库源码，不使用项目引用、不假设相邻 checkout，也不包含 `workspace:` 依赖声明。测试覆盖提供方注册与释放、路由正反例、真实用户消息过滤、waterfall 拒绝与中止行为、Loader 导出处理、该包自有的会话 invariant、分发元数据和运行时预检行为。

安装后可用以下命令检查本机能力；输出不会包含凭据值：

```sh
dsh plugin --profile web exec dsh-health-ppt-master-doctor --json
```

## 试点 profile 隔离

使用独立 `DSH_HOME` 运行生命周期验收。Web 会话从所选 agent preset 获取工作区指令，而 Web host 的 `agent-instructions` 配置项处于停用状态。用下面的完整试点配置覆盖用户自有 preset 的 `agent.cordis.yml` 中的 `agent-instructions` 配置项，防止仓库 `CLAUDE.md` 和本地 overlay 进入模型上下文：

```yaml
- id: agent-instructions
  config:
    maxBytes: 65536
    instructionFileCandidates: [AGENTS.md]
    localInstructionFileCandidates: []
```

该组合包不修改 preset，也不包含或注册 `AGENTS.md`、`CLAUDE.md` 或 `SOUL.md`。部署可以为预期医疗或科研角色提供 scoped（限定作用域的）`AGENTS.md`；该 preset 自有指令属于应用上下文，不属于 skill 内容。

## 运行时行为

不可变提供方把包内 `assets/health-ppt-master/` 目录发布为 skill 资源基底，并在返回 skill 正文前移除 YAML frontmatter。运行资源包含 `SKILL.md`、`requirements-core.txt`、`requirements.txt`、`docs/`、`references/`、`scripts/`、`templates/` 和 `workflows/`。源码 checkout 的项目、测试、`.env.example`、Python 缓存、凭据和运行状态均被排除。

Router 是从 Hermes `research-skill-router` 的 presentation 路由中提取的窄化版本：

- 新建、修改、优化、套用模板、明确 PPT/slide 词和既定演示交付物会路由到 `health-ppt-master`。
- 医疗或科研角色标记只有与科室汇报、课件、答辩或大会发言等演示交付物共现时才会命中。
- 仅阅读、提取、总结、导出或转换现有 PPT/PPTX 且不产出 deck 的请求不进入本路由。
- Router 只检查来源为 `user` 的文本消息。监听器通过 `next()` 委派，并且只对下游接受的消息批追加指令；该提示不能证明模型已经加载 skill。

Hermes router 中的论文路由、项目恢复状态、输出转换、斜杠命令以及针对通用 `powerpoint` skill 的 `pre_tool_call` 阻断均不属于本包。

## 外部要求

发现、路由、skill 加载、预检、项目初始化、质量检查以及本地 SVG 到可编辑 PPTX 路径均已打包。核心导出路径需要 Python 3 和 `requirements-core.txt` 中的包；只有当前 DSH 权限策略允许时，skill 才会把这些依赖安装到 workspace 自有虚拟环境，绝不会修改包目录或宿主全局 Python 环境。

只需检查所选工作流实际使用的能力。以下功能仍需要插件之外的部署资源：

- 用于 PDF、Office、图片、URL 和 OCR 输入的外部 `document-parser` dispatcher（分派器）。
- 所选工作流使用的可选 Python 依赖，以及 LibreOffice、Playwright Chromium 浏览器、FFmpeg/ffprobe、字体和渲染库等系统程序。
- 面向图片、搜索和旁白提供方的可信凭据注入。包内没有 `.env` 或密钥，也不依赖父进程环境继承。
- 把 `read_file`、`run_in_background` 等源工作流工具名映射到 DSH，并处理浏览器可达性和预览进程所有权。
- 面向项目与可续工作的 DSH workspace/state（工作区/状态）策略。包内不使用 `projects/` 示例或 Hermes home 路径。
- 产品特定的交付展示。Hermes 前端的裸路径解析和任何外部输出治理插件均不会随本包迁移。

可选外部资源缺失不会阻止插件或核心导出路径加载。包内预检只会让所选工作流显式要求的能力组失败，并指出缺失的模块、程序或路径。外部资源仍会阻止完整 Hermes 等价声明。

## 模型体验

### 软 router 指令

#### 模型看到什么

真实用户消息命中时，系统会在下游步骤前上下文之后追加以下持久用户角色指令：

##### 软路由逐字文本

```markdown
<health-ppt-master-router>
这是软路由提示，不表示 skill 已加载。本轮用户请求可能要求新建、修改、优化或参照模板生成一份 PPT/deck。采取任务动作前，先调用 `skill` 工具并使用精确名称 `health-ppt-master` 加载完整说明；只有加载后的说明才是执行依据。仅阅读、提取、总结、导出或转换现有 PPT/PPTX 且不产出 deck 时不要使用此 skill。该试点只绑定发现、路由与生命周期，不表示 Hermes 的 Python 依赖、document-parser、浏览器预览、图片提供方或交付治理已经迁移。
</health-ppt-master-router>
```

#### Token 影响

影响有条件且固定：每个命中的步骤前阶段会追加一次上述逐字提醒。请求未命中或组合包被停用时，不增加 router token。

#### KV Cache 影响

追加的用户角色消息保留更早的请求前缀，并在步骤前插入点扩展该前缀。启用、停用或修改固定提醒会从该位置起改变前缀。

### 组合包内 skill 的发现与加载

#### 模型看到什么

当 `@deepseek-ai/dsh-tool-skill` 渲染本包的注册项时，模型会看到固定目录摘要；调用 `skill` 工具后，还会看到已移除 frontmatter 的指令正文与包内资源目录。

#### Token 影响

组合包启用时，目录增加一条固定摘要。只有模型选择加载该 skill 时，其完整正文才会进入工具结果；大型模板和脚本树以资源路径存在，不作为 prompt（提示词）附件进入上下文。

#### KV Cache 影响

在启用状态固定时，目录保持稳定前缀。加载后的正文在会话后部追加；包内容或启用状态变化会分别从对应插入点起使缓存不可复用。

## 已知限制与延后工作

- 本包为私有实验性包，只支持安装到本地 profile，不属于正式发布依赖。
- 确定性 router 只提供建议，不是 dispatcher，也不能证明 skill 已被使用；会话证据必须区分路由提示与后续 `skill` 工具调用。
- 本包不会让文档摄取、图片生成、浏览器预览、旁白、LibreOffice 转换、供应商凭据、医学正确性、输出治理或最终答案行为变成自包含能力。
- 核心可编辑 PPTX 导出会独立测试；完整视觉保真和真实模型 deck 质量仍需代表性源文档、渲染页对比和应用级快照。
- 完整 Hermes 等价仍需为外部工具、凭据、workspace 状态、浏览器生命周期和交付展示指定明确 owner（所有者）。
