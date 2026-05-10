"""
桑基图 (Sankey / Alluvial Plot)
==================================
展示分类模式在条件间的流转关系（如APA模式在发育阶段间的转换）。

适用数据类型: apa_pattern_flow / set_intersection
必需列: source, target, count/value
可选列: category

参考: HiPlot, matplotlib sankey
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.sankey import Sankey as MplSankey
from pathlib import Path

from base_plot import load_sci_style, save_fig, APA_PATTERN_COLORS

# ============ 参数配置 ============

PATTERN_COLORS = {
    "CONSISTENT_GAIN": "#E64B35",
    "CONSISTENT_LOSS": "#3C5488",
    "SEQUENTIAL_APA_SWITCH": "#4DBBD5",
    "COMPETITIVE_APA_REG": "#00A087",
    "REVERSAL": "#F39B7F",
    "NOISY_UNSTABLE": "#CCCCCC",
}


def generate_mock_data(seed=42):
    """生成APA模式流转演示数据"""
    patterns = list(PATTERN_COLORS.keys())
    n_patterns = len(patterns)
    rng = np.random.default_rng(seed)

    # Prenatal → Postnatal 流转矩阵
    flow_matrix = rng.integers(100, 3000, (n_patterns, n_patterns))
    # 对角线（自身保持）设大值
    np.fill_diagonal(flow_matrix, rng.integers(2000, 5000, n_patterns))

    records = []
    for i, src in enumerate(patterns):
        for j, tgt in enumerate(patterns):
            records.append({
                "source": f"Pre_{src}",
                "target": f"Post_{tgt}",
                "value": int(flow_matrix[i, j]),
            })
    return pd.DataFrame(records)


def plot(df, source_col="source", target_col="target", value_col="value",
         title="Pattern Flow (Sankey)", figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制桑基图（matplotlib实现）

    用手动Alluvial方式绘制：左侧为source节点，右侧为target节点，
    用梯形色带连接表示流量。

    Parameters
    ----------
    df : DataFrame
    source_col : str, 源节点列
    target_col : str, 目标节点列
    value_col : str, 流量值列
    title : str
    figsize : tuple
    save_path : str
    ax : matplotlib Axes
    preset : str, "publication"|"presentation"|"draft"
    """
    load_sci_style(preset)

    if figsize is None:
        figsize = (8, 6) if preset == "publication" else (12, 8)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    # 节点分类
    sources = df[source_col].unique()
    targets = df[target_col].unique()

    # 计算每个节点的总流量（用于确定高度）
    source_totals = {s: df[df[source_col] == s][value_col].sum() for s in sources}
    target_totals = {t: df[df[target_col] == t][value_col].sum() for t in targets}

    max_flow = max(sum(source_totals.values()), sum(target_totals.values()))
    padding = max_flow * 0.02  # 节点间间距

    # X坐标
    x_left = 0.15
    x_right = 0.85

    # Y坐标计算（从上到下排列，留间距）
    def compute_positions(items_dict, total_items, pad):
        positions = {}
        total = sum(items_dict.values()) + pad * (len(items_dict) - 1)
        y = 1.0
        for name, val in items_dict.items():
            height = val / total
            positions[name] = (y, y - height)
            y -= height + pad / total
        return positions

    source_pos = compute_positions(source_totals, max_flow, padding)
    target_pos = compute_positions(target_totals, max_flow, padding)

    # 从matplotlibrc获取字号
    fs = plt.rcParams.get("font.size", 7)

    # 绘制节点（矩形）
    bar_width = 0.03
    for name, (y_top, y_bot) in source_pos.items():
        color = _get_color(name)
        ax.add_patch(mpatches.FancyBboxPatch(
            (x_left - bar_width / 2, y_bot), bar_width, y_top - y_bot,
            boxstyle="round,pad=0.005", facecolor=color, edgecolor="white",
            linewidth=0.5, alpha=0.9, zorder=3))
        ax.text(x_left - bar_width / 2 - 0.01, (y_top + y_bot) / 2,
                _short_label(name), ha="right", va="center",
                fontsize=fs, fontweight="bold")

    for name, (y_top, y_bot) in target_pos.items():
        color = _get_color(name)
        ax.add_patch(mpatches.FancyBboxPatch(
            (x_right - bar_width / 2, y_bot), bar_width, y_top - y_bot,
            boxstyle="round,pad=0.005", facecolor=color, edgecolor="white",
            linewidth=0.5, alpha=0.9, zorder=3))
        ax.text(x_right + bar_width / 2 + 0.01, (y_top + y_bot) / 2,
                _short_label(name), ha="left", va="center",
                fontsize=fs, fontweight="bold")

    # 绘制连接带
    src_offset = {s: source_pos[s][0] for s in sources}
    tgt_offset = {t: target_pos[t][0] for t in targets}

    for _, row in df.iterrows():
        src = row[source_col]
        tgt = row[target_col]
        val = row[value_col]
        if val <= 0:
            continue

        s_top = src_offset[src]
        s_height = val / max_flow
        s_bot = s_top - s_height

        t_top = tgt_offset[tgt]
        t_height = val / max_flow
        t_bot = t_top - t_height

        src_offset[src] = s_bot
        tgt_offset[tgt] = t_bot

        color = _get_color(src)
        mid_x = (x_left + x_right) / 2
        poly_x = [x_left, mid_x, x_right, x_right, mid_x, x_left]
        poly_y = [s_top, (s_top + t_top) / 2, t_top, t_bot, (s_bot + t_bot) / 2, s_bot]

        ax.fill(poly_x, poly_y, color=color, alpha=0.2, edgecolor="none", zorder=1)

    # 阶段标签
    title_fs = plt.rcParams.get("axes.titlesize", 8)
    ax.text(x_left, 1.05, "Prenatal", ha="center", va="bottom",
            fontsize=title_fs, fontweight="bold", color="#8491B4")
    ax.text(x_right, 1.05, "Postnatal", ha="center", va="bottom",
            fontsize=title_fs, fontweight="bold", color="#8491B4")

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.02, 1.1)
    ax.set_title(title, fontsize=title_fs, pad=15)
    ax.axis("off")

    if save_path:
        save_fig(fig, Path(save_path).stem.replace("_demo", ""), transparent=False)

    return ax


def _get_color(name):
    """从节点名称推断颜色"""
    for pattern, color in PATTERN_COLORS.items():
        if pattern in str(name).upper() or pattern in str(name):
            return color
    return "#8491B4"


def _short_label(name):
    """缩短标签名"""
    mapping = {
        "CONSISTENT_GAIN": "C.Gain",
        "CONSISTENT_LOSS": "C.Loss",
        "SEQUENTIAL_APA_SWITCH": "S.Switch",
        "COMPETITIVE_APA_REG": "C.Reg",
        "REVERSAL": "Reversal",
        "NOISY_UNSTABLE": "Unstable",
    }
    base = name.split("_", 1)[-1] if "_" in name else name
    return mapping.get(base, base[:10])


if __name__ == "__main__":
    df = generate_mock_data()
    plot(df, save_path="sankey_demo.png")
    plt.close()