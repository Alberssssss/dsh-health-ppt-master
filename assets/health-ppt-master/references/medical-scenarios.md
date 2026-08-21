# Medical Scenario Playbook Library

> **This is the medical fork's content-injection layer.** It supplies the *standard document
> skeletons* that doctors and clinical/research staff expect — the structures that distinguish a
> hospital-grade deck from a generic one. Strategist reads this file during the Medical Scenario
> Pre-scan (see [`SKILL.md`](../SKILL.md) Step 4 and [`strategist.md`](strategist.md) §0) and uses
> the matched playbook to seed §IX Content Outline, recommend a layout, and pre-select charts.
>
> **How to use a playbook** (Strategist):
> 1. Classify the source / topic into one scenario below (or "no medical match" → fall back to the
>    generic Strategist flow).
> 2. In the Eight Confirmations, recommend the playbook's **outline skeleton** (confirmation c/d),
>    its **preset deck** (name the deck's directory path so the user can accept the template copy; the
>    layout fallback is for when they only want structure), **palette** (confirmation e), and **charts** (§VII).
> 3. The skeleton is a *starting structure*, not a fixed cage — adapt section count and depth to the
>    actual source. Never invent clinical facts to fill a section; mark gaps as "待补充" instead.
>
> **Hard rule — no fabricated medicine.** Doses, lab values, guideline grades, statistics, and
> citations come only from the source material. Do not synthesize plausible-looking clinical data,
> p-values, or references to make a slide look complete. Empty slots stay empty and are flagged.
>
> **Hard rule — figure fidelity (evidence-reproduction decks, esp. `journal_club`, ADR-0048).** When a
> deck reproduces a source paper's own evidence, its figures / tables must be the **original extracted
> images** (`Extracted` status), not redrawn charts or 示意图 — a redrawn chart with correct numbers is
> still lower fidelity than the original. Embedding the original figure is a **mandatory** step; redraw is
> allowed only when no clean original is obtainable, must use the paper's exact reported values verbatim
> (never estimated off a figure), and must be labeled a reconstruction with a source citation.

---

## Preset deck & palette quick map

> **These are finished, ready-to-use decks** — identity + structure + look bundled into one asset, so the
> doctor picks one and fills content. The Pre-scan recommends the matched **deck path**; on confirmation it
> is copied whole into the project (`cp -r templates/decks/<id>/* <project_path>/templates/`). Each row also
> names the lighter structure-only **layout** fallback — use it when the doctor wants only the structure, or
> is bringing their own brand (see *Bring your own template* below).

| Finished deck (preferred) | Path | Palette signature | Scenarios it serves | Layout fallback |
|---|---|---|---|---|
| **clinical_report** | `templates/decks/clinical_report/` | medical blue `#0066B3` + life green `#00A86B` + orange `#FF6B35` accent | clinical case, teaching rounds | `templates/layouts/medical_university/` |
| **research_academic** | `templates/decks/research_academic/` | navy `#1A3A5C` + teal `#0E8C8C`; data-forward, clean | academic conference, journal club, SCI report | `templates/layouts/medical_research/` |
| **medical_education** | `templates/decks/medical_education/` | teaching green `#1F8A5B` + amber `#E8A33D`; friendly, structured | CME / training course | `templates/layouts/medical_university/` |
| **institutional_official** | `templates/decks/institutional_official/` | institutional blue `#13315C` + crimson `#B5121B`; formal, dense | NSFC grant, title-promotion, accreditation / QC, work report, drug/device filing | `templates/layouts/medical_official/` |

Clinical-research charts (use when the scenario calls for them): `templates/charts/survival_curve_km.svg`,
`forest_plot.svg`, `consort_flow.svg`, `roc_curve.svg`.

**Bring your own template**: if the doctor has their own hospital / department deck or logo, reverse-engineer
it into a reusable medical deck / brand via [`workflows/medical-byo-template.md`](../workflows/medical-byo-template.md)
instead of forcing a preset.

---

## 1. clinical_case — 临床病例汇报 / 疑难病例讨论

