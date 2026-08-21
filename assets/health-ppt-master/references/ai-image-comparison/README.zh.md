# AI 图片对比：三维参考图库

[English](README.md) | 中文

PPT Master 的 AI 图片由三个相互独立的维度控制：**渲染（视觉风格）× 配色（色彩行为）× 类型（内部构图）**。
本目录采用**控制变量对比**：每次只改变一个维度，另外两个保持固定，让你能准确看出各维度的作用。

> 这里**不是**示例项目（示例见 `examples/`）。它是供 Strategist 角色和最终用户选择 AI 图片参数时使用的维度参考。

## 三组对比

| 子目录 | 数量 | 变量 | 固定基线 |
|---|---|---|---|
| [`rendering/`](./rendering/) | 20 | rendering（20 种风格） | 单主体主视觉构图（§4.1 基元 A），palette=cool-corporate |
| [`palette/`](./palette/) | 14 | palette（14 种色彩行为） | 单主体主视觉构图（§4.1 基元 A），rendering=vector-illustration |
| [`type/`](./type/) | 11 | type（`page_role: local` 的 11 种内部构图） | rendering=vector-illustration，palette=cool-corporate |

每个子目录都包含：

- `_subject.md`：该组使用的控制变量与主体
- `_manifest.json`：生成 manifest（status=Pending），可通过 `image_gen.py --manifest` 运行
- `<dimension>.png`：每种 rendering、palette 或 type 对应的生成图片

> `page_role: hero_page` 图片不选择 `image_type`，而是直接使用 [`image-generator.md`](../image-generator.md) §4.1 中的四种构图基元（单主体／肖像／文字排印／氛围）。`type/` 中的 11 种类型只用于局部信息图块。

## 选择这些基线的原因

| 选择 | 原因 |
|---|---|
| rendering=`vector-illustration` | 目录中用途最广；与全部 14 种 palette 均达到 ✓✓ 兼容；作为 palette／type 对比的「原点」时干扰最小 |
| palette=`cool-corporate` | 最中性、最常用；色彩行为简单（直接应用 HEX 60-30-10），不会压过待比较的维度 |
| composition=single-subject hero（§4.1 基元 A） | 一个占画布 60–70% 的主导主体，视觉形态最具代表性，因此最容易看清 rendering／palette 的差异 |

## 图片生成方式

> 参考图片使用 **OpenAI gpt-image-2** 后端生成。其他后端（gemini／doubao／qwen 等）会产生不同的视觉结果；这反映模型层面的差异，而不是 PPT Master 维度体系的差异。

复现或重新生成：

```bash
python3 skills/ppt-master/scripts/image_gen.py \
    --manifest skills/ppt-master/references/ai-image-comparison/rendering/_manifest.json \
    -o skills/ppt-master/references/ai-image-comparison/rendering/ \
    --backend openai

python3 skills/ppt-master/scripts/image_gen.py \
    --manifest skills/ppt-master/references/ai-image-comparison/palette/_manifest.json \
    -o skills/ppt-master/references/ai-image-comparison/palette/ \
    --backend openai

python3 skills/ppt-master/scripts/image_gen.py \
    --manifest skills/ppt-master/references/ai-image-comparison/type/_manifest.json \
    -o skills/ppt-master/references/ai-image-comparison/type/ \
    --backend openai
```

生成的图片会写入对应子目录。manifest 中每个条目的 `status` 会原地更新为 `Generated`、`Failed` 或 `Needs-Manual`。再次运行时只会重试 `Pending` 和 `Failed` 条目，`Generated` 条目会被跳过。

## 使用方式

| 如果你需要决定…… | 查看 |
|---|---|
| Strategist h.5 应锁定哪种 rendering | `rendering/`：并排浏览全部 20 种，选择符合 deck 视觉气质的风格 |
| 哪种 palette 与所选 rendering 最匹配 | `palette/`：观察同一主体在不同色彩行为下的变化 |
| 哪种 type 符合某张图片的用途 | `type/`：让内部构图匹配页面内容的组织形式 |

> 三组对比刻意保持相互独立。选择 rendering 时不要查看 palette 组，因为变化的色彩会干扰你对纯粹渲染风格的判断。
