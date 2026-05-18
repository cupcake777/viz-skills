"""
堆叠面积图 (Stacked Area Chart)
================================
展示跨发育阶段/时间点的组分构成变化。
适用于APA proximal vs distal usage、转录本亚型比例、细胞类型丰度等场景。

适用数据类型: composition_table
必需列: stage, component, proportion
可选列: confidence_low, confidence_high

参考: 自定义（APA lifespan composition）
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish, polish_legend,
    SEMANTIC_COLORS, APA_STAGE_COLORS,
)

# ============ 参数配置 ============
STAGES = ["Fetal", "Neonatal", "Infant", "Child", "Adolescent", "Adult"]

# 组分定性配色 — 避免与APA_STAGE_COLORS冲突，使用Set2/NPG风格
COMPONENT_COLORS = [
    "#E64B35",  # 红
    "#4DBBD5",  # 青
    "#00A087",  # 绿
    "#3C5488",  # 蓝
    "#F39B7F",  # 橙
]


def generate_mock_data(seed=42):
    """生成APA proximal/distal usage构成数据。

    模拟5种3'UTR亚型在6个发育阶段的比例变化，
    每个stage的proportion之和 = 1.0。
    """
    rng = np.random.default_rng(seed)
    components = [
        "Proximal PA site",
        "Distal PA site",
        "Intronic PA site",
        "Composite PA site",
        "Tandem UTR",
    ]
    n_stages = len(STAGES)
    n_comp = len(components)

    # 生成logistic-like趋势，确保和为1
    raw = np.zeros((n_stages, n_comp))
    # Proximal: 低→高
    raw[:, 0] = np.linspace(0.15, 0.45, n_stages)
    # Distal: 高→低
    raw[:, 1] = np.linspace(0.50, 0.20, n_stages)
    # Intronic: 稳定偏低
    raw[:, 2] = np.full(n_stages, 0.10) + rng.normal(0, 0.02, n_stages)
    # Composite: 先升后降
    raw[:, 3] = 0.05 + 0.15 * np.sin(np.linspace(0, np.pi, n_stages))
    # Tandem UTR: 补余
    raw[:, 4] = 1.0 - raw[:, :4].sum(axis=1)

    # 加微量噪声后归一化
    raw += rng.normal(0, 0.01, raw.shape)
    raw = np.clip(raw, 0.01, None)
    raw /= raw.sum(axis=1, keepdims=True)

    records = []
    for i, stage in enumerate(STAGES):
        for j, comp in enumerate(components):
            records.append({
                "stage": stage,
                "component": comp,
                "proportion": round(raw[i, j], 4),
            })
    return pd.DataFrame(records)


def plot(df, stage_col="stage", comp_col="component", val_col="proportion",
         stages=None, component_colors=None,
         figsize=None, save_path=None, ax=None, preset="publication"):
    """
    绘制堆叠面积图

    Parameters
    ----------
    df : DataFrame
    stage_col : str, 阶段/时间轴列
    comp_col : str, 组分类别列
    val_col : str, 比例列（每个stage内应求和为1）
    stages : list or None, x轴阶段顺序（默认STAGES）
    component_colors : list or None, 组分配色
    figsize : tuple or None
    save_path : str or None
    ax : matplotlib Axes or None
    preset : str, 风格preset
    """
    load_sci_style(preset)

    if stages is None:
        stages = df[stage_col].unique().tolist()
    components = df[comp_col].unique().tolist()
    if component_colors is None:
        component_colors = COMPONENT_COLORS[:len(components)]

    # 构建pivot: rows=stage_idx, cols=components
    pivot = df.pivot(index=stage_col, columns=comp_col, values=val_col)
    pivot = pivot.reindex(stages)
    pivot = pivot[components]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(stages))

    # 计算累积底部边界
    cumulative = np.zeros(len(stages))
    for i, comp in enumerate(components):
        values = pivot[comp].values
        color = component_colors[i % len(component_colors)]
        ax.fill_between(x, cumulative, cumulative + values,
                        alpha=0.82, color=color, label=comp,
                        edgecolor="white", linewidth=0.8)
        cumulative += values

    # X轴
    ax.set_xticks(x)
    ax.set_xticklabels(stages, rotation=0)
    ax.set_xlim(x[0], x[-1])

    # Y轴 — 百分比格式
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Proportion")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v:.0%}")
    )

    ax.set_title("APA Isoform Composition Across Lifespan")

    apply_gallery_polish(ax)
    polish_legend(ax, ncol=1, loc="upper right")

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df = generate_mock_data()
    ax = plot(df, preset="gallery")
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