- **Audience / occasion**: 科室晨会、病例讨论会、MDT、住培病例汇报。
- **Deck (preset)**: `templates/decks/clinical_report/` · fallback layout `medical_university` · **Palette**: medical blue + life green · **Pages**: 12–20.
- **Outline skeleton** (§IX):
  1. 封面 — 病例标题 / 汇报人 / 科室 / 日期
  2. 病例摘要 (one-slide overview：年龄性别、核心诊断、关键转归)
  3. 主诉 & 现病史 (timeline 表达发病经过)
  4. 既往史 / 个人史 / 家族史
  5. 入院查体 (vital signs 数据卡 + 阳性体征)
  6. 辅助检查 — 实验室 (data cards / 表格，标注危急值)
  7. 辅助检查 — 影像 / 病理 (image-text，图随报告)
  8. 初步诊断 & 鉴别诊断 (对比表：支持点 / 不支持点)
  9. 诊疗经过 (timeline / 流程图：治疗方案与调整)
  10. 转归与随访 (before/after，关键指标趋势)
  11. 讨论 / 文献复习 (要点 + 循证证据等级)
  12. 小结 & 致谢
- **Charts**: timeline、data cards (vital signs)、comparison_table (鉴别诊断)、line_chart (指标趋势)。
- **Reminders**: 去标识化 — 不放可识别患者身份的信息 (姓名/住院号/正脸)；危急值用 §XI 的 Critical 标签红色突出。

## 2. teaching_rounds — 教学查房 / 临床带教

- **Audience / occasion**: 住培 / 实习生教学查房、临床思维训练。
- **Deck (preset)**: `templates/decks/clinical_report/` · fallback layout `medical_university` · **Palette**: medical blue + life green · **Pages**: 10–16.
- **Outline skeleton**:
  1. 封面 — 教学主题 / 带教老师 / 层级 (实习/规培/进修)
  2. 教学目标 (knowledge / skill / attitude 三类)
  3. 病例引入 (精简病史，作为思维载体)
  4. 临床思维拆解 (问题导向：如何从主诉推进到诊断)
  5. 鉴别诊断思路 (决策树 / 流程图)
  6. 关键知识点讲授 (1 知识点 1 页)
  7. 循证要点 (指南推荐 + 证据等级)
  8. 操作 / 技能要点 (如适用)
  9. 思考题 & 小结
- **Charts**: flowchart (诊断思维)、framework (知识框架)、comparison_table。
- **Reminders**: 以"问题—推理—结论"驱动，避免直接给答案；区分"教学要点"与"考核点"。

## 3. nsfc_grant — 科研基金标书 / 项目申报汇报

- **Audience / occasion**: NSFC / 省部级 / 院级基金标书答辩、开题报告、中期/结题汇报。
- **Deck (preset)**: `templates/decks/institutional_official/` · fallback layout `medical_official` · **Palette**: institutional blue + crimson accent · **Pages**: 15–25.
- **Outline skeleton** (经典标书逻辑):
  1. 封面 — 项目名称 / 申请人 / 单位 / 申请类别与代码
  2. 立项依据 — 研究意义 + 国内外研究现状 (gap 分析)
  3. 拟解决的关键科学问题
  4. 研究目标 & 研究内容 (objectives ↔ aims 对齐)
  5. 研究方案 & 技术路线 (technical roadmap 流程图 — 核心页)
  6. 创新点 (3 条以内，逐条 claim)
  7. 可行性分析 (理论 / 技术 / 条件三维)
  8. 研究基础 — 前期工作 & 预实验数据 (放 KM / forest / ROC 等支撑图)
  9. 工作条件 & 团队
  10. 研究计划进度 (gantt)
  11. 预期成果 & 考核指标
  12. 经费预算概要 (如需)
- **Charts**: `consort_flow` / `survival_curve_km` / `forest_plot` / `roc_curve` (前期数据)、gantt (进度)、framework (技术路线)、hub_spoke (科学问题分解)。
- **Reminders**: 技术路线图是评审重点，单独整页；创新点用"相比现有研究…本项目首次…"句式；前期数据图必须来自申请人自己的工作，注明来源。

## 4. academic_conference — 学术大会发言 / SCI 成果汇报

