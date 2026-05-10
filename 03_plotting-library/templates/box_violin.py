"""
箱线-小提琴组合图 (Box-Violin Plot)
====================================
结合小提琴图（分布形态）与箱线图（四分位数），展示不同组间基因表达量分布。

适用数据类型: group_comparison / expression_distribution
必需列: group, value
可选列: subgroup

参考: Nature Methods, ggplot2 violin+box
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS, polish_legend, apply_gallery_polish

# ============ 参数配置 ============
GROUP_NAMES = ["Prenatal", "Adult", "Senile", "Disease"]


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
        groups.extend([name] * n_per_group)
        values.extend(vals)

    return pd.DataFrame({"group": groups, "value": values})


def plot(df, group_col="group", value_col="value", order=None,
         colors=None, figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制箱线-小提琴组合图

    Parameters
    ----------
    df : DataFrame, 必须包含 group 和 value 列
    group_col : str, 分组列名
    value_col : str, 数值列名
    order : list, 组别显示顺序
    colors : list, 各组颜色
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if colors is None:
        colors = NATURE_COLORS
    if order is None:
        order = df[group_col].unique().tolist()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    positions = np.arange(1, len(order) + 1)

    for i, grp in enumerate(order):
        grp_data = df.loc[df[group_col] == grp, value_col].values
        color = colors[i % len(colors)]

        # 小提琴图 (半透明)
        parts = ax.violinplot([grp_data], positions=[positions[i]],
                              showmeans=False, showmedians=False, showextrema=False)
        for pc in parts["bodies"]:
            pc.set_facecolor(color)
            pc.set_alpha(0.35)
            pc.set_edgecolor("black")
            pc.set_linewidth(0.5)

        # 箫线箱线图
        bp = ax.boxplot([grp_data], positions=[positions[i]],
                        widths=0.25, patch_artist=True,
                        showfliers=False,
                        boxprops=dict(facecolor=color, edgecolor="black", linewidth=0.8),
                        medianprops=dict(color="black", linewidth=1.5),
                        whiskerprops=dict(color="black", linewidth=0.8),
                        capprops=dict(color="black", linewidth=0.8))

    ax.set_xticks(positions)
    ax.set_xticklabels(order)
    ax.set_ylabel("Expression Level (log₂ TPM)")
    ax.set_title("Gene Expression Distribution by Developmental Stage")

    apply_gallery_polish(ax)
    polish_legend(ax, loc="best")

    # 添加样本量标注
    for i, grp in enumerate(order):
        n = (df[group_col] == grp).sum()
        ax.text(positions[i], ax.get_ylim()[0] - 0.15 * (ax.get_ylim()[1] - ax.get_ylim()[0]),
                f"n={n}", ha="center", va="top", color="grey")

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
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
