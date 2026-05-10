"""
Manhattan图 (Manhattan Plot)
=============================
展示QTL/GWAS全局显著性概览，突出峰值位点。

适用数据类型: qtl_gwas
必需列: chr, pos, pvalue
可选列: snp_id, beta, se

参考: qqman(R), HiPlot
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
GENOME_LINE = 5e-8          # 全基因组显著性阈值
SUGGESTIVE_LINE = 1e-5      # 建议性阈值
_gwas_pal = get_palette("gwas_significance", as_list=False)["colors"]
CHR_COLORS = [_gwas_pal["chr_even"], _gwas_pal["chr_odd"]]
HIGHLIGHT_COLOR = _gwas_pal["genome_wide_line"]


def generate_mock_data(n_per_chr=5000, n_chr=22, seed=42):
    """生成演示数据"""
    rng = np.random.default_rng(seed)
    records = []
    chr_sizes = {
        i: rng.integers(5e7, 2.5e8) for i in range(1, n_chr + 1)
    }
    for chrom in range(1, n_chr + 1):
        positions = rng.uniform(0, chr_sizes[chrom], n_per_chr)
        # 大部分不显著，少数峰值
        pvals = rng.uniform(0.01, 1, n_per_chr)
        # 每个染色体几个显著位点
        n_peaks = rng.integers(0, 5)
        peak_idx = rng.choice(n_per_chr, size=min(n_peaks, n_per_chr), replace=False)
        pvals[peak_idx] = 10 ** rng.uniform(-12, -6, len(peak_idx))
        # 为peak位点和部分非peak位点分配gene名
        gene_names = {}
        for j, pidx in enumerate(peak_idx):
            gene_names[int(pidx)] = f"GENE{chrom}_{j}"
        some_nonpeak = rng.choice([i for i in range(n_per_chr) if i not in peak_idx],
                                   size=min(20, n_per_chr), replace=False)
        for j, idx in enumerate(some_nonpeak):
            gene_names[int(idx)] = f"LOC{chrom}_{j}"
        for i, (pos, pval) in enumerate(zip(positions, pvals)):
            records.append({
                "chr": chrom, "pos": int(pos), "pvalue": pval,
                "snp_id": f"chr{chrom}:{int(pos)}",
                "gene": gene_names.get(i, ""),
            })
    return pd.DataFrame(records)


def plot(df, chr_col="chr", pos_col="pos", pval_col="pvalue",
         snp_col=None, gene_col="gene", genome_line=GENOME_LINE, suggestive_line=SUGGESTIVE_LINE,
         highlight_peaks=True, chr_colors=CHR_COLORS, figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制Manhattan图

    Parameters
    ----------
    df : DataFrame
    chr_col, pos_col, pval_col : str, 列名
    snp_col : str or None, SNP标签列
    gene_col : str or None, 基因名列（优先用于标注峰值）
    genome_line : float, 全基因组显著性阈值
    suggestive_line : float, 建议性阈值
    highlight_peaks : bool, 是否标注峰值SNP
    chr_colors : list, 染色体交替配色
    """
    load_sci_style(preset)

    df = df.copy()
    df["neg_log10p"] = -np.log10(df[pval_col].clip(lower=1e-300))
    df = df.sort_values([chr_col, pos_col])

    # 计算累积位置
    chr_max = df.groupby(chr_col)[pos_col].max()
    chr_offset = {}
    cum_pos = 0
    for chrom in sorted(df[chr_col].unique()):
        chr_offset[chrom] = cum_pos
        cum_pos += chr_max[chrom] + chr_max[chrom] * 0.01
    df["cum_pos"] = df.apply(lambda r: chr_offset[r[chr_col]] + r[pos_col], axis=1)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (12, 4))

    # 按染色体交替着色绘制
    for i, chrom in enumerate(sorted(df[chr_col].unique())):
        mask = df[chr_col] == chrom
        color = chr_colors[i % len(chr_colors)]
        ax.scatter(df.loc[mask, "cum_pos"], df.loc[mask, "neg_log10p"],
                   c=color, s=6, alpha=0.7, rasterized=True, edgecolors="none")

    # 阈值线
    if genome_line:
        ax.axhline(-np.log10(genome_line), color=HIGHLIGHT_COLOR, ls="--", lw=0.8)
    if suggestive_line and suggestive_line != genome_line:
        ax.axhline(-np.log10(suggestive_line), color="grey", ls="--", lw=0.6, alpha=0.5)

    # 标注峰值（使用auto_label）
    peak_label_col = None
    if highlight_peaks:
        for col in [gene_col, snp_col]:
            if col and col in df.columns:
                peak_label_col = col
                break
        if peak_label_col:
            peaks = df[df[pval_col] < genome_line].nsmallest(10, pval_col)
            if len(peaks) > 0:
                auto_label(ax, texts=peaks[peak_label_col].astype(str).tolist(),
                           x=peaks["cum_pos"].tolist(),
                           y=peaks["neg_log10p"].tolist())

    # X轴标签
    chr_centers = {c: chr_offset[c] + chr_max[c] / 2 for c in sorted(chr_offset)}
    ax.set_xticks(list(chr_centers.values()))
    ax.set_xticklabels([str(c) for c in chr_centers.keys()])

    ax.set_xlabel("Chromosome")
    ax.set_ylabel("-log₁₀(p-value)")
    ax.set_title("Manhattan Plot")

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
    ax = plot(df, snp_col="snp_id", preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
