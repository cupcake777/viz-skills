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
