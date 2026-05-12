---
name: sci-fig
description: "Scientific figure decision and quality-control skill. Use for planning, generating, revising, or critiquing scientific plots and figures. Triggers on plot, figure, chart, visualization, heatmap, volcano, scatter, bar, violin, enrichment, Manhattan, ggplot2, matplotlib, label overlap, unreadable figure, color problems, or requests to learn a figure style."
version: 5.0
tags: [plotting, visualization, bioinformatics, R, ggplot2, figures]
related_skills: [plotting-library, academic-slides]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/02_sci-fig
compatibility: R-first. Prefer ggplot2/ComplexHeatmap/patchwork/cowplot for static scientific figures; use Python only when the existing template or chart type makes it the better execution path.
---

# Scientific Figure Skill

## Architecture

```
sci-fig (skill)              ← 你现在读的：知识系统 + 学习协议 + 选图决策
    │
    ├── references/           ← 图表recipe文档（R+Python代码模板、参数、反模式）
    │
    ├── templates/AGENTS.md   ← Codex/Claude Code 入口文件（精简规则，放repo根）
    │
    └── /root/ops/plotting/   ← 可执行模板库（强制风格一致的执行层）
         ├── templates/*.py/*.R  25个可执行脚本，每个有generate_mock_data() + plot()
         ├── style/matplotlibrc  全局风格配置（Nature调色板、字体、DPI）
         ├── style/color_palettes.py/.R  25+套配色方案
         ├── catalog.yaml        数据类型→图表→模板索引（v3 schema）
         ├── demo_data/          mock数据
         ├── demo_fig/           demo PNG+PDF输出
         └── requirements.txt
```

**GitHub repo**: `cupcake777/viz-skills` — numbered directory structure (01_workflows/ through 05_powerpoint/, SKILL.md in 02_sci-fig/ and 03_plotting-library/). Local execution path mirrors `03_plotting-library/` at `/root/ops/plotting/`.

**Agent compatibility**: Codex CLI and Claude Code only read root-level config files (`AGENTS.md`, `CLAUDE.md`). The repo MUST have an AGENTS.md at root with condensed rules for these agents. See plotting-library skill for the template.

**关键原则：skill管知识和决策，plotting-library管执行。两者结合才能保证"学了就用上，用了就一致"。**

⚠️ **用户多次纠正的铁律：**
- **学习不产出可执行脚本=没学** — 只存markdown recipe不算完成，必须落到`/root/ops/plotting/templates/`的可执行.py脚本
- **学习不渲染验证=没学** — 必须执行代码出图→用户确认→才入库。未确认的图不入库。
- **不在VPS开新端口serve web页面** — 所有web统一走Brain API(8080)
- **所有web页面需认证** — Brain API token auth保护，无token返回401
- **不重复部署** — Brain API已有: `/login`, `/dashboard`, `/quota`(号池), `/review`, `/grok`, `/gallery`

---

## Workflow

### Step 0: 确定输出目标

问用户（或从上下文推断）：
- **Publication** — 7pt基准, PDF/TIFF, 300+ DPI
- **Presentation** — 16pt基准, PNG, 150-200 DPI
- **Poster** — 24pt基准, PDF/PNG, 300 DPI
- **Draft** — 12pt, PNG, 100 DPI，快速看

不确定时默认**publication**。完整规格见 [presets.md](references/presets.md)。

### Step 1: 选图

写任何绘图代码之前，先对照决策树选图。**永远不要默认用柱状图画连续数据。**

#### Claim标签系统

每张图背后回答一个核心问题。用Claim ID标签驱动选图，避免"想画什么画什么"：

| Claim | 含义 | 示例问题 |
|-------|------|---------|
| DIST | 分布 | "表达值在样本中如何分布？" |
| COMP | 组间比较 | "实验组与对照组是否有差异？" |
| TREND | 有序趋势 | "指标随时间如何变化？" |
| RELATE | 关联 | "两个连续变量的相关性？" |
| COMPOSE | 组成比例 | "各类别占比如何？" |
| RANK | 排序 | "哪些变量effect最强？" |
| GENOMIC | 基因组信号 | "QTL hits在全基因组分布？" |
| DIFF | 差异 | "哪些特征差异显著？" |
| MATRIX | 表达矩阵 | "Top基因跨条件聚类？" |
| OVERLAP | 集合交集 | "多个基因集有多重叠？" |
| TRAJ | 发育轨迹 | "单变量跨时间点如何变化？" |
| ENRICH | 富集结果 | "差异基因富集了哪些通路？" |
| MARKER | 标记基因 | "细胞cluster的marker表达？" |

#### 决策树（Claim × Data × N）