- **Audience / occasion**: 学术年会发言、口头报告 (oral)、成果路演。
- **Deck (preset)**: `templates/decks/research_academic/` · fallback layout `medical_research` · **Palette**: navy + teal · **Pages**: 10–15 (口头报告控制在 ~1 页/分钟)。
- **Outline skeleton** (IMRaD-derived):
  1. 封面 — 题目 / 作者与单位 / 会议名
  2. Background & 研究空白
  3. Objective / Hypothesis
  4. Methods — 设计 / 人群 / 干预 / 终点 (放 `consort_flow` 入组流程)
  5. Results — 主要结局 (放 `survival_curve_km` / `forest_plot` / `roc_curve`)
  6. Results — 次要结局 / 亚组
  7. Discussion — 解读 + 与既往研究比较
  8. Limitations
  9. Conclusion (one-sentence take-home)
  10. 致谢 & 利益冲突声明
- **Charts**: `survival_curve_km`、`forest_plot`、`roc_curve`、`consort_flow`、kpi_cards (主要终点)。
- **Reminders**: 一页一信息；结论先行 (take-home message 放标题)；必须有 limitations 与 disclosure 页。

## 5. journal_club — 文献汇报 / Journal Club

> **本场景第一纪律 = 忠于原文证据（ADR-0048）。** journal_club 不是"论文摘要的可视化"，而是建立在**忠实复现论文自身证据**之上的一次可辩护的批判性评价。一切围绕原文原始信息构建；汇报人可做更高层的分析 / 评价，但所呈现的每个数据点、每张图表都必须出自论文本身。

- **Audience / occasion**: 科室文献学习、循证读书报告。
- **Deck (preset)**: `templates/decks/research_academic/` · fallback layout `medical_research` · **Palette**: navy + teal · **Pages**: 12–16（评价类页占重心，见下）。
- **交互（ADR-0049，仅 journal_club）**: 命中后先跑 [`strategist.md §0.1` clarify 脊柱](./strategist.md)——一轮轻量澄清（≤5 lever：受众&场景 / 时长页数 / 汇报重心 / **必嵌原图表清单** / 延展开关），每项给推荐默认+理由，开场已答的不再问；答案喂进 Eight-Confirmations bundle 做**唯一一次大纲确认**，确认后一气呵成。lever④ 的必嵌清单 = 下面逐图保真闸的目标集。
- **图表保真（必经流程，硬要求）**:
  - 结果 / 图表页 **必须嵌入原文原图**：来自 document-parser 抽取的 `Extracted` 图（`sources/<stem>_files/*.png` → 传播进 `images/`，§VIII 标 `Acquire Via: source` / `no-crop`），逐像素嵌入、不裁。
  - 抽取残缺 / 漏抽 / 边界错时，走 [`../references/executor-base.md` §6 的 render-crop 路径](../references/executor-base.md)：`render_pdf_region.py --detect-figure --caption "Figure N"` 确定性定界（unions 页内 drawings + 关联文本，**无需 vision**）→ 按打印的 `--frac` 裁 → `--verify-crop` 校验 PASS 才用。**禁止**用裸 `fitz.get_text()` 之类脚本自读。
  - **重绘不禁止，但必须严谨零误差**：仅当确实拿不到干净原图时才重绘，且必须用原文**精确报告值**（效应量 / 95%CI / P 值 / 事件数 / 风险人数表——**不许眼估读曲线**），对照原图校准，并在页面显式标注"据原文数据重绘 / reconstructed from source data"、注明图号与出处。重绘数值若靠估计 / 编造 = 保真违规。
