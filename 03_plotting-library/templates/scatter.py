"""
散点图 (Scatter Plot)
======================
展示两个连续变量之间的关系，支持分组着色、回归拟合线和边际密度图。

适用数据类型: relationship / quantitative_comparison
必需列: x, y
可选列: group, label, size

参考: Nature Methods, ggplot2 geom_point + geom_smooth
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from typing import Optional, Tuple, List, Union

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import (
    load_sci_style, save_fig, auto_label,
    apply_gallery_polish, polish_legend, SEMANTIC_COLORS
)

# ============ 参数配置 ============
# 语义配色 — 分组颜色（按出现顺序分配）
GROUP_PALETTE = [
    SEMANTIC_COLORS["proposed"],   # #0F4D92 深蓝
    SEMANTIC_COLORS["negative"],   # #E53935 红
    SEMANTIC_COLORS["positive"],   # #2E9E44 绿
    SEMANTIC_COLORS["baseline"],   # #3775BA 中蓝
    SEMANTIC_COLORS["neutral"],    # #8491B4 灰蓝
    "#F39B7F",                     # 橙粉（第6组+）
    "#8491B4",                     # 灰蓝
    "#00A087",                     # 青绿
]

# 分组 marker 形状
GROUP_MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]

POINT_SIZE = 28          # 默认散点大小
POINT_ALPHA = 0.75       # 散点透明度
POINT_EDGE_WIDTH = 0.5   # 散点边框宽度
LABEL_TOP_N = 8          # 标注 top N 个点
FIT_LINE_WIDTH = 1.5     # 拟合线宽度
MARGINAL_ALPHA = 0.5     # 边际直方图透明度


# ============ Mock data ============

def generate_mock_data(n=200, n_groups=3, seed=42):
    """生成演示数据：~200 个点，含 x, y, group 列。

    模拟基因表达 (TPM) 与 APA 位点 PDUI score 的关系，
    不同组代表不同发育阶段。
    """
    rng = np.random.default_rng(seed)
    group_names = ["Fetal", "Adult", "Aged"][:n_groups]

    frames = []
    per_group = n // n_groups
    for i, grp in enumerate(group_names):
        n_g = per_group if i < n_groups - 1 else n - per_group * (n_groups - 1)
        # 每组有不同的斜率和噪声
        slope = 0.8 + 0.3 * i
        intercept = 2.0 * i
        noise = 0.6 + 0.15 * i
        x = rng.uniform(0, 15, n_g)
        y = slope * x + intercept + rng.normal(0, noise, n_g)
        # 添加少量极端值用于 label 演示
        if n_g > 10:
            outlier_idx = rng.choice(n_g, size=min(3, n_g // 10), replace=False)
            y[outlier_idx] += rng.uniform(3, 6, len(outlier_idx))
        labels = [f"Gene_{grp[:3]}_{j}" for j in range(n_g)]
        frames.append(pd.DataFrame({
            "x": x, "y": y, "group": grp, "label": labels
        }))

    return pd.concat(frames, ignore_index=True)


# ============ Plotting ============

def _add_fit_line(ax, x, y, method="lm", color="0.3", **kwargs):
    """在 axes 上添加拟合线。

    Parameters
    ----------
    method : str, 'lm' (线性回归) 或 'loess' (LOESS/LOWESS 平滑)
    """
    order = np.argsort(x)
    xs = x[order]

    if method == "lm":
        # numpy polyfit degree-1
        coeffs = np.polyfit(x, y, 1)
        ys = np.polyval(coeffs, xs)
        ax.plot(xs, ys, color=color, lw=FIT_LINE_WIDTH, zorder=5, **kwargs)

        # R² 标注
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        ax.text(0.05, 0.95, f"R² = {r2:.3f}",
                transform=ax.transAxes, fontsize=plt.rcParams.get("font.size", 7) - 1,
                va="top", ha="left", color=color,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8))

    elif method in ("loess", "lowess"):
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            result = lowess(y, x, frac=0.3, return_sorted=True)
            ax.plot(result[:, 0], result[:, 1], color=color,
                    lw=FIT_LINE_WIDTH, zorder=5, **kwargs)
        except ImportError:
            # 回退：用 polynomial smoothing
            z = np.polyfit(x, y, 3)
            ys = np.polyval(z, xs)
            ax.plot(xs, ys, color=color, lw=FIT_LINE_WIDTH,
                    ls="--", zorder=5, **kwargs)


def _add_marginal_histograms(fig, ax, x, y, color="0.6"):
    """在主 axes 右侧和上方添加边际直方图（使用 inset axes）。"""
    # 创建与主 axes 共享 x / y 轴的 inset axes
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)

    # 顶部 — x 分布
    ax_top = divider.append_axes("top", size="18%", pad=0.08, sharex=ax)
    ax_top.hist(x, bins=30, color=color, alpha=MARGINAL_ALPHA,
                edgecolor="white", linewidth=0.3)
    ax_top.set_yticks([])
    ax_top.tick_params(axis="x", labelbottom=False, length=0)
    for spine in ax_top.spines.values():
        spine.set_visible(False)

    # 右侧 — y 分布
    ax_right = divider.append_axes("right", size="18%", pad=0.08, sharey=ax)
    ax_right.hist(y, bins=30, orientation="horizontal", color=color,
                  alpha=MARGINAL_ALPHA, edgecolor="white", linewidth=0.3)
    ax_right.set_xticks([])
    ax_right.tick_params(axis="y", labelleft=False, length=0)
    for spine in ax_right.spines.values():
        spine.set_visible(False)

    return ax_top, ax_right


def plot(
    df: pd.DataFrame,
    x_col: str = "x",
    y_col: str = "y",
    group_col: Optional[str] = "group",
    label_col: Optional[str] = "label",
    size_col: Optional[str] = None,
    colors: Optional[List[str]] = None,
    markers: Optional[List[str]] = None,
    fit: Optional[str] = None,          # 'lm', 'loess', or None
    marginal: bool = False,             # 添加边际直方图
    top_n: int = LABEL_TOP_N,           # 标注 top N 个点（按 y 值降序）
    figsize: Optional[Tuple[float, float]] = None,
    save_path: Optional[str] = None,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,       # e.g. "Expression (TPM)"
    ylabel: Optional[str] = None,       # e.g. "PDUI score"
    preset: str = "publication",
    point_size: float = POINT_SIZE,
    alpha: float = POINT_ALPHA,
):
    """
    绘制散点图

    Parameters
    ----------
    df : DataFrame, 必须包含 x 和 y 列
    x_col : str, x 轴列名
    y_col : str, y 轴列名
    group_col : str or None, 分组列名（None 则不分组）
    label_col : str or None, 标签列名（用于 auto_label）
    size_col : str or None, 点大小列名
    colors : list, 各组颜色（默认用 GROUP_PALETTE）
    markers : list, 各组 marker 形状（默认用 GROUP_MARKERS）
    fit : str or None, 'lm' 或 'loess'，拟合线方法
    marginal : bool, 是否添加边际直方图
    top_n : int, 标注 top N 个点
    figsize : tuple, 图片尺寸（英寸）
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选（支持子图拼接）
    title : str, 图标题
    xlabel : str, x 轴标签（含单位）
    ylabel : str, y 轴标签（含单位）
    preset : str, 'publication'|'gallery'|'presentation'|'draft'
    point_size : float, 散点大小
    alpha : float, 散点透明度
    """
    # 加载风格
    load_sci_style(preset)

    df = df.copy()
    if colors is None:
        colors = GROUP_PALETTE
    if markers is None:
        markers = GROUP_MARKERS

    # --- 分组逻辑 ---
    if group_col and group_col in df.columns:
        groups = df[group_col].unique().tolist()
        n_groups = len(groups)
    else:
        groups = [None]
        n_groups = 1

    # --- 创建 figure ---
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (8, 5.6) if preset == "gallery" else (5, 4)
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # --- 绘制散点 ---
    for i, grp in enumerate(groups):
        if grp is not None:
            mask = df[group_col] == grp
            sub = df[mask]
        else:
            sub = df

        x_vals = sub[x_col].values
        y_vals = sub[y_col].values
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]

        # 点大小
        if size_col and size_col in sub.columns:
            s = sub[size_col].values
            # 归一化到合理范围
            s_norm = 10 + (s - s.min()) / (s.max() - s.min() + 1e-9) * (point_size * 3)
        else:
            s_norm = point_size

        ax.scatter(
            x_vals, y_vals,
            c=color, s=s_norm, marker=marker,
            alpha=alpha, edgecolors="white", linewidths=POINT_EDGE_WIDTH,
            label=str(grp) if grp is not None else None,
            rasterized=True, zorder=3,
        )

    # --- 拟合线 ---
    if fit:
        if n_groups > 1 and group_col:
            for i, grp in enumerate(groups):
                mask = df[group_col] == grp
                x_vals = df.loc[mask, x_col].values
                y_vals = df.loc[mask, y_col].values
                _add_fit_line(ax, x_vals, y_vals, method=fit,
                              color=colors[i % len(colors)], label=None)
        else:
            _add_fit_line(ax, df[x_col].values, df[y_col].values,
                          method=fit, color="0.3")

    # --- 边际直方图 ---
    if marginal:
        if n_groups > 1:
            # 多组时用所有数据的灰色直方图
            _add_marginal_histograms(fig, ax,
                                     df[x_col].values, df[y_col].values,
                                     color="0.75")
        else:
            _add_marginal_histograms(fig, ax,
                                     df[x_col].values, df[y_col].values,
                                     color=colors[0])

    # --- auto_label ---
    if label_col and label_col in df.columns and top_n > 0:
        # 按 |y| 或 y 降序选择 top N
        top = df.nlargest(top_n, y_col)
        auto_label(
            ax,
            texts=top[label_col].tolist(),
            x=top[x_col].tolist(),
            y=top[y_col].tolist(),
            fontsize=plt.rcParams.get("font.size", 7) - 1,
        )

    # --- 轴标签 ---
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if title:
        ax.set_title(title, fontweight="bold", pad=8)

    # --- 图例 + polish ---
    if n_groups > 1:
        polish_legend(ax, ncol=min(n_groups, 3), loc="best")
    apply_gallery_polish(ax)

    # --- 保存 ---
    if save_path:
        save_fig(ax.figure if external_ax else fig,
                 Path(save_path).stem.replace("_demo", ""),
                 transparent=False)

    return ax


# ============ CLI / Demo ============

if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig

    load_sci_style("gallery")

    # --- Demo 1: 分组散点 + lm 拟合线 ---
    df = generate_mock_data(n=200, n_groups=3)
    fig, ax = plt.subplots(figsize=(8, 5.6))
    ax = plot(
        df,
        x_col="x", y_col="y", group_col="group", label_col="label",
        fit="lm", marginal=False, top_n=5,
        xlabel="Expression (TPM)", ylabel="PDUI score",
        preset="gallery", ax=ax,
        title="Gene Expression vs. APA PDUI Score",
    )
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)

    # --- Demo 2: 单组散点 + 边际直方图 + loess ---
    df_single = df[df["group"] == "Adult"].copy()
    fig2, ax2 = plt.subplots(figsize=(8, 5.6))
    ax2 = plot(
        df_single,
        x_col="x", y_col="y", group_col=None, label_col="label",
        fit="loess", marginal=True, top_n=3,
        xlabel="Expression (TPM)", ylabel="PDUI score",
        preset="gallery", ax=ax2,
        title="Adult: Expression vs. PDUI (with marginals)",
    )
    save_fig(ax2.figure, f"{name}_marginal", dpi=180, fmt="both")
    plt.close(ax2.figure)

    print("Scatter demos saved.")