```
展示什么？ [Claim标签]
│
├─ DIST 分布
│  ├─ 1组 → 直方图/密度图
│  ├─ 2-5组,<30点 → strip plot (geom_jitter)
│  ├─ 2-5组,≥30点 → violin + box (或 raincloud，更全面)
│  ⚠️ 绝不用 bar+error bar 画连续数据
│  ⚠️ 绝不用 bar+error bar 画连续数据
│
├─ COMP 组间比较
│  ├─ 计数/比例 → bar plot（唯一正确用法）
│  ├─ 2组,<30 → strip + mean±SD
│  ├─ 2组,≥30 → violin + box + p-value
│  └─ 多组 → violin + box, facet_wrap
│
├─ TREND 有序趋势
│  ├─ ≤10线 → line + CI ribbon
│  └─ 多基因 → heatmap (ComplexHeatmap)
│
├─ RELATE 关联
│  ├─ <500点 → scatter + lm/loess
│  └─ ≥500点 → hex bin
│
├─ GENOMIC 基因组
│  ├─ GWAS/QTL → Manhattan (qqman)
│  └─ 区域注释 → chromosome ideogram
│
├─ DIFF 差异
│  └─ log2FC + p-value → volcano
│
├─ MATRIX 表达矩阵
│  └─ genes × samples → clustered heatmap
│
├─ COMPOSE 组成比例
│  ├─ ≤5类 → stacked bar (position="fill")
│  └─ >5类 → treemap
│
├─ OVERLAP 集合交集
│  ├─ ≤3集 → Venn
│  └─ >3集 → UpSet plot ⚠️绝不用>3集Venn
│
├─ TRAJ 发育轨迹
│  ├─ ≤20基因 → line + points
│  └─ >20基因 → heatmap
│
├─ ENRICH 富集
│  └─ dot plot (size=Count, color=p.adjust)
│
├─ RANK 排序
│  └─ horizontal lollipop
│
├─ MARKER 标记基因
│  └─ Seurat dot plot (size=pct, color=avg_expr)
│
├─ 时间/有序变化
│  ├─ 单轨迹 → line plot
│  ├─ 多轨迹 → multi-line (≤7, 颜色+facet)
│  └─ 有CI → ribbon plot
│
├─ 基因组数据（子类）
│  ├─ GWAS → Manhattan plot
│  ├─ 差异表达 → volcano
│  ├─ 表达矩阵 → heatmap
│  ├─ marker基因 → dot plot
│  ├─ 降维 → UMAP/tSNE
│  ├─ 富集 → dot plot
│  └─ 共定位 → stacked regional + LD
│
├─ 比例/组成
│  ├─ ≤5类 → stacked bar
│  └─ 多类 → treemap / waffle
│
├─ 排名/重要性
│  ├─ 有序列表 → horizontal bar / lollipop
│  └─ 特征重要性 → dot plot + error bars
│
└─ 网络/关系
   ├─ 基因/蛋白互作 → network graph
   ├─ 集合交集 → UpSet plot (>3集不用Venn)
   └─ 层级 → dendrogram
```

### Step 1.5: 语义配色与亮度感知（nature-skills规则）

**语义配色映射** — 不随意选色，根据数据含义选色：

| 语义 | Hex | 用途 |
|------|-----|------|
| proposed/己方 | `#0F4D92` | 蓝色系=提出方法 |
| baseline/对照 | `#3775BA` | 灰蓝=基线 |
| positive/增益 | `#2E9E44` | 绿色=正面结果 |
| negative/衰减 | `#E53935` | 红色=负面结果 |
| neutral/无变化 | `#8491B4` | 灰紫 |
| up/上调 | `#D55E00` | Okabe-Ito红橙 |
| down/下调 | `#0072B2` | Okabe-Ito蓝 |
| ns/不显著 | `#BBBBBB` | 淡灰 |

