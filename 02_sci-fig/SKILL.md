---
name: sci-fig
description: "Scientific figure decision and quality-control skill. Use for planning, generating, revising, or critiquing scientific plots and figures."
version: 6.0
tags: [plotting, visualization, bioinformatics, R, ggplot2, figures]
related_skills: [plotting-library, academic-slides]
compatibility: R-first. Prefer ggplot2/ComplexHeatmap/patchwork/cowplot for static scientific figures; use Python only when the existing template makes it the better execution path.
---

# Scientific Figure Skill

## Architecture

```
sci-fig (this file)        ← Knowledge: decision tree, QA, anti-patterns
    ├── references/         ← Deep docs (color palettes, learning protocol, recipes)
    └── 03_plotting-library/ ← Execution layer (templates, style, catalog.yaml)
```

**关键原则：skill管知识和决策，plotting-library管执行。两者结合才能保证"学了就用上，用了就一致"。**

---

## Project Config

If the project root has `config/plot_config.yaml`, **source it first**. Its palette overrides all defaults below. This lets each project lock its own color scheme without editing the skill.

```python
import yaml
from pathlib import Path
_cfg = Path("config/plot_config.yaml")
if _cfg.exists():
    with open(_cfg) as f:
        PLOT_CONFIG = yaml.safe_load(f)
    # PLOT_CONFIG["palette"] overrides default palette
```

```r
if (file.exists("config/plot_config.yaml")) {
  PLOT_CONFIG <- yaml::read_yaml("config/plot_config.yaml")
}
```

---

## Workflow

### Step 0: 确定输出目标

| Target | 基准字号 | DPI | 格式 |
|--------|---------|-----|------|
| Publication | 7pt | 300+ | PDF/TIFF |
| Presentation | 16pt | 150-200 | PNG |
| Poster | 24pt | 300 | PDF/PNG |
| Draft | 12pt | 100 | PNG |

不确定时默认 **publication**。完整规格见 [presets.md](references/presets.md)。

### Step 1: 选图（Claim × Data × N）

用Claim标签驱动选图，永远不要默认用柱状图画连续数据。

| Claim | 含义 | 选图规则 |
|-------|------|---------|
| DIST | 分布 | 1组→直方图; 2-5组<30点→strip; ≥30点→violin+box |
| COMP | 比较 | 计数→bar; 2组→strip+mean±SD; 多组→violin+box+facet |
| TREND | 趋势 | ≤10线→line+CI; 多基因→heatmap |
| RELATE | 关联 | <500点→scatter+lm; ≥500点→hexbin |
| GENOMIC | 基因组 | GWAS→Manhattan; 区域→ideogram |
| DIFF | 差异 | log2FC+p→volcano |
| MATRIX | 矩阵 | genes×samples→clustered heatmap |
| COMPOSE | 组成 | ≤5类→stacked bar; >5类→treemap |
| OVERLAP | 交集 | ≤3集→Venn; >3集→UpSet ⚠️ |
| TRAJ | 轨迹 | ≤20基因→line; >20→heatmap |
| ENRICH | 富集 | dot plot (size=Count, color=p.adjust) |
| RANK | 排序 | horizontal lollipop |
| MARKER | 标记 | Seurat dot plot |

### Step 1.5: 语义配色（唯一真相表）

| 语义 | Hex | 用途 |
|------|-----|------|
| proposed/己方 | `#0F4D92` | 蓝色系=提出方法 |
| baseline/对照 | `#3775BA` | 灰蓝=基线 |
| positive/增益 | `#2E9E44` | 绿色=正面 |
| negative/衰减 | `#E53935` | 红色=负面 |
| up/上调 | `#D55E00` | Okabe-Ito红橙 |
| down/下调 | `#0072B2` | Okabe-Ito蓝 |
| ns/不显著 | `#BBBBBB` | 淡灰 |

**方向性变量（Gain/Loss, Up/Down）映射到 up/down 色，不用 positive/negative。**

完整配色库（25+套+CVD标注）: [color-palettes.md](references/color-palettes.md)

### Step 2: 加载模板

先查 `03_plotting-library/templates/` 有无现成模板。有→基于模板生成代码。没有→查 `references/` recipe文档，生成图后 offer 保存为新模板。

### Step 2.5: 强制输出规则

| 规则 | 细节 |
|------|------|
| PDF+PNG双输出 | PDF矢量出版用，PNG预览用 |
| 明确指定尺寸 | width+height，不用默认值 |
| 禁止图内标题 | 标题属于figure legend |
| 禁止panel label代码 | A/B/C在后期组合 |
| 命名 = `{step}_{desc}` | 如 `01_pca.pdf` |

### Step 3: 视觉规范

- **字体**: Sans-serif only (Arial/Helvetica), 基因名italic
- **标签防重叠**: ggrepel(R) / adjustText(Python), >20标签只标top N
- **连续色**: viridis/roma/vik。**绝不用rainbow/jet**
- **配色入口**: `get_palette()` / `use_pal()` from `style/color_palettes`

### Step 4: 渲染 → 用户确认

生成代码 → 执行渲染 → 发图给用户 → 确认后才入库。**未确认不入库。**

### Step 5: QA清单

- [ ] 文字 ≥ preset最小字号，轴标签含单位
- [ ] 配色与项目palette一致
- [ ] 同项目同色=同义
- [ ] DPI正确，格式正确
- [ ] 无标签重叠，无数据遮挡

---

## 反模式速查

| ❌ 别用 | ✅ 该用 | 原因 |
|---------|--------|------|
| bar+error bar画连续数据 | violin+jitter | 隐藏分布 |
| >3集Venn | UpSet | 不可读 |
| >5类饼图 | horizontal bar | 角度难比 |
| rainbow/jet | viridis | CVD不友好 |
| 红绿色分两组 | 蓝+橙+形状 | 8%男性色盲 |
| 5万点全量scatter | hex bin / alpha=0.1 | 过度绘制 |
| 分类变量折线图 | bar / dot plot | 线暗示连续 |

---

## Deep References

| 需求 | 文件 |
|------|------|
| 完整配色库+CVD+Morandi | [color-palettes.md](references/color-palettes.md) |
| 学习协议(L1-L7) | [learning-protocol.md](references/learning-protocol.md) |
| 图表recipe(各类型) | `references/volcano.md`, `heatmap.md`, `scatter.md` 等 |
| 尺寸preset详解 | [presets.md](references/presets.md) |
| 视觉规范详解 | [visual-standards.md](references/visual-standards.md) |
| 项目审计14项 | [project-audit-checklist.md](references/project-audit-checklist.md) |
| R/Python主题代码 | [r-python-themes.md](references/r-python-themes.md) |
| 图契约+面板层级 | [figure-contract.md](references/figure-contract.md) |

---

## 常见陷阱

| 问题 | 解决 |
|------|------|
| 标签重叠 | ggrepel/adjustText; 减少label数; 45°旋转 |
| 连续数据bar图 | 换violin+jitter |
| p值=0爆轴 | `pmin(p, 1e-300)` / `.clip(1e-300)` |
| 热图行名看不清 | 不显示，用row_annotation |
| 一个极值支配色标 | 截断: `mat[mat>3] <- 3` |
| matplotlibrc不支持hex | hex色通过plt.rcParams设置 |
