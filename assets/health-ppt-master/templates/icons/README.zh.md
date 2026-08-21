# SVG 图标库

[English](README.md) | 中文

本目录提供来自五个图标库的**11,600 多个高质量 SVG 图标**，可直接嵌入 PPT Master 生成的 SVG 文件。其中四个是风格图标库（每个 deck 选择**一个**），另一个是品牌 logo 库（`simple-icons`），作为内嵌图标与所选风格库配合使用。

## 图标库

| 图标库 | 风格 | 数量 | viewBox | 前缀 |
|---------|-------|-------|---------|--------|
| `chunk-filled` | 填充 · 直线几何（锐角、直线形） | 640 | `0 0 16 16` | `chunk-filled/` |
| `tabler-filled` | 填充 · 贝塞尔曲线形态（平滑的圆润轮廓） | 1000+ | `0 0 24 24` | `tabler-filled/` |
| `tabler-outline` | 描边／线条 | 5000+ | `0 0 24 24` | `tabler-outline/` |
| `phosphor-duotone` | 双色调 · 单色 + 0.2 不透明度底板（柔和纵深） | 1200+ | `0 0 256 256` | `phosphor-duotone/` |
| `simple-icons` | **品牌 logo**（真实公司／产品标记），单色剪影，通过 `fill` 上色 | 3400+ | `0 0 24 24` | `simple-icons/` |

---

## 用法

在 **SVG 生成期间**使用占位符语法：

```xml
<!-- chunk-filled (sharp, geometric — tech/engineering/enterprise tone) -->
<use data-icon="chunk-filled/home" x="100" y="200" width="48" height="48" fill="#0076A8"/>

<!-- tabler-filled (rounded, organic — lifestyle/health/home tone) -->
<use data-icon="tabler-filled/home" x="100" y="200" width="48" height="48" fill="#0076A8"/>

<!-- tabler-outline (light, line-art — refined screen-only showcases) -->
<use data-icon="tabler-outline/home" x="100" y="200" width="48" height="48" fill="#0076A8"/>

<!-- phosphor-duotone (soft depth — single color renders the backplate at 20% opacity) -->
<use data-icon="phosphor-duotone/house" x="100" y="200" width="48" height="48" fill="#0076A8"/>

<!-- simple-icons (brand logo — used alongside the deck's primary library, not as a substitute) -->
<use data-icon="simple-icons/github" x="100" y="200" width="48" height="48" fill="#181717"/>
```

**属性**：
- `data-icon`：`<library>/<icon-name>`（不含 `.svg` 的文件名）
- `x`、`y`：位置
- `width`、`height`：尺寸（建议使用 32–48px 以保证可辨识度）
- `fill`：颜色

`finalize_svg.py` 会在后处理期间自动嵌入所有占位符。手动运行：

```bash
python3 scripts/svg_finalize/embed_icons.py svg_output/*.svg
```

---

## 搜索图标

使用 `ls | grep`，不消耗 token：

```bash
ls skills/ppt-master/templates/icons/chunk-filled/ | grep home
ls skills/ppt-master/templates/icons/tabler-filled/ | grep home
ls skills/ppt-master/templates/icons/tabler-outline/ | grep chart
ls skills/ppt-master/templates/icons/phosphor-duotone/ | grep house
ls skills/ppt-master/templates/icons/simple-icons/ | grep github
```

---

## 风格规则

**没有默认图标库，应根据 deck 的视觉需要主动选择。** 先阅读源材料，再选择视觉特征最适合该演示文稿的图标库。各图标库具有不同的视觉个性：

- **`chunk-filled`**：**填充**风格，只由直线命令（M/L/H/V/Z）构成。直角锐利精准；几何形态以直线为主；结构清晰，在小尺寸下也高度可辨。视觉重量：厚重、实心、建筑感。
- **`tabler-filled`**：**填充**风格，由贝塞尔曲线和圆弧（C/A）构成。轮廓平滑、圆润、有机；比 `chunk-filled` 更温暖柔和。视觉重量：中等、亲和。
- **`tabler-outline`**：**描边**风格（线稿，默认 stroke-width 为 2）。轻盈、精致，善用负空间。视觉重量：轻巧、优雅。细描边在打印或投影时可能难以辨认，因此最适合仅在屏幕上查看。
- **`phosphor-duotone`**：**双色调**风格；主形状使用完全不透明度，同色底板使用 20% 不透明度，形成柔和的纵深感。视觉重量：中等、有层次、现代。

> **选择时要考虑两个维度**：
> 1. **几何形态**：直线（`chunk-filled`）、曲线（`tabler-filled`／`phosphor-duotone`）或开放描边（`tabler-outline`）
> 2. **视觉重量**：厚重实心（`chunk-filled`）→ 中等实心（`tabler-filled`）→ 中等分层（`phosphor-duotone`）→ 轻量描边（`tabler-outline`）

**一份演示文稿 = 一个风格图标库。** 开始时选择 `chunk-filled`、`tabler-filled`、`tabler-outline` 或 `phosphor-duotone`，并在通用图标（主页、图表、用户等）中始终只用这个库。如果所选库没有完全匹配的图标，请在同一个库中寻找最接近的替代项；绝不能为填补缺口而混用风格图标库。

**品牌 logo 例外（`simple-icons`）。** `simple-icons` **不是风格图标库**，不受「一个库」规则约束。它的用途是品牌识别，例如 Slack 的紫色、GitHub 的猫、AWS 的配色，这些元素本来就刻意保持多样。请将它与所选风格图标库**配合**使用，但**只**用于真实的公司／产品／服务品牌标记。所选风格库缺少通用图标时，**不要**用它替代。

| `simple-icons` 的适用场景 | `simple-icons` 的禁用场景 |
|------------------------|-------------------------------|
| 「客户信赖」页面中的客户／合作伙伴／生态系统 logo | 通用概念（主页、图表、设置等） |
| 架构图／集成图中的技术栈图标 | 替换 `chunk-filled`／`tabler-*`／`phosphor-duotone` 中缺少的图标 |
| 页脚中的社交媒体账号 | 装饰／插图用途 |

⚠️ **不要**混用不同**风格**图标库（`chunk-filled`／`tabler-filled`／`tabler-outline`／`phosphor-duotone`）。`simple-icons` 是唯一例外，可以作为内嵌品牌 logo 共存；详见上面的品牌 logo 例外。
