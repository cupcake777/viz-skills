"""
富集环形气泡图 (Enrichment Circos-style Plot)
==============================================
以环形布局展示GO/KEGG富集分析结果，按类别(BP/CC/MF)分层排列。

适用数据类型: enrichment_analysis
必需列: term, category, pvalue, count, gene_ratio
可选列: description, gene_list

参考: clusterProfiler, enrichplot
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS, polish_legend

# ============ 参数配置 ============

# Nature 配色 — from npg palette
_npg = get_palette("npg")
CATEGORY_COLORS = {
    "BP": _npg[0],  # Biological Process
    "CC": _npg[1],  # Cellular Component
    "MF": _npg[2],  # Molecular Function
}
EDGE_COLOR = _npg[3]


def generate_mock_data(n_terms_per_cat=5, seed=42):
    """生成GO/KEGG富集分析演示数据"""
    rng = np.random.default_rng(seed)

    terms_bp = [
        ("GO:0006915", "apoptotic process"),
        ("GO:0007049", "cell cycle"),
        ("GO:0016310", "phosphorylation"),
        ("GO:0006468", "protein phosphorylation"),
        ("GO:0042981", "regulation of apoptotic process"),
    ]
    terms_cc = [
        ("GO:0005737", "cytoplasm"),
        ("GO:0005634", "nucleus"),
        ("GO:0005886", "plasma membrane"),
        ("GO:0070062", "extracellular exosome"),
        ("GO:0005829", "cytosol"),
    ]
    terms_mf = [
        ("GO:0005515", "protein binding"),
        ("GO:0003677", "DNA binding"),
        ("GO:0003723", "RNA binding"),
        ("GO:0046872", "metal ion binding"),
        ("GO:0008270", "zinc ion binding"),
    ]

    records = []
    for category, term_list in [("BP", terms_bp), ("CC", terms_cc), ("MF", terms_mf)]:
        for go_id, desc in term_list[:n_terms_per_cat]:
            pvalue = 10 ** rng.uniform(-15, -2)
            count = int(rng.integers(5, 80))
            gene_ratio = rng.uniform(0.02, 0.4)
            records.append({
                "term": f"{go_id} {desc}",
                "category": category,
                "pvalue": pvalue,
                "count": count,
                "gene_ratio": gene_ratio,
            })

    return pd.DataFrame(records)


def plot(df, term_col="term", category_col="category", pval_col="pvalue",
         count_col="count", ratio_col="gene_ratio",
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制富集环形气泡图

    Parameters
    ----------
    df : DataFrame, 必须包含 term, category, pvalue, count, gene_ratio 列
    term_col : str, 通路/术语列名
    category_col : str, 类别列名 (BP/CC/MF)
    pval_col : str, p值列名
    count_col : str, 基因计数列名
    ratio_col : str, 基因比例列名
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选 (必须为polar类型)
    """
    load_sci_style(preset)

    df = df.copy()
    categories = df[category_col].unique().tolist()
    n_categories = len(categories)

    # 计算角度分配: 每个类别占据一段弧
    total_terms = len(df)
    angles_per_term = 2 * np.pi / total_terms

    # 排序: 按类别分组
    df = df.sort_values(category_col).reset_index(drop=True)

    # 计算每个term的角度
    angles = np.array([i * angles_per_term for i in range(total_terms)])

    # -log10(pvalue) 映射到颜色
    neg_log_p = -np.log10(df[pval_col].clip(lower=1e-300))
    norm = plt.Normalize(vmin=neg_log_p.min(), vmax=neg_log_p.max())
    cmap = plt.cm.YlOrRd

    # 气泡大小映射
    sizes = df[count_col].values
    size_norm = plt.Normalize(vmin=sizes.min(), vmax=sizes.max())
    bubble_sizes = 50 + size_norm(sizes) * 400  # 50-450

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (8, 8),
                               subplot_kw={"projection": "polar"})

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # 绘制内圈类别弧段
    cat_start = 0
    for cat in categories:
        cat_mask = df[category_col] == cat
        n_cat = cat_mask.sum()
        cat_angles = angles[cat_mask.values]

        # 内圈弧: r=0.3-0.45
        theta_start = cat_angles[0] - angles_per_term / 2
        theta_end = cat_angles[-1] + angles_per_term / 2
        theta_fill = np.linspace(theta_start, theta_end, 100)
        ax.fill_between(theta_fill, 0.25, 0.42,
                        color=CATEGORY_COLORS.get(cat, "#999999"),
                        alpha=0.25, linewidth=0)
        ax.plot(theta_fill, [0.25] * len(theta_fill),
                color=CATEGORY_COLORS.get(cat, "#999999"),
                lw=1.2, alpha=0.6)
        ax.plot(theta_fill, [0.42] * len(theta_fill),
                color=CATEGORY_COLORS.get(cat, "#999999"),
                lw=1.2, alpha=0.6)

        # 类别标签
        mid_angle = (theta_start + theta_end) / 2
        ax.text(mid_angle, 0.33, cat,
                ha="center", va="center", fontweight="bold",
                color=CATEGORY_COLORS.get(cat, "#999999"))

        cat_start += n_cat

    # 绘制外圈气泡
    for i, row in df.iterrows():
        angle = angles[i]
        r = 0.55 + row[ratio_col] * 1.0  # 半径映射gene_ratio
        color = cmap(norm(neg_log_p.iloc[i]))
        ax.scatter(angle, r, s=bubble_sizes[i], c=[color],
                   alpha=0.8, edgecolors="white", linewidths=0.5, zorder=5)

    # 绘制term标签
    for i, row in df.iterrows():
        angle = angles[i]
        r_label = 0.55 + row[ratio_col] * 1.0 + 0.12
        # 简化term名称
        label = row[term_col]
        if len(label) > 25:
            label = label[:22] + "..."

        # 根据角度决定文字对齐
        ha = "left" if 0 < angle < np.pi else "right"
        rotation = np.degrees(angle)
        if np.pi / 2 < angle < 3 * np.pi / 2:
            rotation += 180

        ax.text(angle, r_label, label,
                ha=ha, va="center",
                rotation=rotation, rotation_mode="anchor",
                color=".2")

    # 色条
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.6)
    cbar.set_label("-log₁₀(p-value)")

    ax.set_ylim(0, 2.0)
    ax.set_rticks([])
    ax.set_xticks([])
    ax.spines["polar"].set_visible(False)
    ax.grid(False)
    ax.set_title("GO Enrichment Circos Plot", pad=25)

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
    ax = plot(df, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
