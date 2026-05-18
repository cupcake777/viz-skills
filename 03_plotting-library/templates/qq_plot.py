"""
QQ图 — GWAS P-value (Quantile-Quantile Plot)
=============================================
展示GWAS p值的观察分布与期望分布对比，检测膨胀(inflation)。

适用数据类型: qtl_gwas / point_table
必需列: pvalue
可选列: snp_id

参考: qqman(R), GAPIT, EasyQC

# Catalog input_shape: point_table (columns: pvalue, optional: snp_id)
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, apply_gallery_polish, polish_legend

# ============ 参数配置 ============
GENOME_WIDE_SIG = 5e-8          # 全基因组显著性阈值
SUGGESTIVE_SIG = 1e-5            # 建议性阈值
COLOR_SIG = "#D55E00"            # 显著位点颜色 (vermillion)
COLOR_NS = "#4DBBD5"             # 不显著位点颜色 (blue)
COLOR_CI = "#E8E8E8"             # 95% CI带颜色 (light grey)
COLOR_REF = "#888888"            # 参考线颜色 (grey)
POINT_SIZE_NS = 8                # 不显著点大小
POINT_SIZE_SIG = 28              # 显著点大小
ALPHA_NS = 0.45                  # 不显著点透明度
ALPHA_SIG = 0.9                  # 显著点透明度


def generate_mock_data(n_snps=50000, inflation=1.15, n_causal=30, seed=42):
    """生成模拟GWAS p值数据，包含适度膨胀。

    Parameters
    ----------
    n_snps : int, SNP数量
    inflation : float, 基因组膨胀因子λ (>1表示膨胀)
    n_causal : int, 因果/关联SNP数量（低p值尾部）
    seed : int, 随机种子

    Returns
    -------
    pd.DataFrame with columns: snp_id, pvalue
    """
    rng = np.random.default_rng(seed)

    # 从卡方分布生成p值（模拟真实GWAS效应量分布）
    # 非关联SNP: 卡方df=1，按inflation缩放
    n_null = n_snps - n_causal
    chi2_null = rng.chisquare(df=1, size=n_null) * inflation
    p_null = stats.chi2.sf(chi2_null, df=1)
    p_null = np.clip(p_null, 1e-300, 1.0)

    # 因果/关联SNP: 更强效应
    chi2_causal = rng.chisquare(df=1, size=n_causal) * 50 + rng.uniform(10, 80, n_causal)
    p_causal = stats.chi2.sf(chi2_causal, df=1)
    p_causal = np.clip(p_causal, 1e-300, 1.0)

    # 合并
    pvalues = np.concatenate([p_null, p_causal])
    snp_ids = [f"rs{100000 + i}" for i in range(n_snps)]

    return pd.DataFrame({"snp_id": snp_ids, "pvalue": pvalues})


def plot(df, pval_col="pvalue", snp_col=None,
         genome_line=GENOME_WIDE_SIG, suggestive_line=SUGGESTIVE_SIG,
         show_ci=True, ci_alpha=0.05, n_boot_ci=1000,
         figsize=None, save_path=None, ax=None,
         title=None, preset="publication"):
    """
    绘制GWAS QQ图

    Parameters
    ----------
    df : DataFrame, 必须包含 pvalue 列
    pval_col : str, p值列名
    snp_col : str or None, SNP ID列名（用于标注显著位点）
    genome_line : float, 全基因组显著性阈值
    suggestive_line : float, 建议性阈值
    show_ci : bool, 是否显示95%置信区间带
    ci_alpha : float, CI的alpha水平（默认0.05 = 95% CI）
    n_boot_ci : int, CI的bootstrap重采样次数（用beta分布精确计算）
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选（支持子图拼接）
    title : str, 图标题，None则显示默认标题
    preset : str, "publication"|"presentation"|"gallery"|"draft"
    """
    load_sci_style(preset)

    df = df.copy()
    pvals = df[pval_col].dropna().values
    pvals = np.clip(pvals, 1e-300, 1.0)
    n = len(pvals)

    # 排序 p值 → 观察 -log10(p)
    observed_sorted = np.sort(pvals)
    observed_log10p = -np.log10(observed_sorted)

    # 期望 -log10(p) (均匀分位数)
    expected = np.arange(1, n + 1) / (n + 1)
    expected_log10p = -np.log10(expected)

    # 计算基因组膨胀因子 λ (lambda)
    chi2_obs = stats.chi2.isf(observed_sorted, df=1)
    lambda_gc = np.median(chi2_obs) / stats.chi2.ppf(0.5, df=1)

    # 创建figure
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (7, 7) if preset == "gallery" else (3.35, 3.35) if preset == "publication" else (6, 6)
        fig, ax = plt.subplots(figsize=figsize)

    # 绘制95%置信区间带 (使用beta分布精确计算)
    if show_ci:
        from scipy.stats import beta as beta_dist
        alpha_ci = ci_alpha
        ci_x = np.linspace(0, 1, 500)
        ci_lower = beta_dist.ppf(alpha_ci / 2, np.arange(1, len(ci_x) + 1),
                                  len(ci_x) + 1 - np.arange(1, len(ci_x) + 1))
        ci_upper = beta_dist.ppf(1 - alpha_ci / 2, np.arange(1, len(ci_x) + 1),
                                  len(ci_x) + 1 - np.arange(1, len(ci_x) + 1))
        ci_lower_log = -np.log10(np.clip(ci_lower, 1e-300, 1.0))
        ci_upper_log = -np.log10(np.clip(ci_upper, 1e-300, 1.0))

        # 将CI映射到期望值坐标
        expected_ci = np.linspace(expected_log10p[0], expected_log10p[-1], len(ci_x))
        ax.fill_between(expected_ci, ci_lower_log, ci_upper_log,
                        color=COLOR_CI, alpha=0.6, linewidth=0, zorder=1,
                        label="95% CI")

    # 分类：显著 vs 不显著
    sig_mask = observed_sorted < genome_line
    ns_mask = ~sig_mask

    # 绘制不显著点（先画，底层）
    if np.any(ns_mask):
        ax.scatter(expected_log10p[ns_mask], observed_log10p[ns_mask],
                   c=COLOR_NS, s=POINT_SIZE_NS, alpha=ALPHA_NS,
                   rasterized=True, edgecolors="none", zorder=2,
                   label="Non-significant")

    # 绘制显著点（后画，顶层）
    if np.any(sig_mask):
        ax.scatter(expected_log10p[sig_mask], observed_log10p[sig_mask],
                   c=COLOR_SIG, s=POINT_SIZE_SIG, alpha=ALPHA_SIG,
                   rasterized=True, edgecolors="none", zorder=3,
                   label=f"p < {genome_line:.0e}")

    # 45度参考线 (y = x)
    lim_max = max(observed_log10p.max(), expected_log10p.max()) * 1.05
    ax.plot([0, lim_max], [0, lim_max],
            color=COLOR_REF, linestyle="--", linewidth=0.8, zorder=4,
            label="Expected")

    # 建议性阈值线（水平虚线）
    if suggestive_line:
        ax.axhline(-np.log10(suggestive_line), color=COLOR_REF,
                    linestyle=":", linewidth=0.5, alpha=0.5, zorder=4)

    # 轴标签
    ax.set_xlabel("Expected $-\\log_{10}(p)$")
    ax.set_ylabel("Observed $-\\log_{10}(p)$")
    if title:
        ax.set_title(title)
    else:
        ax.set_title("GWAS QQ Plot")

    # 等比例坐标轴
    ax.set_xlim(0, lim_max)
    ax.set_ylim(0, lim_max)
    ax.set_aspect("equal")

    # 注释 λ 值
    lam_text = f"$\\lambda_{{GC}}$ = {lambda_gc:.3f}"
    # 放在左上角
    ax.text(0.05, 0.95, lam_text, transform=ax.transAxes,
            fontsize=plt.rcParams.get("font.size", 10) * 0.95,
            fontweight="bold", verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#CCCCCC", alpha=0.9),
            zorder=5)

    # 图例 & 美化
    apply_gallery_polish(ax)
    polish_legend(ax, loc="lower right")

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
    ax = plot(df, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
