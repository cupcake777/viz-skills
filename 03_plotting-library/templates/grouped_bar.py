"""
分组柱状图 (Grouped Bar Plot)
================================
多组间数值比较，支持误差线和显著性标注。

适用数据类型: grouped_comparison
必需列: group, category, value
可选列: error, significance_mark

参考: R2Omics
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
BAR_WIDTH = 0.8       # 组内柱宽系数
ERROR_CAPSIZE = 3
ADD_NUMBERS = False   # 柱顶是否标注数值


def generate_mock_data(seed=42):
    """生成演示数据"""
    rng = np.random.default_rng(seed)
    groups = ["Prenatal", "Postnatal"]
    categories = ["3'/5' UTR", "CDS", "Intron", "Intergenic"]
    records = []
    for g in groups:
        for c in categories:
            val = rng.uniform(20, 80)
            err = rng.uniform(2, 8)
            records.append({
                "group": g, "category": c,
                "value": val, "error": err,
                "significance": rng.choice(["*", "**", "***", "ns"])
            })
    return pd.DataFrame(records)


def plot(df, group_col="group", cat_col="category", val_col="value",
         err_col="error", sig_col=None, bar_width=BAR_WIDTH,
         add_numbers=ADD_NUMBERS, figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制分组柱状图

    Parameters
    ----------
    df : DataFrame
    group_col : str, 分组列（如Prenatal/Postnatal）
    cat_col : str, 类别列
    val_col : str, 数值列
    err_col : str or None, 误差列
    sig_col : str or None, 显著性标注列
    bar_width : float
    add_numbers : bool, 柱顶标注数值
    """
    load_sci_style(preset)

    groups = df[group_col].unique()
    categories = df[cat_col].unique()
    n_groups = len(groups)
    n_cats = len(categories)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(n_cats)
    group_width = bar_width / n_groups

    for i, grp in enumerate(groups):
        subset = df[df[group_col] == grp]
        # 确保顺序一致
        vals = [subset.loc[subset[cat_col] == c, val_col].values[0] for c in categories]
        errs = None
        if err_col and err_col in df.columns:
            errs = [subset.loc[subset[cat_col] == c, err_col].values[0] for c in categories]

        offset = (i - n_groups / 2 + 0.5) * group_width
        bars = ax.bar(x + offset, vals, width=group_width * 0.9,
                      yerr=errs, capsize=ERROR_CAPSIZE,
                      label=grp, alpha=0.85)

        # 柱顶数值
        if add_numbers:
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"{v:.1f}", ha="center", va="bottom")

    # 显著性标注
    if sig_col and sig_col in df.columns:
        for i, grp in enumerate(groups):
            subset = df[df[group_col] == grp]
            offset = (i - n_groups / 2 + 0.5) * group_width
            for j, c in enumerate(categories):
                row = subset[subset[cat_col] == c]
                if len(row) > 0:
                    sig = row[sig_col].values[0]
                    v = row[val_col].values[0]
                    e = row[err_col].values[0] if err_col and err_col in df.columns else 0
                    if sig != "ns":
                        ax.text(x[j] + offset, v + e + 1, sig,
                                ha="center", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(val_col)
    ax.set_title("Grouped Bar Plot")
    ax.legend(title=group_col)

    apply_gallery_polish(ax)
    polish_legend(ax, loc="best")

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df = generate_mock_data()
    ax = plot(df, sig_col="significance", add_numbers=True, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
