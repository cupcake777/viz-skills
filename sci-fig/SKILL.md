---
name: sci-fig
description: "Scientific figure generation: chart type selection, R/Python recipes, visual standards, and learning from example figures. Use whenever generating, modifying, or discussing any scientific plot or figure. Triggers on: plot, visualize, draw, figure, chart, heatmap, volcano, scatter, bar, violin, enrichment, manhattan, any ggplot2/matplotlib code, or figure quality complaints (labels overlap, text too small, colors clash)."
version: 3.2
tags: [plotting, visualization, bioinformatics, R, python, ggplot2, matplotlib]
related_skills: [plotting-library]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/sci-fig
---

# Scientific Figure Skill


## Architecture

```
sci-fig (skill)              ← 你现在读的：知识系统 + 学习协议 + 选图决策
    │
    ├── references/           ← 图表recipe文档（R+Python代码模板、参数、反模式）
    │
    └── /root/ops/plotting/   ← 可执行模板库（强制风格一致的执行层）
         ├── templates/*.py      7+个可执行脚本，每个有generate_mock_data() + plot()
         ├── style/matplotlibrc  全局风格配置（Nature调色板、字体、DPI）
         ├── catalog.yaml        数据类型→图表→模板索引
         ├── demo_data/          mock数据
         └── requirements.txt
```

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
| DIST | 分布 | "PDUI在Fetal样本中如何分布？" |
| COMP | 组间比较 | "Fetal vs Adult的3'UTR长度有差异吗？" |
| TREND | 有序趋势 | "PDUI从Fetal到Aged如何变化？" |
| RELATE | 关联 | "eQTL effect size与PDUI shift相关吗？" |
| COMPOSE | 组成比例 | "APA事件proximal vs distal占比？" |
| RANK | 排序 | "哪些基因3'aQTL effect最强？" |
| GENOMIC | 基因组信号 | "3'aQTL hits在全基因组分布？" |
| DIFF | 差异 | "哪些基因差异表达？" |
| MATRIX | 表达矩阵 | "Top 50 APA基因跨样本聚类？" |
| OVERLAP | 集合交集 | "3'aQTL与eQTL和疾病SNP有多重叠？" |
| TRAJ | 发育轨迹 | "单个基因跨6个阶段如何变化？" |
| ENRICH | 富集结果 | "lifespan-APA基因富集了哪些GO？" |
| MARKER | 标记基因 | "单细胞cluster的marker表达？" |

#### 决策树（Claim × Data × N）

```
展示什么？ [Claim标签]
│
├─ DIST 分布
│  ├─ 1组 → 直方图/密度图
│  ├─ 2-5组,<30点 → strip plot (geom_jitter)
│  ├─ 2-5组,≥30点 → violin + box
│  └─ >5组 → ridge plot
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

### Step 2: 加载模板

**先查可执行模板库** `/root/ops/plotting/templates/`:

| 模板脚本 | catalog数据类型 | 用途 |
|----------|---------------|------|
| volcano.py | differential_expression | 差异表达火山图 |
| manhattan.py | qtl_gwas | GWAS/QTL Manhattan图 |
| heatmap_clustered.py | expression_matrix | 聚类热图 |
| apa_pattern.py | apa_pattern_comparison | APA模式散点图 |
| enrichment_bubble.py | enrichment_result | 富集气泡图 |
| grouped_bar.py | grouped_comparison | 分组柱状图 |
| sankey.py | apa_pattern_flow | APA桑基图 |

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

### Step 3: 应用视觉规范

#### 配色（一个项目一套，全项目共用）

| 名称 | 色值 | N | 适用 |
|------|------|---|------|
| **Safe 6** | `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377` | 6 | 默认多组 |
| **Nature** | `#E64B35 #4DBBD5 #00A087 #3C5488 #F39B7F #8491B4` | 6 | 发文级 |
| **JAMA** | `#374E55 #DF8F44 #00A1D5 #B24745 #79AF97 #6A6599` | 6 | 临床 |
| **2-group** | `#2166AC #B2182B` | 2 | Up/Down, Ctrl/Treat |

连续色：`viridis`/`mako`(序列), `RdBu`/`coolwarm`(发散)。**绝不用rainbow/jet。**

matplotlibrc已内置Nature配色。如需切换：
```python
PROJECT_COLORS = {"Prenatal": "#4477AA", "Postnatal": "#EE6677"}
```
```r
project_colors <- c("Prenatal" = "#4477AA", "Postnatal" = "#EE6677")
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
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
}

def apply_sci_theme():
    plt.rcParams.update(SCI_RC)
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
## References

Detailed guides and domain-specific content:

- **[learning-protocol.md](references/learning-protocol.md)** — Figure learning protocol (L1-L5)
- **[apa-neuroscience.md](references/apa-neuroscience.md)** — APA/neuroscience decision trees, project palettes, specialized chart types
- **[gallery-workflow.md](references/gallery-workflow.md)** — Brain Gallery web UI, feedback loop, template updates
- **[scatter.md](references/scatter.md)** — Scatter plot recipe (R + Python)
- **[box_violin.md](references/box_violin.md)** — Box + violin plot recipe
- **[volcano.md](references/volcano.md)** — Volcano plot recipe
- **[heatmap.md](references/heatmap.md)** — Clustered heatmap recipe
- **[enrichment_dot.md](references/enrichment_dot.md)** — Enrichment dot/bubble plot recipe
- **[barplot.md](references/barplot.md)** — Bar plot recipe
- **[presets.md](references/presets.md)** — Detailed preset specifications
- **[telegram-chart-delivery.md](references/telegram-chart-delivery.md)** — Chart delivery via Telegram
- **[brain-gallery-deployment.md](references/brain-gallery-deployment.md)** — Gallery deployment on Brain API
- **[gallery-feedback-loop.md](references/gallery-feedback-loop.md)** — Feedback capture and template update process
