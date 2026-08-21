# SVG 可视化模板库

[English](README.md) | 中文

本目录包含 PPT Master 使用的标准化 SVG 可视化模板，包括图表、信息图、流程图、关系图和战略框架。为保持向后兼容，目录名仍为 `charts/`；模板库的范围比图表更广。

## 真源

[`charts_index.json`](./charts_index.json) 是模板库的唯一真源：包含总数以及每个模板的一条选择规则 `summary`（格式为 `"Pick for X. Skip if Y (use other_key)."`）。人工读者和 AI 角色都会完整读取该文件，不存在按分类／关键词拆分的子索引。选择过程会在一次遍历中根据摘要列表进行语义匹配。

如需浏览模板库，请打开 `charts_index.json` 并从上到下扫描 `charts` 块；每个条目的 `summary` 会直接回答「何时选择这个模板，何时跳过」。

## 风格规则

所有模板必须遵循的配色、字体和 SVG 编写约定见 [`CHART_STYLE_GUIDE.md`](./CHART_STYLE_GUIDE.md)。

## 用法

生成图表页面前，先打开对应的 `<key>.svg` 文件以读取其结构与布局。文件按 `charts_index.json` 中的 `key` 字段命名（例如 `bar_chart.svg`、`quadrant_bubble_scatter.svg`）。模板按视觉结构命名，而不按商业模型命名；SWOT、BCG、PEST、OKR、Porter's Five Forces、Value Chain 等关键词通过每个模板的 `summary` 字段匹配。
