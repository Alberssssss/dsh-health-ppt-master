# 模板资源

[English](README.md) | 中文

## 设计规范与大纲参考

`design_spec_reference.md` 是用于定义以下内容的一体化参考模板：
1.  **视觉规范**：画布尺寸、配色方案、排版和布局原则
2.  **内容大纲**：逐页规划 slide 结构
3.  **技术约束**：SVG 生成与 PPT 兼容性的硬性要求

[查看设计规范参考](./design_spec_reference.md)

## 页面布局模板

`layouts/` 目录包含按设计风格组织的预制页面布局模板：

- **通用**：用途广泛的现代风格，简洁灵活
- **咨询**：专业且结构化的咨询风格
- **顶级咨询**：顶级咨询风格（MBB 水准）
- **学术答辩**：面向科研的学术答辩风格

- **人工浏览**：[layouts/README.md](./layouts/README.md)
- **精简查询（仅发现）**：[layouts/layouts_index.json](./layouts/layouts_index.json)，用于回答「有哪些模板？」。第 3 步只在用户提供明确目录路径时触发，不会因本索引中的名称触发。

## 品牌标识预设

`brands/` 目录包含仅定义品牌的模板：由色彩、字体、logo、表达语气和图标风格组成的标识包，不含 SVG 页面清单。品牌遵循与布局模板**相同的显式路径触发规则**：在 SKILL.md 第 3 步，用户需要提供要应用的品牌目录路径；只有品牌名称绝不会触发。布局和品牌输入都会进入同一个项目目录（`<project_path>/templates/`）。同时提供两者时，第 3 步会将它们融合为一份 `design_spec.md`（品牌决定标识 token，布局决定页面结构）；优先级表见 `SKILL.md` 第 3 步。

品牌在结构上相当于没有页面清单的布局模板。当用户希望锁定标识但自由设计页面布局时使用品牌；还要求固定页面结构时使用布局模板。

- **人工浏览**：[brands/README.md](./brands/README.md)
- **发现索引（不触发）**：[brands/brands_index.json](./brands/brands_index.json)，用于回答「有哪些品牌？」；第 3 步仍要求用户提供明确目录路径
- **创建工作流**：[`../workflows/create-brand.md`](../workflows/create-brand.md)

## 可视化模板

`charts/` 目录包含 57 个标准化可视化模板。为保持向后兼容，目录名仍为 `charts/`，但范围包括图表、信息图、流程图、关系图、战略框架和系统架构图：

- KPI 卡片
- 条形图／堆叠条形图
- 折线图／双轴折线图
- 环形图
- 雷达图
- 漏斗图
- 矩阵（2x2）
- 时间线
- 甘特图
- 流程
- 组织结构图
- 分层架构／模块组成／带说明辐条的中心辐射图／分阶段流水线／客户端—服务器流程

- **库索引（唯一真源）**：[charts/charts_index.json](./charts/charts_index.json)
- **目录概览**：[charts/README.md](./charts/README.md)

## 图标库

`icons/` 目录包含来自五个库的 11,600 多个矢量图标：

| 图标库 | 风格 | 数量 |
|---------|-------|-------|
| `chunk-filled` | 填充／直线几何 | 640 |
| `tabler-filled` | 填充／贝塞尔曲线形态 | 1000+ |
| `tabler-outline` | 描边／线条 | 5000+ |
| `phosphor-duotone` | 双色调／单色 + 0.2 不透明度底板 | 1200+ |
| `simple-icons` | 品牌 logo（公司／产品标记） | 3400+ |

- **用法与风格规则**：[icons/README.md](./icons/README.md)
- **搜索图标**：`ls skills/ppt-master/templates/icons/<library>/ | grep <keyword>`
