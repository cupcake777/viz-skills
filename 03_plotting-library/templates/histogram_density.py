"""
直方图 + 密度曲线叠加图 (Histogram + Density Overlay)
=====================================================
叠加多组连续变量的直方图与KDE密度曲线，展示分布形态对比。
可选添加rug marks和均值/中位数参考线。

适用数据类型: numeric_vector / distribution_comparison
必需列: value
可选列: group

参考: Nature Methods, seaborn histplot + kdeplot
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
from typing import Optional, Tuple, List

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import (
    load_sci_style, save_fig, polish_legend,
    apply_gallery_polish, SEMANTIC_COLORS
)

# ============ 参数配置 ============

# 分组配色：用SEMANTIC_COLORS为主，补充Nature色板
GROUP_COLORS = [
    SEMANTIC_COLORS["proposed"],    # #0F4D92 深蓝 — Control
    SEMANTIC_COLORS["negative"],    # #E53935 红   — Treatment
    SEMANTIC_COLORS["positive"],    # #2E9E44 绿
    SEMANTIC_COLORS["baseline"],    # #3775BA 中蓝
    SEMANTIC_COLORS["neutral"],     # #8491B4 灰蓝
    "#F39B7F",                      # 橙粉
]

HIST_ALPHA = 0.6          # 直方图透明度
HIST_EDGEWIDTH = 0.6      # 直方图边框宽度
KDE_LINEWIDTH = 1.8       # KDE曲线宽度
RUG_HEIGHT = 0.03         # rug mark高度（占轴比例）
RUG_ALPHA = 0.4           # rug mark透明度
STAT_LINEWIDTH = 1.4      # 均值/中位数线宽


# ============ Mock data ============

def generate_mock_data(n_per_group=500, seed=42):
    """生成演示数据：两组基因表达量（~500个连续值）。

    模拟Control vs Treatment条件下的基因表达(log2 TPM)，
    Control为正态分布，Treatment均值偏移且略有偏态。
    """
    rng = np.random.default_rng(seed)

    # Control: mean=6.5, std=1.4（正态）
    control = rng.normal(6.5, 1.4, n_per_group)
    # Treatment: mean=8.2, std=1.8（略右偏）
    treatment = rng.normal(8.2, 1.8, n_per_group)

    values = np.concatenate([control, treatment])
    groups = (["Control"] * n_per_group + ["Treatment"] * n_per_group)

    return pd.DataFrame({"value": values, "group": groups})


# ============ Plotting ============

def plot(
    df: pd.DataFrame,
    value_col: str = "value",
    group_col: Optional[str] = "group",
    colors: Optional[List[str]] = None,
    bins: int = 40,
    kde: bool = True,
    rug: bool = False,
    stat_lines: Optional[str] = None,   # "mean", "median", or None
    figsize: Optional[Tuple[float, float]] = None,
    save_path: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    preset: str = "publication",
):
    """
    绘制直方图 + 密度曲线叠加图

    Parameters
    ----------
    df : DataFrame, 必须包含 value 列
    value_col : str, 数值列名
    group_col : str or None, 分组列名（None 则单组直方图）
    colors : list, 各组颜色
    bins : int, 直方图bin数
    kde : bool, 是否叠加KDE密度曲线
    rug : bool, 是否添加rug marks
    stat_lines : str or None, "mean"/"median" 添加垂直参考线
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    title : str, 图标题
    xlabel : str, x轴标签（含单位）
    ylabel : str, y轴标签（含单位）
    preset : str, 'publication'|'gallery'|'presentation'|'draft'
    """
    # 加载风格
    load_sci_style(preset)

    df = df.copy()
    if colors is None:
        colors = GROUP_COLORS

    # --- 分组逻辑 ---
    if group_col and group_col in df.columns:
        groups = sorted(df[group_col].unique().tolist())
    else:
        groups = [None]

    # --- 创建 figure ---
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (8, 5.6) if preset == "gallery" else (5, 4)
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # --- 计算全局bin范围（所有组统一） ---
    all_vals = df[value_col].dropna().values
    bin_edges = np.linspace(all_vals.min(), all_vals.max(), bins + 1)

    # --- 绘制直方图 + KDE ---
    legend_handles = []

    for i, grp in enumerate(groups):
        if grp is not None:
            mask = df[group_col] == grp
            vals = df.loc[mask, value_col].dropna().values
        else:
            vals = df[value_col].dropna().values

        color = colors[i % len(colors)]

        # 直方图（density=True 归一化）
        ax.hist(
            vals, bins=bin_edges, density=True,
            alpha=HIST_ALPHA, color=color,
            edgecolor="white", linewidth=HIST_EDGEWIDTH,
            label=str(grp) if grp is not None else None,
            zorder=2,
        )

        # KDE 曲线
        if kde:
            try:
                from scipy.stats import gaussian_kde
                kde_func = gaussian_kde(vals)
                x_range = np.linspace(bin_edges[0], bin_edges[-1], 300)
                kde_vals = kde_func(x_range)
                ax.plot(
                    x_range, kde_vals,
                    color=color, linewidth=KDE_LINEWIDTH,
                    solid_capstyle="round", zorder=4,
                )
            except ImportError:
                pass  # scipy不可用时跳过KDE

        # Rug marks
        if rug:
            rug_y = np.full_like(vals, 0, dtype=float)
            ax.plot(
                vals, rug_y, "|",
                color=color, markersize=4,
                alpha=RUG_ALPHA, zorder=1,
            )

        # 均值/中位数线
        if stat_lines == "mean":
            mu = np.mean(vals)
            ax.axvline(
                mu, color=color, linewidth=STAT_LINEWIDTH,
                linestyle="--", alpha=0.85, zorder=5,
            )
            # 标注
            ax.text(
                mu, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 0.95,
                f"μ={mu:.2f}", color=color, fontsize=8,
                ha="center", va="top", fontweight="bold",
            )
        elif stat_lines == "median":
            med = np.median(vals)
            ax.axvline(
                med, color=color, linewidth=STAT_LINEWIDTH,
                linestyle=":", alpha=0.85, zorder=5,
            )
            ax.text(
                med, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 0.95,
                f"Md={med:.2f}", color=color, fontsize=8,
                ha="center", va="top", fontweight="bold",
            )

    # --- 轴标签 ---
    ax.set_xlabel(xlabel if xlabel else value_col)
    ax.set_ylabel(ylabel if ylabel else "Density")
    if title:
        ax.set_title(title, fontweight="bold", pad=8)

    # --- rug 时调整y轴下限 ---
    if rug:
        ax.set_ylim(bottom=-RUG_HEIGHT * ax.get_ylim()[1])

    # --- 图例 + polish ---
    apply_gallery_polish(ax)
    polish_legend(ax, ncol=min(len(groups), 3), loc="best")

    # --- 保存 ---
    if save_path:
        save_fig(
            ax.figure if external_ax else fig,
            Path(save_path).stem.replace("_demo", ""),
            transparent=False,
        )

    return ax


# ============ CLI / Demo ============

if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig

    load_sci_style("gallery")

    df = generate_mock_data(n_per_group=500)

    # --- Demo 1: 标准直方图 + KDE ---
    fig, ax = plt.subplots(figsize=(8, 5.6))
    ax = plot(
        df,
        value_col="value", group_col="group",
        bins=40, kde=True, rug=False, stat_lines="mean",
        xlabel="Gene Expression (log₂ TPM)",
        ylabel="Density",
        preset="gallery", ax=ax,
        title="Gene Expression Distribution: Control vs Treatment",
    )
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)

    # --- Demo 2: 带 rug marks + 中位数线 ---
    fig2, ax2 = plt.subplots(figsize=(8, 5.6))
    ax2 = plot(
        df,
        value_col="value", group_col="group",
        bins=35, kde=True, rug=True, stat_lines="median",
        xlabel="Gene Expression (log₂ TPM)",
        ylabel="Density",
        preset="gallery", ax=ax2,
        title="Distribution with Rug Marks & Median Lines",
    )
    save_fig(ax2.figure, f"{name}_rug", dpi=180, fmt="both")
    plt.close(ax2.figure)

    print("Histogram + density demos saved.")
