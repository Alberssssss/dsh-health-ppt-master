# @deepseek-ai/dsh-experimental-health-ppt-master

[English](README.md) | 中文

私有实验性 profile 组合包，把 `health-ppt-master` skill（技能）提供方及其 `agent/pre-step` 软 router 作为同一个 Cordis 插件安装。该组合包只贡献一个 `health-ppt-master` 配置项，因此安装、停用、重载和移除会同时作用于两项贡献。

Bundle 是部署单元，不是完整应用上下文；本试点证明安装与生命周期，不证明 Hermes 行为等价。

## 安装与生命周期

把带标签的预构建组合包安装到 Web profile：

```sh
dsh plugin --profile web add github:Alberssssss/dsh-health-ppt-master#v0.1.0-rc.8
```

如果从 dsh 源码 checkout 运行，请用 `pnpm dsh` 替代 `dsh`。安装后重启正在运行的 Web 应用，再用 `dsh --profile web --dump-config` 验证配置层。

本仓库提交运行所需的 `lib/` 文件，并且没有定义 package lifecycle script。通过 GitHub 安装时不构建本包，也不会要求 pnpm 执行本包自有的安装代码。

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

不可变提供方把包内 `assets/health-ppt-master/` 目录发布为 skill 资源基底，并在返回 skill 正文前移除 YAML frontmatter。运行资源包含 `SKILL.md`、`requirements.txt`、`docs/`、`references/`、`scripts/`、`templates/` 和 `workflows/`。源码 checkout 的项目、测试、`.env.example`、Python 缓存、凭据和运行状态均被排除。

Router 是从 Hermes `research-skill-router` 的 presentation 路由中提取的窄化版本：

- 新建、修改、优化、套用模板、明确 PPT/slide 词和既定演示交付物会路由到 `health-ppt-master`。
- 医疗或科研角色标记只有与科室汇报、课件、答辩或大会发言等演示交付物共现时才会命中。
- 仅阅读、提取、总结、导出或转换现有 PPT/PPTX 且不产出 deck 的请求不进入本路由。
- Router 只检查来源为 `user` 的文本消息。监听器通过 `next()` 委派，并且只对下游接受的消息批追加指令；该提示不能证明模型已经加载 skill。

Hermes router 中的论文路由、项目恢复状态、输出转换、斜杠命令以及针对通用 `powerpoint` skill 的 `pre_tool_call` 阻断均不属于本包。

## 外部要求

发现与路由是自包含的。演示文稿工作流的执行并不自包含，仍需为下列适用项完成部署工作：

- 用于 PDF、Office、图片、URL 和 OCR 输入的外部 `document-parser` dispatcher（分派器）。
- 所选工作流使用的 Python 依赖，以及 LibreOffice、Chromium/Playwright、FFmpeg/ffprobe、字体和渲染库等系统程序。
- 面向图片、搜索和旁白提供方的可信凭据注入。包内没有 `.env` 或密钥，也不依赖父进程环境继承。
- 把 `read_file`、`run_in_background` 等源工作流工具名映射到 DSH，并处理浏览器可达性和预览进程所有权。
- 面向项目与可续工作的 DSH workspace/state（工作区/状态）策略。包内不使用 `projects/` 示例或 Hermes home 路径。
- 产品特定的交付展示。Hermes 前端的裸路径解析和任何外部输出治理插件均不会随本包迁移。

外部资源缺失不会阻止插件加载，但会阻止功能等价声明，并可能在实际 deck 工作流遇到第一个未满足前置条件时使其停下。

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
- 本阶段不验证真实文档摄取、图片生成、预览交互、可编辑 PPTX 导出、视觉保真、医学正确性、输出治理或 Hermes 最终答案等价。
- 功能迁移仍需为外部工具、凭据、workspace 状态、浏览器生命周期、交付展示以及无密钥和真实模型 deck 快照指定明确 owner（所有者）。
