"""
火山图 (Volcano Plot)
======================
展示差异表达/差异分析的fold change与显著性关系。

适用数据类型: differential_expression
必需列: log2FC, pvalue
可选列: gene_label, qvalue

参考: R2Omics, HiPlot
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS, polish_legend, apply_gallery_polish, SEMANTIC_COLORS

# ============ 参数配置 ============
STYLE_PATH = Path(__file__).parent.parent / "style" / "matplotlibrc"
FC_THRESHOLD = 1.0      # log2FC阈值
P_THRESHOLD = 0.05      # p值阈值
POINT_SIZE_NS = 8       # 不显著点大小（小）
POINT_SIZE_SIG = 20     # 显著点大小
LABEL_TOP_N = 10        # 标注top N基因
ALPHA_NS = 0.3          # 不显著点透明度
ALPHA_SIG = 0.85        # 显著点透明度

# 语义配色（nature-skills规则：红=上调/positive，蓝=下调/negative，灰=NS）
COLOR_UP = SEMANTIC_COLORS["up"]       # #D55E00 Okabe-Ito红橙→上调
COLOR_DOWN = SEMANTIC_COLORS["down"]    # #0072B2 Okabe-Ito蓝→下调
COLOR_NS = SEMANTIC_COLORS["ns"]        # #BBBBBB 淡灰→不显著


def generate_mock_data(n=3000, seed=42):
    """生成演示数据"""
    rng = np.random.default_rng(seed)
    log2fc = rng.normal(0, 1.5, n)
    pvalue = rng.uniform(1e-10, 1, n)
    # 让部分基因显著
    significant_idx = rng.choice(n, size=int(n * 0.15), replace=False)
    n_sig = len(significant_idx)
    half = n_sig // 2
    log2fc[significant_idx[:half]] += rng.uniform(1.5, 4, half)
    log2fc[significant_idx[half:]] -= rng.uniform(1.5, 4, n_sig - half)
    pvalue[significant_idx] = 10 ** rng.uniform(-10, -np.log10(P_THRESHOLD), len(significant_idx))

    genes = [f"Gene_{i}" for i in range(n)]
    return pd.DataFrame({"gene_label": genes, "log2FC": log2fc, "pvalue": pvalue})


def plot(df, fc_col="log2FC", pval_col="pvalue", label_col="gene_label",
         fc_thresh=FC_THRESHOLD, p_thresh=P_THRESHOLD,
         top_n=LABEL_TOP_N, figsize=None, save_path=None, ax=None,
         title=None, preset="publication"):
    """
    绘制火山图

    Parameters
    ----------
    df : DataFrame, 必须包含 log2FC 和 pvalue 列
    fc_col : str, fold change列名
    pval_col : str, p值列名
    label_col : str, 基因标签列名
    fc_thresh : float, log2FC阈值
    p_thresh : float, p值阈值
    top_n : int, 标注的top显著基因数
    figsize : tuple, 图片尺寸(英寸)，None则用matplotlibrc默认
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选（支持子图拼接）
    title : str, 图标题，None则无标题（Nature风格不加标题）
    preset : str, "publication"|"presentation"|"draft"
    """
    # 加载风格
    load_sci_style(preset)

    # 计算 -log10(p)
    df = df.copy()
    df["neg_log10p"] = -np.log10(df[pval_col].clip(lower=1e-300))

    # 分类：上调/下调/不显著
    df["category"] = "ns"
    df.loc[(df[fc_col] > fc_thresh) & (df[pval_col] < p_thresh), "category"] = "up"
    df.loc[(df[fc_col] < -fc_thresh) & (df[pval_col] < p_thresh), "category"] = "down"

    colors = {"up": COLOR_UP, "down": COLOR_DOWN, "ns": COLOR_NS}
    sizes = {"up": POINT_SIZE_SIG, "down": POINT_SIZE_SIG, "ns": POINT_SIZE_NS}
    alphas = {"up": ALPHA_SIG, "down": ALPHA_SIG, "ns": ALPHA_NS}

    # 创建figure
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (3.35, 2.76) if preset == "publication" else (7, 5)
        fig, ax = plt.subplots(figsize=figsize)

    # 绘制散点（先画ns，再画显著点覆盖在上面）
    for cat in ["ns", "down", "up"]:  # 绘制顺序：ns在底层
        mask = df["category"] == cat
        ax.scatter(df.loc[mask, fc_col], df.loc[mask, "neg_log10p"],
                   c=colors[cat], s=sizes[cat], alpha=alphas[cat],
                   label={"up": "Up", "down": "Down", "ns": "NS"}[cat],
                   rasterized=True, edgecolors="none", zorder={"ns": 1, "down": 2, "up": 3}[cat])

    # 阈值线
    ax.axhline(-np.log10(p_thresh), color="0.5", ls="--", lw=0.5, zorder=4)
    ax.axvline(fc_thresh, color="0.5", ls="--", lw=0.5, zorder=4)
    ax.axvline(-fc_thresh, color="0.5", ls="--", lw=0.5, zorder=4)

    # 标注top基因（adjustText自动防重叠）
    if label_col and label_col in df.columns:
        sig = df[df["category"] != "ns"].copy()
        if len(sig) > 0:
            sig["abs_fc"] = sig[fc_col].abs()
            top = sig.nlargest(top_n, "abs_fc")
            auto_label(ax, texts=top[label_col].tolist(),
                       x=top[fc_col].tolist(),
                       y=top["neg_log10p"].tolist(),
                       fontsize=plt.rcParams.get("font.size", 7),
                       force_text=(0.5, 0.5),
                       force_points=(0.5, 0.5))

    # 轴标签（带单位，Nature规范）
    ax.set_xlabel("log₂ Fold Change")
    ax.set_ylabel("-log₁₀(p-value)")
    if title:
        ax.set_title(title)

    # 图例优化：去掉NS，只保留显著类别
    handles, labels = ax.get_legend_handles_labels()
    sig_mask = [l != "NS" for l in labels]
    ax.legend([h for h, m in zip(handles, sig_mask) if m],
              [l for l, m in zip(labels, sig_mask) if m],
              frameon=False, loc="best", borderpad=0.3)

    apply_gallery_polish(ax)
    polish_legend(ax, loc="best")

    # Extend top margin to prevent label clipping
    y_max = df["neg_log10p"].max()
    y_bottom = ax.get_ylim()[0]
    ax.set_ylim(bottom=y_bottom, top=y_max * 1.18)

    if save_path:
        save_fig(ax.figure if external_ax else fig, 
                 Path(save_path).stem.replace("_demo", ""),
                 transparent=False)

    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df = generate_mock_data()
    fig, ax = plt.subplots()
    ax = plot(df, preset="gallery", ax=ax)
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