**方向性变量配色规则**：Gain/Loss、Increase/Decrease、Up/Down 是方向性变量，本质不是正面/负面。必须映射到 `up`/`down` 语义色(#D55E00/#0072B2)，而非 `positive`/`negative`。

**常见错误**：方向性变量（如Gain/Loss）不能用绿色表示正向变化、橙色表示负向变化——这违反语义映射，且在色觉缺陷下区分度差。

用法（Python）：
```python
from base_plot import SEMANTIC_COLORS, apply_semantic_palette
colors = apply_semantic_palette({"treatment": "proposed", "control": "baseline", "up": "up", "down": "down"})
# → {"treatment": "#0F4D92", "control": "#3775BA", "up": "#D55E00", "down": "#0072B2"}
```

**亮度感知文字色** — 色条/热图cell内文字自动选白或黑：
```python
from base_plot import text_color_on_bg
color = text_color_on_bg("#E64B35")  # → "white" (dark background)
color = text_color_on_bg("#FAFAFA")   # → "black" (light background)
```

**绝对禁止**：随意重映射语义色（如蓝色=负面、红色=正面），除非有充分领域惯例理由（如热图红=高表达是惯例）。

**NMI稠密图pastel专用色系**（大量柱子需要柔和区分时）：
- `#484878`→`#B4C0E4`（基线暗→柔）
- `#E4CCD8`→`#F0C0CC`（对比基→柔）

### Step 2: 加载模板

**先查可执行模板库** `/root/ops/plotting/templates/`:

| 模板脚本 | catalog数据类型 | 用途 |
|----------|---------------|------|
| volcano.py | differential_expression | 差异表达火山图 |
| manhattan.py | qtl_gwas | GWAS/QTL Manhattan图 |
| heatmap_clustered.py | expression_matrix | 聚类热图 |
| enrichment_bubble.py | enrichment_result | 富集气泡图 |
| grouped_bar.py | grouped_comparison | 分组柱状图 |
| raincloud.py | distribution_comparison | 云雨图(violin+box+jitter+mean) |

如果列表里有，**基于模板脚本生成代码**，保证 matplotlibrc 风格一致：
```python
from pathlib import Path
STYLE_PATH = Path(__file__).parent.parent / "style" / "matplotlibrc"
matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)
```

如果列表里没有（如box_violin, scatter, ridge等），**查 references/ 里的recipe文档**获取R+Python模板代码，遵循同样的视觉规范，并生成图后**Offer保存为新模板**。

### Step 2.5: 强制输出规则（不可违反）

每张科研图必须遵守：

| 规则 | 细节 |
|------|------|
| **必须同时输出PDF+PNG** | PDF出版排版用(矢量)，PNG预览用 |
| **必须明确指定尺寸** | `width` + `height`，不用默认值 |
| **禁止图内标题/副标题** | 标注属于figure legend(Word/LaTeX)，不属于图内 |
| **禁止代码中硬编码panel label** | 不用 `tag_levels="A"`，panel标注在AI/Inkscape中后期组合 |
| **文件命名 = `{step}_{description}`** | 跟pipeline step对齐：`01_preprocess.R` → `01_pca.pdf` |

R ggsave标准写法：
```r
ggsave(
  filename = "figures/01_pca.pdf",
  plot     = p,
  width    = 4, height = 3,
  device   = cairo_pdf
)
ggsave(
  filename = "figures/01_pca.png",
  plot     = p,
  width    = 4, height = 3,
  dpi      = 300
)
```

R save_fig辅助函数（放到`config/`或脚本头部）：
```r
save_fig <- function(plot, name, width, height) {
  dir.create("figures", showWarnings = FALSE)
  ggsave(paste0("figures/", name, ".pdf"),
         plot, width = width, height = height, device = cairo_pdf)
  ggsave(paste0("figures/", name, ".png"),
         plot, width = width, height = height, dpi = 300)
  message("Saved: figures/", name, ".pdf + .png")
}
# Usage: save_fig(p, "02_de_volcano", width = 3.5, height = 3.5)
```

Python对应（matplotlib）：
```python
def save_fig(fig, name, transparent=False):
    fig.savefig(f"figures/{name}.pdf", dpi=300, bbox_inches='tight',
                transparent=transparent)
    fig.savefig(f"figures/{name}.png", dpi=300, bbox_inches='tight',
                transparent=transparent)
```

### Step 2.6: 图契约 (Figure Contract) — 来源 nature-skills

每张图始于一个核心结论，而非"想画什么画什么"：

1. **核心结论** → 这张图必须让读者得出的一个要点
2. **证据链** → 从数据到结论的最短路径（1-3步）
3. **选型与原型** → Claim标签驱动选型（见决策树）
4. **导出规格** → Preset + 尺寸 + 格式

**面板层级规则（三级）：**
- **Overview（概览）**：全局分布/组成，回答"整体长什么样"
- **Deviation（偏差）**：差异/异常/对比，回答"哪里不同"
- **Relationship（关联）**：相关性/趋势/机制，回答"为什么"

**每张图的面板不得回答同一个科学问题。** 三个面板三级递进是ideal，两级也可以，但绝不重复。

**语义配色映射（项目锁定）：**
| 语义 | 色组 | 规则 |
|------|------|------|
| 己方/提出方法 | `#0F4D92` 蓝 | 蓝色系=proposed method |
| 正面/增益 | `#2E9E44` 绿 | 绿色=positive/gain |
| 负面/衰减 | `#E53935` 红 | 红色=negative/drop |
| 基线/对照 | `#3775BA` 浅蓝 + `#B4C0E4` 淡蓝 | 灰蓝=baselines |
| 红蓝仅用于方向 | 红=降/蓝=升 | 绝不随意重映射 |

**NMI稠密图专用pastel色系：**
- `#484878`→`#B4C0E4`（基线暗→柔）
- `#E4CCD8`→`#F0C0CC`（对比基→柔）

**反对称布局偏好：** 70/30 > 75/25 > 65/35 > 50/50。hero panel占45-60%视觉面积。

**亮度感知文字色：** 色条内文字自动判断亮暗：
```python
def text_color(bg_hex):
    r, g, b = int(bg_hex[1:3],16), int(bg_hex[3:5],16), int(bg_hex[5:7],16)
    lum = 0.299*r + 0.587*g + 0.114*b
    return "white" if lum < 128 else "black"
```

### Step 3: 应用视觉规范

#### Palette全库参考

完整25+套配色方案 + CVD安全标注 + 选择决策树: [color-palettes.md](references/color-palettes.md)

可执行Python模块: `/root/ops/plotting/style/color_palettes.py`

---

#### 配色（一个项目一套，全项目共用）

完整配色库见 `/root/ops/plotting/style/color_palettes.py`，25+套期刊级配色方案，含CVD安全标注。

| 名称 | Hex | N | CVD安全 | 适用 |
|------|-----|---|---------|------|
| **Okabe-Ito** | `#E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 #000000` | 8 | ✓ | Nature金标准，默认首选 |
| **Tol Bright** | `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377 #BBBBBB` | 7 | ✓ | 高辨识度线条图 |
| **Tol Muted** | `#332288 #88CCEE #44AA99 #117733 #999933 #DDCC77 #CC6677 #882255 #AA4499` | 9 | ✓ | 9组以上多类别 |
| **NPG** | `#E64B35 #4DBBD5 #00A087 #3C5488 #F39B7F #8491B8 #91D1C2 #DC0000 #7E6148 #B09C85` | 10 | ✗ | Nature Reviews Cancer |
| **NEJM** | `#BC3C29 #0072B5 #E18727 #20854E #7876B1 #6F99AD #FFDC91 #EE4C97` | 8 | ✓ | NEJM医学期刊 |
| **Lancet** | `#00468B #ED0000 #42B540 #0099B5 #925E9F #FDAF91 #AD002A #ADB6B6` | 8 | ✓ | 柳叶刀 |
| **JAMA** | `#374E55 #DF8D5B #003B5C #B6370E #56B3E0 #00A087` | 6 | ✓ | 深色调高端感 |
| **JCO** | `#0073A8 #E08B28 #A0244D #56B3E0 #3C5488 #91D1C2 #DC0000 #7E6148` | 8 | ✓ | 肿瘤学 |
| **2-group** | `#2166AC #B2182B` | 2 | ✓ | Up/Down, Ctrl/Treat |

基因组学专用：
- **Volcano**: Up `#D55E00` / Down `#0072B2` / NS `#BBBBBB`
- **Survival**: High `#D55E00` / Low `#0072B2` / Censored `#BBBBBB`

连续色：`viridis`/`mako`(序列), `RdBu`/`coolwarm`(发散), `roma`/`vik`(Crameri CVD-safe发散)。**绝不用rainbow/jet。**

使用方式：
```python
from style.color_palettes import get_palette, apply_palette
apply_palette("okabe_ito")   # 设为全局色环
colors = get_palette("npg")   # 获取hex列表
```
```r
source("style/color_palettes.R")
use_pal("okabe_ito")           # 设为ggplot2默认
pal <- get_pal("npg")         # 命名hex向量
```

**项目配色（按项目锁定）**

项目级配色由用户根据研究定义。连续变量用cmap（如`mako`），分类变量用已有palette（如`npg`/`okabe_ito`）。

```python
# 项目配色示例（用户自定义）
from style.color_palettes import apply_palette
apply_palette("npg")  # 全项目统一用NPG配色
# 连续变量: plt.cm.mako
# 方向性变量: apply_semantic_palette({"gain": "up", "loss": "down"})
```
}
```

#### 字体与尺寸

- Sans-serif only: Arial / Helvetica / Calibri
- 基因名 *italic*（*APOE*），蛋白名 roman
- 轴标签带单位："Gene expression (TPM)", "-log₁₀(p-value)"
- 进入多面板/PPT的图不加title，用slide标题代替

| Preset | 基准 | 轴标签 | 刻度 | 图例 |
|--------|------|--------|------|------|
| Publication | 7pt | 7pt | 6pt | 6pt |
| Presentation | 16pt | 16pt | 14pt | 14pt |
| Poster | 24pt | 24pt | 20pt | 20pt |

#### 标签防重叠（#1视觉缺陷）

- **永远**用 `ggrepel`(R) 或 `adjustText`(Python) 标注基因名。不用 `geom_text`
- >20个标签 → 只标top N
- 拥挤分类轴 → 旋转45° 或翻转为水平bar

### Step 4: 生成代码 → 渲染图 → 用户确认

**这是闭环的关键。生成代码后必须执行渲染出图，发给用户确认。**

流程：
1. 生成绘图代码（基于模板或recipe）
2. **执行代码，渲染出图**
3. 把图发给用户（上传PNG到Gallery或直接发送）
4. 等用户反馈：
   - "可以" → 确认，可选保存为模板
   - 具体修改意见 → 修改 → 重新渲染 → 再次确认
   - "保存为模板" → 存入 `/root/ops/plotting/templates/` 并更新 `catalog.yaml`

**不是确认过的图，不存模板。**

用户可通过Gallery页面交互式反馈（✓ Approve / ✎ Suggest / ✕ Reject），反馈写入 `/root/ops/plotting/gallery_feedback.jsonl`。Agent应定期读取该文件处理Suggest意见：

```bash
# 读取Gallery反馈
cat /root/ops/plotting/gallery_feedback.jsonl
# 处理建议后清空（可选）
> /root/ops/plotting/gallery_feedback.jsonl
```

处理Suggest的闭环：读取反馈 → 修改对应模板代码 → `python3 templates/xxx.py` 重新渲染demo → 更新Gallery → 通知用户确认。

### Step 5: QA清单

交付前自查：

**可读性**
- [ ] 所有文字 ≥ 该preset最小字号
- [ ] 轴标签含单位
- [ ] 图例完整且匹配数据
- [ ] 无标签重叠
- [ ] 在实际尺寸下可读

**准确性**
- [ ] 轴起始值正确（bar图从0起）
- [ ] 统计标注正确
- [ ] 配色与项目palette一致
- [ ] 无数据被遮挡

**一致性**
- [ ] 同项目同色=同义
- [ ] 字体族和大小层级一致
- [ ] 轴标签格式一致
- [ ] 基因命名规范（italic gene, roman protein）

**技术**
- [ ] DPI正确（pub 300+, ppt 150+）
- [ ] 尺寸符合preset
- [ ] 格式正确（pub PDF, ppt PNG）
- [ ] 如需PPT叠加则透明背景

---

## 学习协议

当用户发来一张觉得好的图（来自paper、网站或自己的作品）：

### L1: 拆解

分析并提取8个维度：

1. **图表类型** — 火山图?热图?ridge?dot plot?
2. **布局** — 单面板/多面板? 排列方式? 宽高比?
3. **配色** — 提取hex色值，或匹配已知palette
4. **字体** — serif/sans-serif, 大小层级, bold/italic用法
5. **轴处理** — log/sqrt刻度? 刻度标签格式? 有无grid
6. **标注** — 统计标记, 基因标签, 阈值线, 图例位置
7. **数据编码通道** — position, color, size, shape 各编码了什么
8. **好在哪里** — 1-2句话总结，为什么这张图比平均水准好

### L2: 分类

| 情况 | 操作 |
|------|------|
| 全新图表类型（模板库没有） | 创建新模板脚本 + 新recipe文档 |
| 已有类型的风格变体 | 在现有模板上加 variation 参数 + recipe文档加 Variants 段 |
| 基础recipe的普适改进 | 直接patch基础模板和recipe，加版本说明 |

### L3: 生成代码 + 渲染验证

**不是只写markdown完事。必须产出可执行代码并渲染出图让用户确认。**

1. 写出Python脚本（复用 matplotlibrc 风格，放到 `/root/ops/plotting/templates/`）和/或R代码
2. **执行代码，用mock数据渲染出PNG**（`python3 templates/xxx.py` 生成 `_demo.png`）
3. 发图给用户看（Telegram发送图片或Gallery链接）
4. 用户确认后才保存：
   - 脚本存 `templates/`, mock数据存 `demo_data/`
   - 更新 `catalog.yaml`
   - recipe存 `references/`
   - 重建Gallery并推送到HF Space
5. 用户说修改 → 按反馈改 → 重新渲染 → 再审

**⚠️ 只存markdown recipe不入库。入库=可执行脚本+用户确认过的图。**

### L4: 保存

经用户确认后才保存：

**可执行层** (`/root/ops/plotting/`):
```
templates/new_chart.py      ← 可执行脚本，含 generate_mock_data() + plot()
demo_data/new_chart_demo.tsv ← mock数据
catalog.yaml                ← 更新数据类型→模板映射
```

**知识层** (`skill references/`):
```
references/new_chart.md     ← recipe文档（When/Learn/Code/Params/Pitfalls/Variants）
```

### L5: 竞品调研（Chart Gap Analysis）

当需要系统性扩展模板库时，不只是从单张图学习，而是进行竞品网站调研：

1. **爬取竞品站点** — 用web_extract/web_search获取SRplot、ChiPlot、Bioincloud等平台的完整图表分类
2. **建立对照表** — 将竞品图表与现有catalog逐项对比，标记✅已有/🔴缺失
3. **优先级分级** — P0(三站都有且高频) > P1(常见) > P2(特色但低频)
4. **实施顺序** — 从P0开始，每个模板: mock数据→代码→渲染→用户确认→入库
5. **调研产出** — 写入 `references/site-survey.md`，包含平台对比、配色参考、数据格式共性

调研文档已存在: [site-survey.md](references/site-survey.md)（SRplot 120+图、ChiPlot 41图、Bioincloud 100+图）

### Gallery架构 (2026-05-09重构)
- catalog.yaml是单一真相源，Gallery热加载，无硬编码demo_map
- 分类筛选: 15个大类(category) + 3个Tier(P0/P1/P2)，不再是101个扁平tag
- 每个图表tags最多2个，通过`_CATEGORY_GROUPS`映射到大类
- 新增图表只需改catalog.yaml + 放demo PNG，不需重启服务
- 详见 plotting-library skill `references/gallery-architecture.md`

### P0图表当前状态
- raincloud ✅ 已完成 (云雨图, violin+box+jitter+mean)
- forest_plot 📋 待实现
- oncoplot 📋 待实现
- lollipop 📋 待实现

### L6: 应用

后续绘图时，检查优先级：
1. 当前项目是否已指定palette？用那个
2. 用户是否为该图表类型发过示例图？优先用那个变体
3. 跟数据/分析场景匹配的变体？用那个
4. 都没有 → 用基础recipe + matplotlibrc默认风格

### L7: 语义配色规则（nature-skills集成）

所有新模板应优先使用 `SEMANTIC_COLORS` 和 `text_color_on_bg()` 而非任意hex。
语义色规则：
- 蓝=己方/提出方法, 绿=正面/增益, 红=负面/衰减, 灰蓝=基线/对照
- 红蓝仅用于方向：红=升/下调, 蓝=降/下调（Okabe-Ito）
- 同一项目内绝不重映射语义色

详细规则和学术写作规则见 [nature-skills-rules.md](references/nature-skills-rules.md)

---

## 项目配色约定

定义项目级配色时，遵循以下原则：
- 一个项目统一一套配色，全项目共用
- 连续变量（如发育阶段）用连续色标（`viridis`/`mako`），不要离散色
- 分类配色优先使用已有palette（okabe_ito/npg/lancet等），不硬编码hex
- 方向性变量（up/down, increase/decrease）用语义色，不用领域特定名称

```python
# 项目配色定义示例（用户根据自己项目定义）
# from style.color_palettes import apply_palette
# apply_palette("npg")  # 全项目统一用NPG配色
# 连续变量用cmap: plt.cm.mako
```

```r
# source("style/color_palettes.R") 后可直接用:
# use_pal("npg")  # 全项目统一用NPG配色
```

### 新增图表类型（优先级排序）

| 图表 | 模板名 | 数据类型 | 用途 |
|------|--------|---------|------|
| 全生命周期轨迹 | `lifespan_trajectory` | lifespan_trajectory | 连续变量随年龄的多轨迹变化 |
| 云雨图 | `raincloud` | distribution_comparison | violin+box+jitter三合一 ✅Done |
| Forest plot | `forest_plot` | meta_analysis | 多变量OR/HR及置信区间 (P0) |
| Lollipop | `lollipop` | mutation_site | 基因突变/修饰位点标注 (P0) |
| Oncoplot | `oncoplot` | mutation_matrix | 肿瘤突变景观瀑布图 (P0) |
| Seurat dot plot | `dot_plot_seurat` | marker_expression | 单细胞marker基因表达 |
| Stacked area | `stacked_area` | composition_over_time | 组成比例随时间变化 |
| 染色体ideogram | `chromosome_ideogram` | genomic_region | 染色体区段标注(GWAS/QTL信号) |

---

## 项目代码审计铁律（14项全查）

⚠️ **仅替换hex色值≠完成！** 用户明确说"几乎看不出改动"。详见 [references/project-audit-checklist.md](references/project-audit-checklist.md)。

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | 语义配色 | PATTERN_COLORS用up/down语义映射，非硬编码hex |
| 2 | 散点图例 | scatter必须有图例 |
| 3 | 富集尺寸图例 | Line2D proxy, 非scatter([],[])假点 |
| 4 | PDF+PNG双格式 | save_fig必须同时输出 |
| 5 | Arial字体 | 非DejaVu Sans |
| 6 | #FAFAFA背景 | 非纯白 |
| 7 | labelweight=bold | 轴标签加粗 |
| 8 | alpha密度 | scatter alpha≤0.5(>50点), ≤0.3(>500点) |
| 9 | matplotlibrc加载 | 用viz-skills matplotlibrc，非inline plt.rcParams.update |
| 10 | text_color_on_bg | 从base_plot import，非手动阈值 |
| 11 | adjustText防重叠 | 非ax.text()静态放置，需HAS_ADJUST_TEXT fallback |
| 12 | 无panel letter | set_title不含A/B/C/D前缀 |
| 13 | DPI=300 | 非自定义值(320/180等) |
| 14 | 无硬编码hack | pad=42等hardcoded布局需移除 |

---

## 反模式速查

| ❌ 别用 | ✅ 该用 | 原因 |
|---------|--------|------|
| bar+error bar画基因表达 | violin+jitter | 隐藏分布形态 |
| >3集的Venn图 | UpSet plot | 3集以上不可读 |
| >5类的饼图 | horizontal bar | 角度难以比较 |
| 3D柱状图 | 2D柱状图 | 3D扭曲感知 |
| rainbow/jet色标 | viridis或单色序列 | 感知不均匀、色盲不友好 |
| 红绿色分两组 | 蓝+橙+形状 | 8%男性色觉缺陷 |
| 5万点全通透scatter | hex bin / alpha=0.1 | 过度绘制遮密度 |
| 分类变量画折线图 | 分组bar / dot plot | 线暗示连续性 |

---

## Preset速查

| Preset | 宽 | 高 | DPI | 最小字号 | 格式 |
|--------|----|----|-----|---------|------|
| `publication` | 180mm/85mm | 弹性 | 300-600 | 7pt | PDF/TIFF |
| `presentation` | 10in | 5.6in(16:9) | 150-200 | 16pt | PNG |
| `poster` | 弹性 | 弹性 | 300 | 24pt | PDF/PNG |
| `draft` | 8in | 6in | 100 | 12pt | PNG |

完整规格+导出代码: [presets.md](references/presets.md)

---

## R/Python主题模板

### R
```r
theme_sci <- function(base_size = 7) {
  theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.title = element_text(size = base_size),
      axis.text = element_text(size = base_size - 1, color = "grey30"),
      legend.title = element_text(size = base_size, face = "bold"),
      legend.text = element_text(size = base_size - 1),
      strip.text = element_text(size = base_size, face = "bold"),
      strip.background = element_blank(),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.margin = margin(5, 5, 5, 5, "pt")
    )
}
```

### Python
```python
SCI_RC = {
    "font.family": "Arial",
    "font.size": 7,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "axes.labelweight": "bold",     # v2: 加粗轴标签增加层次感
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": "#FAFAFA",      # v2: 浅灰plot area背景增加层次
    "figure.facecolor": "white",
    "figure.dpi": 300,
}

