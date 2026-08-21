# PPT Master 工具集

[English](README.md) | 中文

本目录包含面向用户的脚本，用于格式转换、项目初始化、直接填充 PPTX 模板、处理 SVG、导出、录制旁白和生成图片。

## 目录布局

- 顶层 `scripts/`：可直接运行的入口脚本
- `scripts/source_to_md/`：源文档 → Markdown 转换器（`pdf_to_md.py`、`doc_to_md.py`、`excel_to_md.py`、`ppt_to_md.py`、`web_to_md.py`）
- `scripts/image_backends/`：供 `image_gen.py` 使用的内部提供方实现
- `scripts/tts_backends/`：供 `notes_to_audio.py` 使用的内部 TTS 提供方实现
- `scripts/template_import/`：供 `pptx_template_import.py` 使用的内部 PPTX 参考准备辅助程序
- `scripts/svg_finalize/`：供 `finalize_svg.py` 使用的内部后处理辅助程序
- `scripts/docs/`：按主题组织的脚本文档
- `scripts/assets/`：脚本使用的静态资源

## 快速开始

典型的端到端工作流：

```bash
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
# or
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/project_manager.py init <project_name> --format ppt169
python3 scripts/project_manager.py import-sources <project_path> <source_files...> --move
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/animation_config.py scaffold <project_path>  # optional object-level animation overrides
python3 scripts/svg_to_pptx.py <project_path>
```

更新仓库：

```bash
python3 scripts/update_repo.py
```

## 脚本索引

| 领域 | 主要脚本 | 文档 |
|------|-----------------|---------------|
| 格式转换 | `source_to_md/pdf_to_md.py`、`source_to_md/doc_to_md.py`、`source_to_md/excel_to_md.py`、`source_to_md/ppt_to_md.py`、`source_to_md/web_to_md.py` | [格式转换](./docs/conversion.md) |
| 项目管理 | `project_manager.py`、`batch_validate.py`、`generate_examples_index.py`、`error_helper.py`、`pptx_template_import.py`、`template_fill_pptx.py` | [项目](./docs/project.md) |
| SVG 流水线 | `finalize_svg.py`、`svg_to_pptx.py`、`total_md_split.py`、`svg_quality_checker.py`、`animation_config.py`、`notes_to_audio.py` | [SVG 流水线](./docs/svg-pipeline.md) |
| 规范维护 | `update_spec.py` | [更新规范](./docs/update_spec.md) |
| 图片工具 | `image_gen.py`、`latex_render.py`、`analyze_images.py`、`gemini_watermark_remover.py` | [图片](./docs/image.md) |
| 仓库维护 | `update_repo.py` | README 的安装／更新章节 |
| 故障排查 | 校验、预览、导出和依赖问题 | [故障排查](./docs/troubleshooting.md) |

## 高频命令

格式转换：

```bash
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/doc_to_md.py <file.docx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/source_to_md/web_to_md.py <url>
```

项目初始化：

```bash
python3 scripts/project_manager.py init <project_name> --format ppt169
python3 scripts/project_manager.py import-sources <project_path> <source_files...> --move
python3 scripts/project_manager.py validate <project_path>
```

导入模板源文件：

```bash
python3 scripts/pptx_template_import.py <template.pptx>
python3 scripts/pptx_template_import.py <template.pptx> --manifest-only
python3 scripts/pptx_template_import.py <template.pptx> --inheritance-mode both
```

填充模板（直接处理 PPTX，不转换 SVG）：

```bash
mkdir -p <project_path>/sources <project_path>/analysis <project_path>/exports <project_path>/validation
python3 scripts/template_fill_pptx.py analyze <project_path>/sources/<source.pptx> -o <project_path>/analysis/slide_library.json
python3 scripts/template_fill_pptx.py scaffold <project_path>/analysis/slide_library.json -o <project_path>/analysis/fill_plan.json --slides "1,3,4"
python3 scripts/template_fill_pptx.py check-plan <project_path>/analysis/slide_library.json <project_path>/analysis/fill_plan.json -o <project_path>/analysis/check_report.json
python3 scripts/template_fill_pptx.py apply <project_path>/sources/<source.pptx> <project_path>/analysis/fill_plan.json -o <project_path>/exports/filled.pptx
```

除非输出文件 stem 已以时间戳结尾，否则 `apply` 会自动写入 `filled_YYYYMMDD_HHMMSS.pptx`。默认应用 `fade` 页面切换效果；`--transition <effect>`（fade/push/wipe/split/strips/cover/random，`--transition-duration` 以秒为单位）可更改效果，`--transition none` 会移除效果，`--transition keep` 会保留源文件的切换效果，计划中的逐页 `transition` 字段会覆盖 CLI 选择。

后处理与导出：

```bash
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/svg_to_pptx.py <project_path>
```

图片生成：

```bash
python3 scripts/latex_render.py <project_path>
python3 scripts/latex_render.py <project_path> --providers codecogs,quicklatex,mathpad,wikimedia
python3 scripts/image_gen.py "A modern futuristic workspace"
python3 scripts/image_gen.py --list-backends
python3 scripts/analyze_images.py <project_path>/images
```

更新仓库：

```bash
python3 scripts/update_repo.py
python3 scripts/update_repo.py --skip-pip
```

## 建议

- 每个工作流在顶层 `scripts/` 中只保留一个面向用户的入口
- 把提供方专用实现或内部辅助程序移入子目录
- 优先使用统一入口 `project_manager.py`、`finalize_svg.py` 和 `image_gen.py`
- 导出时优先使用 `svg_final/`，不要使用 `svg_output/`

## 相关文档

- [格式转换工具](./docs/conversion.md)
- [项目工具](./docs/project.md)
- [SVG 流水线工具](./docs/svg-pipeline.md)
- [图片工具](./docs/image.md)
- [故障排查](./docs/troubleshooting.md)
- [Skill 入口](../SKILL.md)

_最后更新：2026-04-09_
