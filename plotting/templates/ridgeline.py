"""
山脊图 (Ridgeline / Joy Plot)
==============================
展示不同发育阶段基因表达密度分布的纵向堆叠，模拟时间序列变化趋势。

适用数据类型: time_series_distribution / expression_profile
必需列: stage, value
可选列: gene, cell_type

参考: ggridge, Joy Division Album Cover
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import gaussian_kde

from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS

# ============ 参数配置 ============
STAGES = ["E15", "P1", "P7", "P30", "Adult", "Elderly"]


def generate_mock_data(n_per_stage=200, seed=42):
    """生成演示数据: 6个发育阶段的基因表达量，均值逐步偏移"""
    rng = np.random.default_rng(seed)

    params = [
        (2.0, 0.8),   # E15: 低表达
        (3.5, 1.0),   # P1: 上升
        (5.5, 1.2),   # P7: 峰值前期
        (7.0, 1.5),   # P30: 高表达
        (6.0, 1.8),   # Adult: 略降但分散
        (4.0, 2.2),   # Elderly: 下降且变异大
    ]

    stages = []
    values = []
    for stage, (mu, sigma) in zip(STAGES, params):
        vals = rng.normal(mu, sigma, n_per_stage)
        if stage in ["P30", "Adult"]:
            vals = np.concatenate([vals, rng.normal(mu + 2, 0.5, int(n_per_stage * 0.2))])
        stages.extend([stage] * len(vals))
        values.extend(vals)

    return pd.DataFrame({"stage": stages, "value": values})


def plot(df, stage_col="stage", value_col="value", stages=None,
         colors=None, overlap=0.7, n_points=300,
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制山脊图

    Parameters
    ----------
    df : DataFrame, 必须包含 stage 和 value 列
    stage_col : str, 发育阶段列名
    value_col : str, 数值列名
    stages : list, 阶段顺序
    colors : list, 各阶段颜色
    overlap : float, 曲线重叠程度 (0-1)
    n_points : int, KDE采样点数
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if stages is None:
        stages = STAGES
    if colors is None:
        colors = NATURE_COLORS

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # 统一x范围
    all_vals = df[value_col].values
    x_min, x_max = np.nanmin(all_vals) - 1, np.nanmax(all_vals) + 1
    x_grid = np.linspace(x_min, x_max, n_points)

    # 计算最大密度用于归一化
    max_density = 0
    kdes = {}
    for stage in stages:
        vals = df.loc[df[stage_col] == stage, value_col].dropna().values
        if len(vals) < 3:
            continue
        kde = gaussian_kde(vals, bw_method=0.3)
        density = kde(x_grid)
        kdes[stage] = density
        max_density = max(max_density, density.max())

    # 绘制山脊图 (从下到上)
    spacing = overlap * max_density
    for i, stage in enumerate(stages):
        if stage not in kdes:
            continue
        density = kdes[stage]
        y_offset = i * spacing
        color = colors[i % len(colors)]

        alpha = 0.4 + 0.3 * (i / len(stages))
        ax.fill_between(x_grid, y_offset, density + y_offset,
                        alpha=alpha, color=color, linewidth=0)
        ax.plot(x_grid, density + y_offset, color=color, linewidth=1.2)

        ax.text(x_min - 0.3, y_offset + spacing * 0.1, stage,
                fontweight="bold", color=color,
                ha="right", va="bottom")

    ax.set_xlim(x_min - 2, x_max)
    ax.set_ylim(-spacing * 0.3, len(stages) * spacing + spacing)
    ax.set_xlabel("Expression Level (log₂ TPM)")
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.set_title("Gene Expression Density Across Developmental Stages")
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    df = generate_mock_data()
    plot(df, save_path="ridgeline_demo.png")
    plt.close()