- **Outline skeleton**（描述性复现服务于评价，不喧宾夺主）:
  1. 封面 — 文献标题 / 期刊与影响因子 / 汇报人
  2. 选题背景 — 为什么读这篇 (临床问题 PICO)
  3. 研究问题 & 假设
  4. 研究方法 (设计类型、样本量、统计方法)
  5. 主要结果 — **嵌入原文关键图表原图**（Figure/Table 原图，非重绘）；效应量 / CI / P 值逐字照搬
  6. 作者结论（仅陈述原文声称，一句话；与后续汇报人评价严格区分）
  7. **批判性评价① 内部效度** — 随机化 / 分配隐藏 / 盲法 / 失访 / 混杂；偏倚风险 (RoB2 / CASP / NOS)
  8. **批判性评价② 统计合理性** — 效应量与 CI 解读、多重比较、检验效能、结果是否真正支撑结论
  9. **批判性评价③ 外部效度 & 可推广性** — 人群 / 场景 / 干预对本院本科室的可迁移性
  9.5 **（可选，clarify lever⑤=加 时才出）本研究 vs 既往 AS 队列对比** — `comparison_table`（如 ProtecT / PRIAS / Klotz / Tosoian）；把本文放进证据脉络里做延展评价。**数值只能来自本文自身引用 / 正文报告的既往队列数字**；本文未报告的格标"未报告 / 待核"，绝不臆造。需要更硬的核验时，可选联网走 `skills/health/med-online-kb` + `skills/research/citation-management`（仅 lever⑤ 且用户同意联网），每个数字标出处。此页是二次分析表、**非重绘源图**，不触保真闸。
  10. 证据等级 & GRADE 评定
  11. 对临床实践的启示 (能否改变我的实践？)
  12. 小结 & 讨论问题
- **重心**: §7–§11（批判性评价 + GRADE + 临床启示）是本套灵魂，应占**全套 ≥ 半数页数**。骨架是起点不是牢笼，按原文实际调整页数。
- **Charts（仅作兜底 / 二次分析，不得替代原文图）**: `forest_plot`（**仅当**原文无法提取原图而须重绘、或汇报人自己做 meta 合并）、`comparison_table`（本研究 vs 既往——即上面**可选的 9.5 对比页**的归宿，属二次分析表、非重绘源图）、`framework`（PICO / CASP 核查表）。原文本身是森林图 / KM 曲线时 → 嵌原图，不要用模板重画。
- **Reminders**:
  1. **图表保真第一 + 逐图完整性确认闸（确定性优先）**：结果图表必须是原文原图（`Extracted`），绝不用 chart 模板重绘或 AI 示意图替代原图。**每张原图嵌入前必须用 `render_pdf_region.py --verify-crop` 确认是完整图（coverage≥92% + caption 在框内），FRAGMENT 则用 `--detect-figure` 的坐标 render-crop 重取再校验**（见 [`../references/executor-base.md` §6 强制门](../references/executor-base.md)）。本部署主模型多无会话内 vision，**"看图"不是门**——`--verify-crop` PASS 才是门，vision 仅在可用时作可选交叉核对（ADR-0050）。抽取不净先 render-crop，重绘是最后手段且须标注。原图按**原生比例**定 box、不裁、不塞进固定槽（信箱化=缺陷，`svg_quality_checker.py` 现会 warn）。
  2. **效应量照搬**：HR/OR/RR、95%CI、P 值、绝对 / 相对风险差逐字取自原文，不重算、不估读。
  3. **重心在评价**：批判性评价 + GRADE + 临床启示是灵魂，不能只复述原文。
  4. 严格区分"作者结论"与"汇报人评价"；每张原文图表标注来源（Fig/Table 号 + 引用）。
  5. **讲稿数值保真**：`notes/` 里念出的每个数字必须 **== 页面正面数字 == 原文**；拼成中文口播时**不得改变量级**（"21 例"→"二十一例"，**不是**"二十一万"）。见 [`../references/executor-base.md` §8](../references/executor-base.md)。

## 6. cme_course — 继续教育 / 培训课件

- **Audience / occasion**: 继续医学教育 (CME)、进修培训、科普讲座的专业版。
- **Deck (preset)**: `templates/decks/medical_education/` · fallback layout `medical_university` · **Palette**: teaching green + amber · **Pages**: 15–30。
- **Outline skeleton**:
  1. 封面 — 课程名 / 讲者 / 学分信息
  2. 学习目标 (可测量的 objectives)
  3. 课程大纲 (toc)
  4–N. 分节讲授 (每节：要点 → 图示 → 案例 → 小结)
  N+1. 常见误区 / 易错点
  N+2. 要点总结 (takeaways)
  N+3. 自测题 / 互动
  N+4. 参考文献 & 致谢
- **Charts**: framework、flowchart、comparison_table、icon_grid。
- **Reminders**: 每节有明确小结；适当互动页 (思考题)；区分专业 CME 与公众科普的深度。

