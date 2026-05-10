"""
UpSet图 (UpSet Plot)
======================
展示多个基因集合间的交集关系，比Venn图更适合超过3个集合的场景。

适用数据类型: set_intersection / gene_sets
必需列: set_name, gene_id (长格式) 或二进制矩阵格式
可选列: category

参考: UpSetR, ComplexUpset
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc_params_from_file
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, NATURE_COLORS, polish_legend

# ============ 参数配置 ============

# Nature 配色 — from npg palette
_npg = get_palette("npg")
DOT_COLOR = "#333333"
BAR_COLOR = _npg[3]
SET_COLORS = {
    "Stage_E15": _npg[0],
    "Stage_P1": _npg[1],
    "Stage_P30": _npg[2],
    "Stage_Adult": _npg[3],
    "Stage_Elderly": _npg[4],
}


def generate_mock_data(seed=42):
    """生成5个发育阶段基因集合的交集演示数据"""
    rng = np.random.default_rng(seed)

    set_names = ["Stage_E15", "Stage_P1", "Stage_P30", "Stage_Adult", "Stage_Elderly"]
    n_sets = len(set_names)

    # 生成约200个基因的二进制成员矩阵
    all_genes = set()
    gene_sets = {}

    # 每个集合有不同大小
    set_sizes = {"Stage_E15": 85, "Stage_P1": 70, "Stage_P30": 90,
                 "Stage_Adult": 65, "Stage_Elderly": 60}

    pool = [f"Gene_{i:04d}" for i in range(300)]

    for sname in set_names:
        size = set_sizes[sname]
        selected = list(rng.choice(pool, size=size, replace=False))
        gene_sets[sname] = set(selected)
        all_genes.update(selected)

    all_genes = sorted(all_genes)

    # 构建二进制矩阵
    rows = []
    for gene in all_genes:
        row = {"gene": gene}
        for sname in set_names:
            row[sname] = 1 if gene in gene_sets[sname] else 0
        rows.append(row)

    df = pd.DataFrame(rows)
    return df, set_names


def _compute_intersections(df, set_names, min_size=1):
    """计算所有非空交集及其大小"""
    intersections = []
    n_sets = len(set_names)

    # 从大到小遍历所有交集组合
    for k in range(n_sets, 0, -1):
        for combo in combinations(range(n_sets), k):
            mask = np.ones(len(df), dtype=bool)
            for idx in combo:
                mask &= df[set_names[idx]].values == 1
            # 排除属于更大交集的元素
            for larger_combo in combinations(range(n_sets), k + 1):
                if set(combo).issubset(set(larger_combo)):
                    larger_mask = np.ones(len(df), dtype=bool)
                    for idx in larger_combo:
                        larger_mask &= df[set_names[idx]].values == 1
                    mask &= ~larger_mask

            count = mask.sum()
            if count >= min_size:
                active_sets = [set_names[i] for i in combo]
                intersections.append({
                    "sets": combo,
                    "active_sets": active_sets,
                    "count": count,
                })

    # 按交集大小降序排列
    intersections.sort(key=lambda x: (-x["count"], -len(x["sets"])))
    return intersections


def plot(df, set_names=None, min_size=1, top_n=20,
         figsize=None, save_path=None, ax=None, preset="publication"):
    """
    绘制UpSet图

    Parameters
    ----------
    df : DataFrame, 二进制矩阵，每列代表一个集合 (0/1)
    set_names : list, 集合列名列表
    min_size : int, 最小交集大小
    top_n : int, 展示的交集数量上限
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选 (此图不使用ax参数，总是创建新figure)
    """
    load_sci_style(preset)

    if set_names is None:
        set_names = [c for c in df.columns if c != "gene"]

    n_sets = len(set_names)

    # 计算集合大小
    set_sizes = {s: int(df[s].sum()) for s in set_names}

    # 计算交集
    intersections = _compute_intersections(df, set_names, min_size=min_size)
    intersections = intersections[:top_n]
    n_intersections = len(intersections)

    # 布局: 左侧水平bar(集合大小) + 中间矩阵 + 上方垂直bar(交集大小)
    fig = plt.figure(figsize=figsize or (max(10, n_intersections * 0.6 + 3), 7))

    # GridSpec: 上方交集bar, 中间矩阵, 左侧集合bar
    gs = fig.add_gridspec(2, 2,
                          width_ratios=[1, n_intersections],
                          height_ratios=[1.5, n_sets],
                          hspace=0.08, wspace=0.05)

    ax_sets = fig.add_subplot(gs[1, 0])     # 左: 集合大小 (水平bar)
    ax_matrix = fig.add_subplot(gs[1, 1])   # 中: 交集矩阵
    ax_isect = fig.add_subplot(gs[0, 1])    # 上: 交集大小 (垂直bar)

    # --- 左侧: 集合大小水平条形图 ---
    y_positions = np.arange(n_sets)[::-1]
    bar_colors = [SET_COLORS.get(s, "#999") for s in set_names]
    ax_sets.barh(y_positions, [set_sizes[s] for s in set_names],
                 color=bar_colors, edgecolor="white", linewidth=0.5, height=0.6)
    ax_sets.set_yticks(y_positions)
    ax_sets.set_yticklabels(set_names, fontsize=9)
    ax_sets.set_xlabel("Set Size", fontsize=9)
    ax_sets.set_ylim(-0.5, n_sets - 0.5)
    ax_sets.invert_xaxis()
    ax_sets.spines["top"].set_visible(False)
    ax_sets.spines["right"].set_visible(False)

    # 数值标注
    for i, s in enumerate(set_names):
        ax_sets.text(set_sizes[s] + 1, y_positions[i], str(set_sizes[s]),
                     va="center", fontsize=8, color="#333")

    # --- 中间: 交集矩阵 ---
    x_positions = np.arange(n_intersections)

    for j, isect in enumerate(intersections):
        active = set(isect["sets"])
        # 绘制竖线连接active dots
        active_ys = [n_sets - 1 - i for i in sorted(active)]
        if len(active_ys) > 1:
            ax_matrix.plot([j, j], [min(active_ys), max(active_ys)],
                           color="#CCCCCC", linewidth=1.5, zorder=1)

        # 绘制dots
        for i in range(n_sets):
            y = n_sets - 1 - i
            if i in active:
                ax_matrix.scatter(j, y, s=50, c=DOT_COLOR, zorder=2,
                                  edgecolors="none")
            else:
                ax_matrix.scatter(j, y, s=20, c="none", edgecolors="#DDDDDD",
                                  linewidths=0.5, zorder=1)

    ax_matrix.set_xticks([])
    ax_matrix.set_yticks([])
    ax_matrix.set_xlim(-0.5, n_intersections - 0.5)
    ax_matrix.set_ylim(-0.5, n_sets - 0.5)
    ax_matrix.spines[:].set_visible(False)

    # 横向分割线
    for i in range(n_sets):
        ax_matrix.axhline(i, color="#F0F0F0", linewidth=0.5, zorder=0)

    # --- 上方: 交集大小垂直条形图 ---
    ax_isect.bar(x_positions, [isect["count"] for isect in intersections],
                 color=BAR_COLOR, edgecolor="white", linewidth=0.3, width=0.6)
    ax_isect.set_xticks([])
    ax_isect.set_ylabel("Intersection Size", fontsize=9)
    ax_isect.set_xlim(-0.5, n_intersections - 0.5)
    ax_isect.spines["bottom"].set_visible(False)
    ax_isect.spines["right"].set_visible(False)

    # 数值标注
    for j, isect in enumerate(intersections):
        ax_isect.text(j, isect["count"] + 0.5, str(isect["count"]),
                      ha="center", va="bottom", fontsize=7, color="#333")

    fig.suptitle("UpSet Plot — Developmental Stage Gene Overlap",
                 fontsize=13, y=0.98)

    for a in fig.axes:
        polish_legend(a, loc="best")

    # Use savefig bbox_inches='tight' instead of tight_layout for GridSpec layouts
    if save_path:
        save_fig(fig, Path(save_path).stem.replace("_demo", ""), transparent=False)
        print(f"Saved to {save_path}")
    return fig


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df, names = generate_mock_data()
    fig = plot(df, set_names=names, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(fig, name, dpi=180, fmt="both")
    plt.close(fig)
