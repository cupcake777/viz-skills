"""
富集气泡图 (Enrichment Bubble Plot)
======================================
展示GO/KEGG富集分析结果。

适用数据类型: enrichment_result
必需列: term, pvalue, gene_ratio
可选列: count, category, qvalue

参考: R2Omics, HiPlot, clusterProfiler
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
SHOW_TOP_N = 20       # 显示top N条目
BUBBLE_SCALE = 300    # 气泡大小系数


def generate_mock_data(n=30, seed=42):
    """生成富集分析演示数据"""
    rng = np.random.default_rng(seed)
    go_terms = [
        "RNA splicing", "mRNA processing", "neuron differentiation",
        "synaptic signaling", "axon guidance", "brain development",
        "chromatin remodeling", "histone modification", "DNA repair",
        "cell cycle", "apoptosis", "protein ubiquitination",
        "translation", "ribosome biogenesis", "mitochondrial transport",
        "glucose metabolism", "oxidative phosphorylation", "immune response",
        "inflammatory response", "NF-kB signaling", "Wnt signaling",
        "Notch signaling", "MAPK cascade", "growth factor response",
        "stem cell maintenance", "cell adhesion", "extracellular matrix",
        "angiogenesis", "vascular development", "lipid metabolism"
    ]
    categories = rng.choice(["BP", "MF", "CC"], n)
    pvals = 10 ** rng.uniform(-8, -0.3, n)
    gene_ratios = rng.uniform(0.05, 0.4, n)
    counts = rng.integers(10, 200, n)
    return pd.DataFrame({
        "term": go_terms[:n],
        "category": categories,
        "pvalue": pvals,
        "gene_ratio": gene_ratios,
        "count": counts,
        "qvalue": pvals * rng.uniform(1, 3, n)
    })


def plot(df, term_col="term", pval_col="pvalue", ratio_col="gene_ratio",
         count_col="count", cat_col="category",
         top_n=SHOW_TOP_N, bubble_scale=BUBBLE_SCALE,
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制富集气泡图

    Parameters
    ----------
    df : DataFrame
    term_col : str, 术语/通路名列
    pval_col : str, p值列
    ratio_col : str, 基因比例列 (GeneRatio)
    count_col : str, 基因数列
    cat_col : str or None, 类别列（如BP/MF/CC）
    top_n : int, 显示top N最显著的条目
    bubble_scale : float, 气泡大小系数
    """
    load_sci_style(preset)

    # 取top N最显著
    df = df.nsmallest(top_n, pval_col).copy()
    df["neg_log10p"] = -np.log10(df[pval_col])
    df = df.sort_values("neg_log10p", ascending=True)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    # 按类别着色 — from NATURE_COLORS
    cat_palette = {"BP": NATURE_COLORS[0], "MF": NATURE_COLORS[1], "CC": NATURE_COLORS[2],
                   "KEGG": NATURE_COLORS[3], "Reactome": NATURE_COLORS[4]}

    if cat_col and cat_col in df.columns:
        for cat, grp in df.groupby(cat_col):
            color = cat_palette.get(cat, "#8491B4")
            ax.scatter(grp[ratio_col], grp["neg_log10p"],
                       s=grp[count_col] / grp[count_col].max() * bubble_scale,
                       c=color, alpha=0.7, label=cat, edgecolors="white", lw=0.5)
    else:
        ax.scatter(df[ratio_col], df["neg_log10p"],
                   s=df[count_col] / df[count_col].max() * bubble_scale,
                   c="#E64B35", alpha=0.7, edgecolors="white", lw=0.5)

    # 条目标签
    for _, row in df.iterrows():
        ax.text(row[ratio_col] + 0.002, row["neg_log10p"],
                row[term_col], va="center", alpha=0.8)

    ax.set_xlabel("Gene Ratio")
    ax.set_ylabel("-log₁₀(p-value)")
    ax.set_title("Enrichment Analysis")
    if cat_col and cat_col in df.columns:
        ax.legend(title=cat_col)

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
    ax = plot(df, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
