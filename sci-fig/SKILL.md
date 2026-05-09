---
name: sci-fig
description: "Scientific figure generation: chart type selection, R/Python recipes, visual standards, and learning from example figures. Use whenever generating, modifying, or discussing any scientific plot or figure. Triggers on: plot, visualize, draw, figure, chart, heatmap, volcano, scatter, bar, violin, enrichment, manhattan, any ggplot2/matplotlib code, or figure quality complaints (labels overlap, text too small, colors clash)."
version: 3.3
tags: [plotting, visualization, bioinformatics, R, python, ggplot2, matplotlib]
related_skills: [plotting-library]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/sci-fig
compatibility: Requires Python 3.9+ with matplotlib, R with ggplot2 for recipes. plotting-library skill and /root/ops/plotting/ for execution.
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

### L5: 应用

后续绘图时，检查优先级：
1. 当前项目是否已指定palette？用那个
2. 用户是否为该图表类型发过示例图？优先用那个变体
3. 跟数据/分析场景匹配的变体？用那个
4. 都没有 → 用基础recipe + matplotlibrc默认风格

---

## 专业场景：APA与脑科学

### 场景决策树

```
你研究什么？
│
├─ APA（可变聚腺苷酸化）
│  ├─ PDUI跨条件对比 → apa_pattern (已有模板)
│  ├─ PDUI分布比较 → box_violin (已有模板)
│  ├─ 模式跨阶段流转 → sankey (已有模板)
│  ├─ 3'UTR长度分布 → stacked_area (新增)
│  ├─ 基因结构+APA位点 → gene_structure_apa (新增)
│  ├─ 全生命周期PDUI变化 → lifespan_trajectory (新增)
│  └─ APA事件基因集交集 → upset_plot (已有模板)
│
├─ 脑区表达分析
│  ├─ 单脑区热图 → heatmap_clustered (已有模板)
│  ├─ 多脑区热图+解剖标注 → brain_atlas_heatmap (新增)
│  ├─ 脑区×发育阶段矩阵 → lifespan_trajectory (新增)
│  └─ 单细胞marker → dot_plot_seurat (新增)
│
├─ 生命周期/发育
│  ├─ 连续趋势(多轨迹) → lifespan_trajectory (新增)
│  ├─ 组成比例变化 → stacked_area (新增)
│  └─ 多时间点分布 → ridgeline (已有模板)
│
└─ 临床/预后
   ├─ 生存分析 → km_survival (已有模板)
   ├─ 诊断ROC → roc_curve (已有模板)
   ├─ 多变量OR/HR → forest_plot (新增)
   └─ 基因突变位点 → lollipop (新增)
```

### 项目配色（按项目锁定）

**全生命周期APA项目（默认）**
```python
PROJECT_COLORS = {
    "Fetal": "#4DBBD5",       # 蓝-胎期
    "Neonatal": "#00A087",    # 绿-新生儿
    "Child": "#3C5488",      # 深蓝-儿童
    "Adolescent": "#F39B7F", # 粉橙-青少年
    "Adult": "#E64B35",      # 红-成年
    "Aged": "#8491B4",       # 灰紫-老年
}
PROJECT_CMAP = "mako"  # 连续色标(发育阶段)
```

```r
project_colors <- c(
  Fetal = "#4DBBD5", Neonatal = "#00A087", Child = "#3C5488",
  Adolescent = "#F39B7F", Adult = "#E64B35", Aged = "#8491B4"
)
```

**神经精神疾病项目**
```python
DISEASE_COLORS = {
    "Control": "#3C5488",
    "MDD": "#E64B35",
    "SCZ": "#4DBBD5",
    "BD": "#00A087",
    "ASD": "#F39B7F",
}
```

### 新增图表类型（优先级排序）

| 图表 | 模板名 | 数据类型 | 用途 |
|------|--------|---------|------|
| 全生命周期轨迹 | `lifespan_trajectory` | lifespan_trajectory | PDUI/表达随年龄的多轨迹变化 |
| 脑区热图+标注 | `brain_atlas_heatmap` | brain_region_matrix | 多脑区表达热图配解剖标注 |
| 基因结构+APA | `gene_structure_apa` | gene_apa_structure | 基因exon-intron + 3'UTR APA位点 |
| Seurat dot plot | `dot_plot_seurat` | marker_expression | 单细胞marker基因表达(点=比例,色=表达) |
| Forest plot | `forest_plot` | meta_analysis | 多变量OR/HR及置信区间 |
| Lollipop | `lollipop` | mutation_site | 基因突变/修饰位点标注 |
| Stacked area | `stacked_area` | composition_over_time | 组成比例随时间变化(APA usage%) |
| 染色体ideogram | `chromosome_ideogram` | genomic_region | 染色体区段标注(GWAS/QTL信号) |

### 脑科学绘图关键约定

1. **脑区命名统一**：使用Allen Brain Atlas标准名称(Frontal Cortex, Hippocampus, Cerebellum等)
2. **发育阶段色彩**：同一项目使用`PROJECT_COLORS`，Fetal→Aged渐变，连续变量用`mako` cmap
3. **3'UTR可视化**：exon用宽矩形，intron用细线(∩弧形表示)，PAS用▼三角标注，proximal=蓝，distal=红
4. **生存曲线**：神经退行性疾病用橙色线，对照组用蓝色；P值放在右下角
5. **脑区热图**：行按解剖位置排序(皮层上→皮层下→小脑)，不用默认聚类；列按发育阶段排

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