def apply_sci_theme():
    plt.rcParams.update(SCI_RC)

def apply_gallery_polish(ax):
    """Gallery级别视觉打磨：极淡y-grid + spine微调。"""
    ax.yaxis.grid(True, axis='y', linestyle='--', linewidth=0.4, 
                  alpha=0.5, color='#CCCCCC', zorder=0)
    ax.set_axisbelow(True)
    for spine_key in ['left', 'bottom']:
        ax.spines[spine_key].set_color('#555555')
        ax.spines[spine_key].set_linewidth(
            plt.rcParams.get('axes.linewidth', 0.5) * 1.2)

def polish_legend(ax, ncol=1, loc='best', frame_alpha=0.92):
    """统一图例风格：圆角框、padding、边缘色。"""
    leg = ax.legend(ncol=ncol, loc=loc, framealpha=frame_alpha,
                    edgecolor='#CCCCCC', fancybox=True,
                    borderpad=0.6, handlelength=1.8, handletextpad=0.6)
    leg.get_frame().set_linewidth(0.6)
    return leg
```

### 已有的全局matplotlibrc
可执行模板统一加载 `/root/ops/plotting/style/matplotlibrc`：
```python
from pathlib import Path
STYLE_PATH = Path("/root/ops/plotting/style/matplotlibrc")
matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)
```
里面预置了Nature配色、Arial字体、300DPI等。所有模板脚本共用这个风格配置。

---

## Gallery & 审核流程

### 线上Gallery

地址: Brain API `/gallery`（需auth token登录）

Brain API已有完整Web看板体系：`/login` → `/dashboard`, `/quota`(号池), `/grok`, **`/gallery`**(绘图Gallery)。所有页面统一认证（token或密码），所有图片通过 `/gallery/static/` 按需加载。Gallery可按tag筛选，点击放大查看。

访问方式：
- 浏览器: `http://<server>:8080/login` → 登录 → 点击Gallery导航
- API: `curl -H "Authorization: Bearer <token>" http://<server>:8080/gallery`

