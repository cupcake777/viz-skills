# 生信绘图网站调研：三方平台对比

> 调研时间: 2026-05-09
> 来源: SRplot (bioinformatics.com.cn), ChiPlot (chiplot.online), Bioincloud (bioincloud.tech)

## 平台概况

| 维度 | SRplot (微生信) | ChiPlot | Bioincloud (微科盟) |
|------|----------------|---------|---------------------|
| 图表总数 | 120+ | ~41 | 100+ |
| 生信特色 | 多(GO/KEGG/富集变体多) | 强(树/圈图/基因簇) | 强(宏基因组/多样性) |
| 技术栈 | R (ggplot2系) | D3.js前端交互 | R (Shiny/plotly) |
| 配色 | npg/lancet/aaas/jama等 | 默认 | 默认 |
| 输出 | PDF/SVG/PNG/TIFF | SVG/PNG | PDF/PNG |
| 特色 | 种类最全, 2000+引用 | 树可视化最强, 基因簇/共线性 | 流程化分析, 多组学联动 |

## SRplot 完整图表分类 (120+)

### Basic Plot (基础图)
2D Pie, 3D Pie, Donut, Funnel, Rectangle Funnel, Horizontal Bar, Vertical Bar,
Stacked Bar, Grouped Bar, Dot Bar (水平点图), Left-Right Bidirectional Bar,
Line, Smooth Line, Multi-line, Area, Stem Plot, Scatter, 3D Scatter,
Quadrant Scatter, Histogram, Box Plot, Horizontal Box, Violin, Ridgeline,
Raincloud, QQ Plot, Correlation Plot, Dendrogram

### Genome (基因组)
SNP Density, Chromosome Distribution, Peak Venn, Circos Plot

### Transcriptome (转录组)
Heatmap, Volcano (3-color, enhanced), MA Plot

### Enrichment (富集分析)
GO/KEGG Enrichment Bubble, GO BP/CC/MF 3-in-1, GO Chord, Enrichment Bar,
GSEA, Pathway Enrichment Category

### Epigenome (表观遗传)
Metagene Plot, Peak Annotation

### Clinical (临床)
KM Survival, Forest Plot, ROC, Risk Score Tri-Phase

### Motif
MEME Motif, Sequence Logo

### Network/Relation
Sankey, Alluvial, Venn (2-7 sets), Proportional Venn, UpSet, Chord,
CircRNA-miRNA Ring, Multi-layer Circle Network, Three-layer Network

### Special
Lollipop, Waterfall, Radar, China Map, Flower Plot, Gene Up/Down Bar,
Ternary Plot, Four Quadrant Scatter, Gene Structure

## ChiPlot 图表清单 (41)

### Phylogenetic Tree (4)
Normal layout, Circular layout, Unrooted layout, TVBOT

### BioPlot (8)
Gene Cluster, Conserved Domains (NCBI CDD), Motif (MEME), Circos,
Volcano, KEGG/GO Enrichment, Circle Enrichment, McScanX Synteny

### Statistics (29)
Network Plot, Map Plot, Scatter (+error bar), PCA, NMDS, RDA,
Line (group), Bar (+category, +error bar, group error bar),
Box, Group Box, Violin, Raincloud, Ridgeline,
Pie, Radar, Heatmap, Circle Heatmap, Correlation Heatmap,
Double Matrices Correlation, Mantel Test Correlation,
Dumbbell, Bubble, Sankey, Lollipop, UpSet

## Bioincloud 特色图表 (100+)

### 基础统计 (核心新增)
Circos圈图, 瀑布图(Oncoplot), MA-图, 蜂群图(Beeswarm), 三元相图,
九象限图, 环状条形图, 环状热图, 网格热图, 堆叠连线柱状图/河流图,
核密度估计边际图, 花瓣图, 动态物种丰度桑基图

### 排序分析
PCA, NMDS/PCoA (Bray-Curtis/UniFrac), dbRDA, tSNE, UMAP

### 显著性差异
T检验火山图, DESeq2/edgeR火山图, OPLS-DA, PLS-DA, ANOVA,
Kruskal-Wallis, LEfSe, Cox生存分析

### 富集分析
GO GSEA, GO ORA, KEGG GSEA, KEGG ORA, 动态富集圈图

### 进化
系统发育树, 带热图的物种进化树, 动态变异热图

## 调研来源与配色参考

### SRplot 内置配色
- `npg`: Nature Publishing Group (#E64B35, #4DBBD5, #00A087, #3C5488, #F39B7F, #8491B4)
- `lancet`: Lancet (#00468B, #ED0000, #925E9F, #925E9F)  
- `aaas`: AAAS/Science (#3B4992, #EE0000, #008B45, #631879)
- `jama`: JAMA (#374E55, #DF8F44, #00A1D5, #B24745)
- `jmco`: JCO (#0073B0, #E8322E, #A62750)
- `frontiers`: Frontiers (#4A6DB5, #E3642D, #2AA176)

### SRplot 图表数据格式共性
- 制表符分隔的TXT/XLSX
- 第一行为表头
- 第一列通常为名称/ID
- 支持直接粘贴或文件上传
- 所有图表支持PDF/SVG/PNG/TIFF输出