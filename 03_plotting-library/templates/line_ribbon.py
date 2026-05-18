"""
Line with Confidence Ribbon (Line + CI Ribbon)
===============================================
展示跨有序轴（时间、发育阶段、剂量等）的趋势变化，带多层置信区间色带。

适用数据类型: ordered_series
必需列: stage, group, y_mean, y_lo, y_hi
可选列: y_lo95, y_hi95 (宽CI层)

参考: 自定义（APA 3'UTR length across lifespan）
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish, polish_legend,
    APA_STAGE_COLORS,
)

# ============ 参数配置 ============
STAGES = ["Fetal", "Neonatal", "Infant", "Child", "Adolescent", "Adult", "Aged"]
GROUPS = ["Neuron", "Glia"]
GROUP_COLORS = {"Neuron": "#E64B35", "Glia": "#4DBBD5"}

# CI层透明度 — 外层(95%)更淡，内层(68%)更深
CI_LEVELS = [
    {"suffix": "95", "alpha": 0.12, "label": "95% CI"},
    {"suffix": "68", "alpha": 0.28, "label": "68% CI"},
]


def generate_mock_data(seed=42):
    """生成3'UTR长度跨发育阶段的趋势数据。

    模拟Neuron和Glia两组在7个发育阶段的均值和置信区间，
    展现先升后降的发育趋势。
    """
    rng = np.random.default_rng(seed)
    n_stages = len(STAGES)
    records = []

    # 基础趋势：3'UTR长度在发育中期达到峰值
    base_trend = np.array([1.2, 1.8, 2.4, 2.8, 2.5, 2.0, 1.6])

    for grp in GROUPS:
        offset = 0.3 if grp == "Neuron" else 0.0
        scale_ci = 0.25 if grp == "Neuron" else 0.30

        for i, stage in enumerate(STAGES):
            y_mean = base_trend[i] + offset + rng.normal(0, 0.08)
            # 68% CI (±1σ)
            ci_68 = scale_ci * (0.8 + 0.3 * rng.random())
            y_lo68 = y_mean - ci_68
            y_hi68 = y_mean + ci_68
            # 95% CI (±1.96σ)
            ci_95 = ci_68 * 1.96
            y_lo95 = y_mean - ci_95
            y_hi95 = y_mean + ci_95

            records.append({
                "stage": stage,
                "group": grp,
                "y_mean": round(y_mean, 3),
                "y_lo": round(y_lo68, 3),
                "y_hi": round(y_hi68, 3),
                "y_lo95": round(y_lo95, 3),
                "y_hi95": round(y_hi95, 3),
            })

    return pd.DataFrame(records)


def plot(df, stage_col="stage", group_col="group",
         mean_col="y_mean", lo_col="y_lo", hi_col="y_hi",
         lo95_col="y_lo95", hi95_col="y_hi95",
         stages=None, group_colors=None,
         xlabel="Developmental Stage", ylabel="3'UTR Length (kb)",
         title=None,
         figsize=None, save_path=None, ax=None, preset="publication"):
    """
    绘制带多层置信区间色带的折线图

    Parameters
    ----------
    df : DataFrame
    stage_col : str, 有序阶段列（x轴）
    group_col : str, 分组列
    mean_col : str, 均值列（y轴）
    lo_col, hi_col : str, 窄CI列（68%）
    lo95_col, hi95_col : str or None, 宽CI列（95%）
    stages : list or None, x轴阶段顺序
    group_colors : dict or None, 分组配色
    xlabel, ylabel : str, 坐标轴标签
    title : str or None, 图标题
    figsize : tuple or None
    save_path : str or None
    ax : matplotlib Axes or None
    preset : str, 风格preset
    """
    load_sci_style(preset)

    if stages is None:
        stages = df[stage_col].unique().tolist()
    groups = df[group_col].unique().tolist()
    if group_colors is None:
        group_colors = GROUP_COLORS

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(stages))

    for grp in groups:
        sub = df[df[group_col] == grp].set_index(stage_col).reindex(stages)
        color = group_colors.get(grp, "#8491B4")
        y_mean = sub[mean_col].values
        y_lo = sub[lo_col].values
        y_hi = sub[hi_col].values

        # 95% CI ribbon（外层，更淡）
        has_95 = lo95_col in sub.columns and hi95_col in sub.columns
        if has_95:
            y_lo95 = sub[lo95_col].values
            y_hi95 = sub[hi95_col].values
            ax.fill_between(x, y_lo95, y_hi95,
                            color=color, alpha=0.12, linewidth=0,
                            label="_nolegend_")

        # 68% CI ribbon（内层，更深）
        ax.fill_between(x, y_lo, y_hi,
                        color=color, alpha=0.28, linewidth=0,
                        label="_nolegend_")

        # 均值连线 + 标记
        ax.plot(x, y_mean, color=color, linewidth=1.8,
                marker="o", markersize=5, markeredgecolor="white",
                markeredgewidth=0.6, label=grp, zorder=3)

    # X轴：阶段标签 + 底部色条
    ax.set_xticks(x)
    ax.set_xticklabels(stages, rotation=25, ha="right")
    ax.set_xlim(x[0] - 0.3, x[-1] + 0.3)

    # 底部色条：为每个stage绘制彩色tick
    for i, stage in enumerate(stages):
        stage_color = APA_STAGE_COLORS.get(stage, "#CCCCCC")
        ax.plot(i, ax.get_ylim()[0], marker="|", markersize=14,
                markeredgewidth=3, color=stage_color, clip_on=False,
                zorder=0)

    # Y轴
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)

    # CI图例说明（手动构建）
    from matplotlib.lines import Line2D
    legend_handles = []
    for grp in groups:
        color = group_colors.get(grp, "#8491B4")
        legend_handles.append(
            Line2D([0], [0], color=color, linewidth=1.8,
                   marker="o", markersize=5, markeredgecolor="white",
                   label=grp)
        )
    # CI层示意
    legend_handles.append(
        plt.Rectangle((0, 0), 1, 1, fc="#888888", alpha=0.28,
                       label="68% CI", linewidth=0)
    )
    if has_95:
        legend_handles.append(
            plt.Rectangle((0, 0), 1, 1, fc="#888888", alpha=0.12,
                           label="95% CI", linewidth=0)
        )
    ax.legend(handles=legend_handles, loc="best", framealpha=0.92,
              edgecolor="#CCCCCC", fancybox=True,
              borderpad=0.6, handlelength=1.8, handletextpad=0.6)

    apply_gallery_polish(ax)

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df = generate_mock_data()
    ax = plot(df, preset="gallery",
              title="3'UTR Length Across Lifespan")
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