⚠️ **所有web页面统一走Brain API**（8080端口），不在VPS开新端口，不在HF Space部署Gallery。

### 审核入库流程

Gallery每张demo图卡有三个交互按钮，通过 `/api/gallery/feedback` API写入反馈：
- ✓ Approve → `{action: "approve"}`
- ✎ Suggest → 展开textarea输入建议 → `{action: "suggest", suggestion: "..."}`
- ✕ Reject → `{action: "reject"}`

反馈记录在 `/root/ops/plotting/gallery_feedback.jsonl`。

1. 生成新样图后，渲染demo保存到 `/root/ops/plotting/`
2. 重启Brain API: `systemctl restart hermes-serve`
3. 通知用户访问 `/gallery` 查看，点击按钮反馈
4. 用户确认"可以/入库" → 执行：
   - 脚本存 `templates/`, mock数据存 `demo_data/`
   - 更新 `catalog.yaml`
   - recipe存 `references/`
5. 用户说修改 → 按反馈改 → 重新渲染 → 再审

**未确认的图不入库。**

### 更新Gallery流程

```bash
cd /root/ops/plotting
for f in templates/*.py; do python3 "$f"; done
systemctl restart hermes-serve
# 验证
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8080/gallery | head -5
```

⚠️ **所有web页面统一走Brain API**（8080端口），不在VPS开新端口
⚠️ **Gallery需认证**，无token返回401
⚠️ **JS必须用 `extra_js` 参数传入 `_page()`** — f-string会破坏JS的`{{`/`}}`，见 `references/brain-gallery-deployment.md`
⚠️ **浏览器fetch用 `credentials: 'same-origin'`** — httponly cookie不可JS读取，靠浏览器自动带cookie+Origin

