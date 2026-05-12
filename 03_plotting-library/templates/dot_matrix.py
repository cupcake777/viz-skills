"""
Dot Matrix (Size + Color Encoding)
====================================
Displays a matrix of circles where SIZE encodes one metric and COLOR encodes
another. Inspired by scib benchmarking (Nature Methods 2022) dot plots used
to compare batch integration methods across multiple evaluation metrics.

Applicable data type: benchmarking / multi-metric comparison
Required data: size_values (DataFrame, rows x cols), color_values (DataFrame, rows x cols)
Optional: row_labels, col_labels

Reference: Luecken et al., Nature Methods 2022 — scib benchmarking framework
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from pathlib import Path
from typing import Optional, Tuple, List, Union

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig,
    apply_gallery_polish, polish_legend, SEMANTIC_COLORS
)

# ============ 参数配置 ============
ROW_BAND_ALPHA = 0.06          # 交替行背景条透明度
ROW_BAND_COLOR = "#AAAAAA"      # 行背景条颜色
DOT_EDGE_COLOR = "#333333"      # 圆点边框颜色
DOT_EDGE_WIDTH = 0.5            # 圆点边框宽度
DOT_ALPHA = 0.85                # 圆点透明度
DEFAULT_CMAP = "RdYlBu_r"      # 默认色图
DEFAULT_SIZE_RANGE = (20, 200)  # 圆点面积范围 (pt^2)
SIZE_LEGEND_COUNT = 4           # 尺寸图例参考圆数量
TICK_LABEL_SIZE = 9


# ============ Mock data ============

def generate_mock_data(seed=42):
    """生成演示数据：8 种整合方法 x 5 个评估指标的 size/color 评分。

    模拟 scib 基准测试场景：
    - size_df: 方法在各指标上的综合得分 (如 mean score)
    - color_df: 方法在各指标上的另一维度得分 (如生物保守性)
    """
    rng = np.random.RandomState(seed)

    methods = ["scVI", "Harmony", "Scanorama", "BBKNN",
               "LIGER", "Combat", "MNN", "scGen"]
    metrics = ["Bio conservation", "Batch correction",
               "Silhouette", "ARI", "NMI"]

    size_values = rng.rand(len(methods), len(metrics))
    color_values = rng.rand(len(methods), len(metrics))

    size_df = pd.DataFrame(size_values, index=methods, columns=metrics)
    color_df = pd.DataFrame(color_values, index=methods, columns=metrics)
    return size_df, color_df


# ============ Plot function ============

def plot(size_df, color_df, row_labels=None, col_labels=None,
         cmap=None, size_range=None, title=None,
         xlabel=None, ylabel=None, figsize=None, save_path=None,
         ax=None, preset="publication"):
    """绘制 size+color 双编码点阵图。

    Parameters
    ----------
    size_df : pd.DataFrame or np.ndarray
        数值矩阵，行=方法，列=指标。值域 [0, 1]，控制圆点大小。
    color_df : pd.DataFrame or np.ndarray
        同形矩阵。值域 [0, 1]，控制圆点填充颜色。
    row_labels : list of str, optional
        行标签（方法名称）。若为 None 则从 DataFrame index 读取。
    col_labels : list of str, optional
        列标签（指标名称）。若为 None 则从 DataFrame columns 读取。
    cmap : str or Colormap, optional
        色图名称，默认 RdYlBu_r。
    size_range : tuple of (float, float), optional
        圆点面积范围 (min_size, max_size)，单位 pt^2。
    title : str, optional
    xlabel, ylabel : str, optional
    figsize : tuple, optional
    save_path : str, optional
    ax : matplotlib Axes, optional
    preset : str
        'publication' | 'gallery'

    Returns
    -------
    ax : matplotlib Axes
    """
    if cmap is None:
        cmap = DEFAULT_CMAP
    if size_range is None:
        size_range = DEFAULT_SIZE_RANGE

    # Convert to numpy if needed
    if isinstance(size_df, pd.DataFrame):
        if row_labels is None:
            row_labels = list(size_df.index)
        if col_labels is None:
            col_labels = list(size_df.columns)
        size_arr = size_df.values
    else:
        size_arr = np.asarray(size_df)

    if isinstance(color_df, pd.DataFrame):
        color_arr = color_df.values
    else:
        color_arr = np.asarray(color_df)

    n_rows, n_cols = size_arr.shape

    if row_labels is None:
        row_labels = [f"Row {i}" for i in range(n_rows)]
    if col_labels is None:
        col_labels = [f"Col {j}" for j in range(n_cols)]

    # Create figure/axes
    if ax is None:
        if figsize is None:
            figsize = (max(6, n_cols * 1.2 + 3), max(4, n_rows * 0.55 + 2))
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # ---- Alternating row background bands ----
    for i in range(n_rows):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=ROW_BAND_COLOR,
                       alpha=ROW_BAND_ALPHA, zorder=0, linewidth=0)

    # ---- Build scatter coordinates ----
    xs, ys, sizes, colors = [], [], [], []
    smin, smax = size_range

    for i in range(n_rows):
        for j in range(n_cols):
            xs.append(j)
            ys.append(i)
            # Normalize size: scale [0,1] -> [smin, smax]
            sizes.append(smin + size_arr[i, j] * (smax - smin))
            colors.append(color_arr[i, j])

    sc = ax.scatter(
        xs, ys, s=sizes, c=colors, cmap=cmap,
        edgecolors=DOT_EDGE_COLOR, linewidths=DOT_EDGE_WIDTH,
        alpha=DOT_ALPHA, zorder=3,
        vmin=0, vmax=1,
    )

    # ---- Axes formatting ----
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, rotation=35, ha="right",
                       fontsize=TICK_LABEL_SIZE)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=TICK_LABEL_SIZE)
    ax.set_xlim(-0.6, n_cols - 0.4)
    ax.set_ylim(n_rows - 0.5, -0.5)  # top row first
    ax.tick_params(length=0)

    # Grid lines
    for j in range(n_cols):
        ax.axvline(j, color="#E0E0E0", linewidth=0.5, zorder=1, clip_on=False)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # ---- Colorbar ----
    cbar = fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.04, shrink=0.8)
    cbar.set_label("Color metric", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    # ---- Size legend ----
    legend_vals = np.linspace(0, 1, SIZE_LEGEND_COUNT)
    legend_elements = []
    for v in legend_vals:
        sz = smin + v * (smax - smin)
        legend_elements.append(
            Line2D([0], [0], marker="o", color="w",
                   markerfacecolor="#BBBBBB",
                   markeredgecolor=DOT_EDGE_COLOR,
                   markeredgewidth=DOT_EDGE_WIDTH,
                   markersize=np.sqrt(sz) * 0.55,
                   label=f"{v:.1f}")
        )
    leg = ax.legend(
        handles=legend_elements,
        title="Size metric",
        loc="upper left",
        bbox_to_anchor=(1.18, 1.0),
        frameon=True,
        fontsize=8,
        title_fontsize=9,
        borderpad=0.8,
        handletextpad=0.6,
    )
    leg.get_frame().set_linewidth(0.5)

    # Spine cleanup
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
        spine.set_color("#CCCCCC")

    if preset == "gallery":
        apply_gallery_polish(ax)

    return ax


# ============ Main ============

if __name__ == "__main__":
    load_sci_style("gallery")

    size_df, color_df = generate_mock_data()

    ax = plot(
        size_df, color_df,
        cmap="RdYlBu_r",
        size_range=(30, 220),
        title="scib Benchmark: Method × Metric Dot Matrix",
        xlabel="Evaluation Metric",
        ylabel="Integration Method",
        preset="gallery",
    )

    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
    print("Dot matrix demo saved.")
