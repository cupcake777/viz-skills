"""
APA模式图 (APA Pattern Scatter)
================================
展示跨发育阶段/条件的APA模式变化（gain/loss/switch等分类）。

适用数据类型: apa_pattern_comparison
必需列: gene, PDUI_cond1, PDUI_cond2
可选列: category, pvalue, significance

参考: 自定义（WCPG项目特有）
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
P_THRESHOLD = 0.05
FC_THRESHOLD = 0.1  # PDUI差异阈值

# APA模式配色 — from apa_pattern palette + npg
_apa_pal = get_palette("apa_pattern", as_list=False)["colors"]
_npg = get_palette("npg")
PATTERN_COLORS = {
    "CONSISTENT_GAIN": _apa_pal["proximal"],
    "CONSISTENT_LOSS": _apa_pal["distal"],
    "SEQUENTIAL_APA_SWITCH": _npg[1],
    "COMPETITIVE_APA_REG": _npg[2],
    "REVERSAL": _npg[4],
    "NOISY_UNSTABLE": ".6",
    "NS": ".8",
}


def generate_mock_data(n=3000, seed=42):
    """生成APA模式演示数据"""
    rng = np.random.default_rng(seed)
    patterns = list(PATTERN_COLORS.keys())
    # 模拟7种APA模式
    n_per = n // len(patterns)
    records = []
    for i, pattern in enumerate(patterns):
        if pattern == "CONSISTENT_GAIN":
            x = rng.normal(0.3, 0.15, n_per)
            y = rng.normal(0.6, 0.12, n_per)
        elif pattern == "CONSISTENT_LOSS":
            x = rng.normal(0.6, 0.12, n_per)
            y = rng.normal(0.3, 0.15, n_per)
        elif pattern == "SEQUENTIAL_APA_SWITCH":
            x = rng.normal(0.2, 0.1, n_per)
            y = rng.normal(0.8, 0.08, n_per)
        elif pattern == "COMPETITIVE_APA_REG":
            x = rng.normal(0.5, 0.1, n_per)
            y = rng.normal(0.5, 0.1, n_per)
        elif pattern == "REVERSAL":
            x = rng.normal(0.7, 0.12, n_per)
            y = rng.normal(0.2, 0.12, n_per)
        elif pattern == "NOISY_UNSTABLE":
            x = rng.uniform(0.1, 0.9, n_per)
            y = rng.uniform(0.1, 0.9, n_per)
        else:  # NS
            x = rng.normal(0.5, 0.2, n_per)
            y = rng.normal(0.5, 0.2, n_per)
        genes = [f"{pattern[:3]}_{j}" for j in range(n_per)]
        pvals = rng.uniform(1e-10, 1, n_per)
        if pattern != "NOISY_UNSTABLE" and pattern != "NS":
            pvals[:int(n_per * 0.7)] = 10 ** rng.uniform(-10, -np.log10(P_THRESHOLD), int(n_per * 0.7))
        records.extend(zip(genes, x, y, [pattern] * n_per, pvals))

    df = pd.DataFrame(records, columns=["gene", "PDUI_prenatal", "PDUI_postnatal", "category", "pvalue"])
    return df


def plot(df, x_col="PDUI_prenatal", y_col="PDUI_postnatal",
         cat_col="category", label_col="gene",
         pval_col="pvalue", p_thresh=P_THRESHOLD,
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制APA模式散点图

    Parameters
    ----------
    df : DataFrame
    x_col, y_col : str, 两个条件的PDUI列
    cat_col : str, APA模式分类列
    label_col : str, 基因标签列
    pval_col : str, p值列（用于控制透明度）
    p_thresh : float, p值阈值
    """
    load_sci_style(preset)

    df = df.copy()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # 绘制每个模式
    for pattern, color in PATTERN_COLORS.items():
        mask = df[cat_col] == pattern
        if mask.sum() == 0:
            continue
        alpha = 0.15 if pattern in ("NOISY_UNSTABLE", "NS") else 0.6
        size = 8 if pattern in ("NOISY_UNSTABLE", "NS") else 15
        ax.scatter(df.loc[mask, x_col], df.loc[mask, y_col],
                   c=color, s=size, alpha=alpha, label=pattern,
                   rasterized=True, edgecolors="none")

    # 对角线
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, alpha=0.5)

    # 区域标注
    ax.text(0.2, 0.75, "Gain\n(Longer)", alpha=0.5,
            ha="center", transform=ax.transAxes, color="grey")
    ax.text(0.75, 0.2, "Loss\n(Shorter)", alpha=0.5,
            ha="center", transform=ax.transAxes, color="grey")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel(x_col.replace("_", " "))
    ax.set_ylabel(y_col.replace("_", " "))
    ax.set_title("APA Pattern Comparison")
    ax.set_aspect("equal")

    apply_gallery_polish(ax)
    polish_legend(ax, loc="upper left", ncol=2)

    # 图例
    handles, labels = ax.get_legend_handles_labels()
    legend_labels = []
    for lab in labels:
        count = (df[cat_col] == lab).sum()
        legend_labels.append(f"{lab} (n={count})")
    ax.legend(handles, legend_labels, title="Pattern",
              loc="upper left", framealpha=0.8, ncol=2)

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
