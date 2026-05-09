"""
云雨图 (Raincloud Plot)
========================
半小提琴(云) + 箱线图(伞) + 抖动散点(雨) + 均值连线(雷)，
比box_violin更全面地展示数据分布。

适用数据类型: distribution_comparison / expression_distribution
必需列: group, value
可选列: subgroup

参考: Allen et al., 2019 (Raincloud plots: a multi-platform tool)
      SRplot #093, ChiPlot, Bioincloud
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import gaussian_kde

from base_plot import load_sci_style, save_fig, NATURE_COLORS

# ============ 参数配置 ============
GROUP_NAMES = ["Prenatal", "Adult", "Senile", "Disease"]

# 云参数
VIOLIN_WIDTH = 0.4      # 小提琴宽度
KDE_BW = 0.3            # 核密度带宽
CUT_OFF = 0             # KDE延伸(cut=0不延伸)

# 伞参数
BOX_WIDTH = 0.15        # 箱线图宽度
BOX_LINEWIDTH = 0.8

# 雨参数
RAIN_POINT_SIZE = 8     # 散点大小
RAIN_ALPHA = 0.3        # 散点透明度

# 雷参数(均值连线)
SHOW_MEAN_LINE = True   # 是否连接各组均值


def generate_mock_data(n_per_group=80, seed=42):
    """生成演示数据: 4组基因表达量，分布参数不同"""
    rng = np.random.default_rng(seed)

    # Prenatal: 中等表达，窄分布
    prenatal = rng.normal(5.2, 1.0, n_per_group)
    # Adult: 高表达，中等分布
    adult = rng.normal(7.8, 1.3, n_per_group)
    # Senile: 略低表达，宽分布
    senile = rng.normal(4.5, 2.0, n_per_group)
    # Disease: 低表达，右偏
    disease = rng.exponential(2.0, n_per_group) + 2.0

    groups = []
    values = []
    for name, vals in zip(GROUP_NAMES, [prenatal, adult, senile, disease]):
        groups.extend([name] * len(vals))
        values.extend(vals)

    return pd.DataFrame({"group": groups, "value": values})


def plot(df, group_col="group", value_col="value", order=None,
         colors=None, orientation="vertical", show_mean_line=True,
         violin_width=0.4, box_width=0.15, rain_point_size=8,
         rain_alpha=0.3, kde_bw=0.3, n_points=300,
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制云雨图 (Raincloud Plot)

    Parameters
    ----------
    df : DataFrame, 必须包含 group 和 value 列
    group_col : str, 分组列名
    value_col : str, 数值列名
    order : list, 组别显示顺序
    colors : list, 各组颜色
    orientation : str, "vertical" 或 "horizontal"
    show_mean_line : bool, 是否连接各组均值
    violin_width : float, 小提琴(云)宽度
    box_width : float, 箱线图(伞)宽度
    rain_point_size : float, 散点(雨)大小
    rain_alpha : float, 散点透明度
    kde_bw : float, 核密度估计带宽
    n_points : int, KDE采样点数
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if colors is None:
        colors = list(NATURE_COLORS)
    if order is None:
        order = df[group_col].unique().tolist()

    n_groups = len(order)
    if figsize is None:
        if orientation == "vertical":
            figsize = (2.5 + n_groups * 1.2, 4)
        else:
            figsize = (5, 2.5 + n_groups * 0.8)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # 计算全局值范围
    all_vals = df[value_col].values
    val_min, val_max = np.nanmin(all_vals), np.nanmax(all_vals)
    val_range = val_max - val_min

    # 云(半小提琴): 用fill_betweenx(horizontal)或fill_between(vertical)
    half_violin_width = violin_width / 2

    means = []
    for i, grp in enumerate(order):
        grp_data = df.loc[df[group_col] == grp, value_col].dropna().values
        if len(grp_data) < 3:
            continue
        color = colors[i % len(colors)]
        means.append(np.mean(grp_data))

        if len(grp_data) < 5:
            # 点太少，跳过KDE
            # 简单箱线图 + 散点
            if orientation == "vertical":
                bp = ax.boxplot([grp_data], positions=[i], widths=box_width,
                                patch_artist=True, showfliers=False,
                                boxprops=dict(facecolor=color, alpha=0.6,
                                              edgecolor="black", linewidth=BOX_LINEWIDTH),
                                medianprops=dict(color="black", linewidth=1.5),
                                whiskerprops=dict(color="black", linewidth=BOX_LINEWIDTH),
                                capprops=dict(color="black", linewidth=BOX_LINEWIDTH))
                # 散点
                jitter = np.random.default_rng(i).uniform(-half_violin_width * 0.5,
                                                          half_violin_width * 0.5,
                                                          len(grp_data))
                ax.scatter(i + jitter, grp_data, s=rain_point_size,
                          alpha=rain_alpha, color=color, edgecolors="none", zorder=3)
            continue

        # KDE
        kde = gaussian_kde(grp_data, bw_method=kde_bw)
        if orientation == "vertical":
            kde_x = np.linspace(val_min - val_range * 0.05,
                              val_max + val_range * 0.05, n_points)
            density = kde(kde_x)
            # 归一化密度到half_violin_width
            density_scaled = density / density.max() * half_violin_width
            # 云: 右半侧小提琴
            ax.fill_betweenx(kde_x, i - density_scaled, i,
                            alpha=0.35, color=color, linewidth=0)
            ax.plot(i - density_scaled, kde_x, color=color, linewidth=0.8)
        else:
            kde_x = np.linspace(val_min - val_range * 0.05,
                              val_max + val_range * 0.05, n_points)
            density = kde(kde_x)
            density_scaled = density / density.max() * half_violin_width
            # 云: 上半侧小提琴
            ax.fill_between(kde_x, i - density_scaled, i,
                          alpha=0.35, color=color, linewidth=0)
            ax.plot(kde_x, i - density_scaled, color=color, linewidth=0.8)

        # 伞(box): 窄箱线图
        q1, med, q3 = np.percentile(grp_data, [25, 50, 75])
        iqr = q3 - q1
        whisker_low = max(grp_data.min(), q1 - 1.5 * iqr)
        whisker_high = min(grp_data.max(), q3 + 1.5 * iqr)

        if orientation == "vertical":
            box_left = i - box_width / 2
            # 箱体
            ax.add_patch(plt.Rectangle((box_left, q1), box_width, q3 - q1,
                                        facecolor=color, edgecolor="black",
                                        linewidth=BOX_LINEWIDTH, alpha=0.6, zorder=2))
            # 中位线
            ax.plot([box_left, box_left + box_width], [med, med],
                   color="black", linewidth=1.5, zorder=3)
            # 须线
            ax.plot([i - box_width/2, i + box_width/2], [whisker_low, whisker_low],
                   color="black", linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([i - box_width/2, i + box_width/2], [whisker_high, whisker_high],
                   color="black", linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([i, i], [whisker_low, q1], color="black",
                   linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([i, i], [q3, whisker_high], color="black",
                   linewidth=BOX_LINEWIDTH, zorder=2)

            # 雨(散点): 在小提琴对侧
            rng = np.random.default_rng(i + 42)
            jitter = rng.uniform(half_violin_width * 0.1,
                                half_violin_width * 0.6,
                                len(grp_data))
            ax.scatter(i + jitter, grp_data, s=rain_point_size,
                      alpha=rain_alpha, color=color, edgecolors="none", zorder=3)
        else:
            box_bottom = i - box_width / 2
            # 箱体 (horizontal)
            ax.add_patch(plt.Rectangle((q1, box_bottom), q3 - q1, box_width,
                                       facecolor=color, edgecolor="black",
                                       linewidth=BOX_LINEWIDTH, alpha=0.6, zorder=2))
            # 中位线
            ax.plot([med, med], [box_bottom, box_bottom + box_width],
                   color="black", linewidth=1.5, zorder=3)
            # 须线
            ax.plot([whisker_low, whisker_low],
                   [i - box_width/2, i + box_width/2],
                   color="black", linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([whisker_high, whisker_high],
                   [i - box_width/2, i + box_width/2],
                   color="black", linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([whisker_low, q1], [i, i], color="black",
                   linewidth=BOX_LINEWIDTH, zorder=2)
            ax.plot([q3, whisker_high], [i, i], color="black",
                   linewidth=BOX_LINEWIDTH, zorder=2)

            # 雨(散点): 在小提琴对侧(horizontal)
            rng = np.random.default_rng(i + 42)
            jitter = rng.uniform(half_violin_width * 0.1,
                                half_violin_width * 0.6,
                                len(grp_data))
            ax.scatter(grp_data, i + jitter, s=rain_point_size,
                      alpha=rain_alpha, color=color, edgecolors="none", zorder=3)

    # 雷(均值连线)
    if show_mean_line and len(means) > 1:
        if orientation == "vertical":
            ax.plot(range(n_groups), means, color="#555555",
                   linewidth=1.0, linestyle="--", marker="D",
                   markersize=3, zorder=4, alpha=0.7)
        else:
            ax.plot(means, range(n_groups), color="#555559",
                   linewidth=1.0, linestyle="--", marker="D",
                   markersize=3, zorder=4, alpha=0.7)

    # 样本量标注
    for i, grp in enumerate(order):
        n = (df[group_col] == grp).sum()
        if orientation == "vertical":
            ax.text(i, ax.get_ylim()[0] - val_range * 0.02,
                   f"n={n}", ha="center", va="top", color="grey",
                   fontsize=plt.rcParams["font.size"] - 1)
        else:
            ax.text(ax.get_xlim()[0] - val_range * 0.02, i,
                   f"n={n}", ha="right", va="center", color="grey",
                   fontsize=plt.rcParams["font.size"] - 1)

    # 轴标签
    if orientation == "vertical":
        ax.set_xticks(range(n_groups))
        ax.set_xticklabels(order)
        ax.set_ylabel("Expression Level (log₂ TPM)")
        ax.set_title("Gene Expression Distribution (Raincloud Plot)")
    else:
        ax.set_yticks(range(n_groups))
        ax.set_yticklabels(order)
        ax.set_xlabel("Expression Level (log₂ TPM)")
        ax.set_title("Gene Expression Distribution (Raincloud Plot)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    df = generate_mock_data()
    plot(df, save_path="raincloud_demo.png")
    plt.close()# Gallery API sync test