---

## 常见陷阱

| 问题 | 解决 |
|------|------|
| 标签重叠 | ggrepel/adjustText; 减少label数; 45°旋转 | adjustText需`pip install adjusttext`; 优先用adjustText，回退用annotate+clip_on=True |
| 连续数据用了bar图 | 换violin+jitter，永远 |
| ≥500点全量scatter无alpha | hex bin / alpha=0.1 / alpha=0.3 |
| 3集以上用Venn图 | UpSet plot，永远 |
| 图内加title/subtitle | 标注在figure legend，不在图内 |
| 代码中用tag_levels组合panel | 在AI/Inkscape中后期组合 |
| ggsave无尺寸参数 | 必须指定width+height |
| 红绿色分两组 | 蓝+橙+形状，8%男性色觉缺陷 |
| p值=0导致log爆轴 | `pmin(p, 1e-300)`(R) / `.clip(lower=1e-300)`(py) |
| 太多显著点成红球 | 提高FC阈值; alpha=0.3; 加密度轮廓 |
| 一个极值支配色标 | 截断: `mat[mat>3] <- 3` |
| 热图行名看不清 | 不显示; 用row_annotation或箭头标注关键基因 |
| 轴标签缺单位 | 加: "Expression (TPM)", "Age (years)" |
| 图在真实尺寸不可读 | 缩小看，检查最小字号 |
| 标签溢出绘图框 | adjustText + `clip_on=True`; fallback时必须加`clip_on` |
| Manhattan标注用了variant ID | 用`gene_col`优先标注Gene name，x轴已经是位置信息 |
| Gallery按钮没后端 | 必须接`/api/gallery/feedback`，纯前端装饰无用 |
| localStorage状态丢失 | JS选择器类名必须与HTML完全匹配；绝不要inline onclick和addEventListener混用于同一行为 |
| inline onclick和addEventListener打架 | 移除所有inline onclick，只用addEventListener统一管理状态+localStorage |
| **matplotlibrc不能设hex色值** | 用float或颜色名(white/gray)，hex色值(#FAFAFA)必须通过Python `plt.rcParams`设置 |
| **matplotlibrc不支持行内注释** | `axes.grid: False  # comment`会报错，注释必须独占一行 |
| **Gallery preset单独渲染** | demo图必须用`preset="gallery"`（14pt, 8×5.6, 180dpi），不用publication(7pt看不清) | |
| **项目代码审计（14项铁律）** | ⚠ 仅替换hex色值≠完成！详见 references/project-audit-checklist.md。(1)语义配色(非硬编码hex) (2)散点缺图例补上 (3)富集点图缺尺寸图例用Line2D proxy (4)PDF+PNG双格式 (5)Arial非DejaVu Sans (6)#FAFAFA非纯白 (7)labelweight=bold (8)alpha≤0.5 (9)加载matplotlibrc替代inline rcParams (10)base_plot.text_color_on_bg()替代手动阈值 (11)adjustText防重叠(非ax.text) (12)删除panel letter前缀 (13)DPI=300 (14)删除pad=N等硬编码hack |