## 7. title_promotion — 职称晋升 / 科技奖申报汇报

- **Audience / occasion**: 高级职称答辩、科技奖 (省部级/学会) 申报、人才项目汇报。
- **Deck (preset)**: `templates/decks/institutional_official/` · fallback layout `medical_official` · **Palette**: institutional blue + crimson accent · **Pages**: 12–20。
- **Outline skeleton**:
  1. 封面 — 姓名 / 申报职称或奖项 / 单位
  2. 个人概况 & 任职以来总体情况
  3. 临床工作业绩 (工作量、疑难/危重、新技术、kpi_cards)
  4. 教学工作 (带教、课程、教改)
  5. 科研成果 (课题、论文、专利 — 用表格 + 代表作高亮)
  6. 代表性成果详述 (1–3 项，逐项 impact)
  7. 社会服务 / 学术兼职 / 获奖
  8. 下一步规划
  9. 小结
- **Charts**: kpi_cards (业绩量化)、bar_chart (逐年趋势)、comparison_table、financial_statement_table (成果清单)。
- **Reminders**: 量化优先 (数字 + 同行/院内对比)；代表作突出而非堆砌；如实陈述，可核查。

## 8. hospital_accreditation — 学科/等级评审 · 质控 · 工作汇报

- **Audience / occasion**: 等级医院评审、学科评估、质控汇报、年度/季度工作汇报。
- **Deck (preset)**: `templates/decks/institutional_official/` · fallback layout `medical_official` · **Palette**: institutional blue + crimson accent · **Pages**: 15–25。
- **Outline skeleton**:
  1. 封面 — 汇报主题 / 科室或医院 / 周期
  2. 总体概况 (规模、定位、一句话成绩)
  3. 关键指标现状 (kpi_cards / 仪表盘：质量/安全/效率指标)
  4. 对标与差距 (本期 vs 上期 vs 标杆)
  5. 主要举措 (按主题分块：流程/质控/学科建设)
  6. 成效 (举措 → 数据改善，before/after)
  7. 存在问题 & 整改
  8. 下一步规划 (gantt / roadmap)
  9. 小结
- **Charts**: kpi_cards、bar_chart / line_chart (指标趋势)、gauge_chart (达标率)、gantt (规划)、comparison_table (对标)。
- **Reminders**: 指标对照评审标准条款；数据可溯源；问题页要实事求是，配整改措施。

## 9. drug_device_filing — 药品/医疗器械注册申报汇报 (NMPA)

- **Audience / occasion**: NMPA 注册沟通会、内部注册策略评审、临床试验方案汇报。
- **Deck (preset)**: `templates/decks/institutional_official/` · fallback layout `medical_official` · **Palette**: institutional blue + crimson accent · **Pages**: 15–25。
- **Outline skeleton**:
  1. 封面 — 产品名 / 申报类别 / 申报单位
  2. 产品概述 (适应症 / 作用机制 / 分类)
  3. 立题依据 & 临床需求 (未满足的医疗需求)
  4. 临床前研究概要 (药学/毒理 或 性能/生物相容性)
  5. 临床试验设计 (放 `consort_flow` 入组与分析流程)
  6. 有效性结果 (放 `survival_curve_km` / `forest_plot` / `roc_curve`)
  7. 安全性结果 (不良事件表)
  8. 获益—风险评估
  9. 监管路径 & 申报策略 (技术审评要点、参照法规)
  10. 合规声明 & 后续计划
- **Charts**: `consort_flow`、`survival_curve_km`、`forest_plot`、`roc_curve`、comparison_table (与对照/已上市产品)、kpi_cards (主要终点)。
- **Reminders**: 区分"已完成数据"与"计划数据"；引用具体法规/指导原则条款 (来自源材料)；不夸大有效性、不弱化安全性；GxP/合规口径以源材料为准。

---

## Fallback

If the source does not match any scenario above (e.g. a general health science article, a department
budget memo, a non-medical topic), do **not** force-fit a playbook. Drop back to the generic Strategist
flow and treat it as free design. Routing a non-medical deck here is a soft error — note it and proceed
generically rather than imposing a clinical skeleton.
