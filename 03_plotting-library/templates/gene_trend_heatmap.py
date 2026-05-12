"""
Gene Trend Heatmap (Palantir-style)
====================================
Expression heatmap over a continuous pseudotime axis, with genes sorted
by peak activation time. Inspired by Palantir / Scanpy gene trend
visualizations.

适用数据类型: temporal_expression / pseudotime
必需列: expression_matrix (genes x pseudotime_bins), gene_labels, pseudotime
可选列: —

参考: Palantir (Setty et al., Nature Biotechnology 2019),
      Scanpy pl.paga / gene_trend heatmaps
"""

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pathlib import Path
from typing import Optional, Tuple, List

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish, SEMANTIC_COLORS
)

# ============ 参数配置 ============
DEFAULT_CMAP = "RdBu_r"       # diverging colormap: blue=low, red=high
DEFAULT_VMIN_PCT = 2          # percentile for color clipping (low)
DEFAULT_VMAX_PCT = 98         # percentile for color clipping (high)
N_GENES = 30                  # mock data: number of genes
N_PSEUDOTIME_BINS = 100       # mock data: pseudotime resolution
NOISE_SCALE = 0.3             # mock data: Gaussian noise sigma


# ============ Mock data ============

def generate_mock_data(n_genes=N_GENES, n_bins=N_PSEUDOTIME_BINS, seed=42):
    """Generate a synthetic expression matrix (genes × pseudotime bins).

    Each gene has a Gaussian activation profile peaking at a random
    pseudotime position, simulating dynamic gene expression along a
    differentiation trajectory (e.g. Palantir pseudotime).

    Returns
    -------
    expression_matrix : np.ndarray, shape (n_genes, n_bins)
    gene_labels : list of str
    pseudotime : np.ndarray, shape (n_bins,)
    """
    rng = np.random.default_rng(seed)
    pseudotime = np.linspace(0, 1, n_bins)
    gene_labels = [f"Gene_{i:02d}" for i in range(n_genes)]

    # Peak position for each gene: spread across pseudotime
    peak_positions = rng.uniform(0.05, 0.95, n_genes)
    # Width of activation window (variability in sharpness)
    widths = rng.uniform(0.05, 0.25, n_genes)
    # Amplitude
    amplitudes = rng.uniform(1.0, 4.0, n_genes)
    # Basal level
    basals = rng.uniform(0.1, 0.8, n_genes)

    expression_matrix = np.zeros((n_genes, n_bins))
    for g in range(n_genes):
        profile = basals[g] + amplitudes[g] * np.exp(
            -0.5 * ((pseudotime - peak_positions[g]) / widths[g]) ** 2
        )
        profile += rng.normal(0, NOISE_SCALE, n_bins)
        expression_matrix[g] = profile

    return expression_matrix, gene_labels, pseudotime


def _zscore_rows(matrix):
    """Z-score normalize each row (gene) independently."""
    means = matrix.mean(axis=1, keepdims=True)
    stds = matrix.std(axis=1, keepdims=True)
    return (matrix - means) / (stds + 1e-9)


def _sort_by_peak(matrix):
    """Return row indices sorted by the column index of each row's peak."""
    return np.argsort(np.argmax(matrix, axis=1))


# ============ Plotting ============

def plot(
    expression_matrix: np.ndarray,
    gene_labels: Optional[List[str]] = None,
    pseudotime: Optional[np.ndarray] = None,
    cmap: str = DEFAULT_CMAP,
    vmin_pct: float = DEFAULT_VMIN_PCT,
    vmax_pct: float = DEFAULT_VMAX_PCT,
    zscore: bool = True,
    sort_genes: bool = True,
    title: Optional[str] = None,
    xlabel: str = "Pseudotime",
    ylabel: str = "Genes",
    figsize: Optional[Tuple[float, float]] = None,
    save_path: Optional[str] = None,
    ax: Optional[Axes] = None,
    preset: str = "publication",
):
    """Plot a gene trend heatmap over pseudotime.

    Parameters
    ----------
    expression_matrix : np.ndarray, shape (n_genes, n_bins)
        Raw or pre-normalized expression values.
    gene_labels : list of str, optional
        Gene names for y-axis ticks.
    pseudotime : np.ndarray, optional
        Pseudotime values for x-axis.
    cmap : str
        Matplotlib colormap name (default 'RdBu_r').
    vmin_pct, vmax_pct : float
        Percentile clipping for color scale.
    zscore : bool
        Whether to z-score normalize rows before plotting.
    sort_genes : bool
        Whether to sort rows by peak pseudotime position.
    title : str, optional
        Plot title.
    xlabel, ylabel : str
        Axis labels.
    figsize : tuple, optional
        Figure size in inches.
    save_path : str, optional
        Path to save figure.
    ax : matplotlib Axes, optional
        Existing axes to draw on.
    preset : str
        Style preset.

    Returns
    -------
    ax : matplotlib Axes
    """
    load_sci_style(preset)

    mat = expression_matrix.copy().astype(float)
    n_genes, n_bins = mat.shape

    # Pseudotime axis
    if pseudotime is None:
        pseudotime = np.linspace(0, 1, n_bins)
    if gene_labels is None:
        gene_labels = [f"Gene_{i}" for i in range(n_genes)]

    # Z-score normalization (row-wise)
    if zscore:
        mat = _zscore_rows(mat)

    # Sort genes by peak pseudotime
    if sort_genes:
        order = _sort_by_peak(mat)
        mat = mat[order]
        gene_labels = [gene_labels[i] for i in order]

    # Percentile-based color clipping
    vmin = np.percentile(mat, vmin_pct)
    vmax = np.percentile(mat, vmax_pct)

    # Figure setup
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (8, max(4, n_genes * 0.25 + 1.5)) if preset == "gallery" else (6, max(3.5, n_genes * 0.22 + 1.0))
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # Heatmap via imshow
    im = ax.imshow(
        mat,
        aspect="auto",
        interpolation="nearest",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        origin="upper",
        extent=[pseudotime[0], pseudotime[-1], n_genes - 0.5, -0.5],
    )

    # Axis ticks
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_yticks(np.arange(n_genes))
    ax.set_yticklabels(gene_labels, fontsize=max(4, min(8, 120 / n_genes)))

    # X-axis: select a handful of pseudotime ticks
    n_xticks = min(6, n_bins)
    tick_indices = np.linspace(0, n_bins - 1, n_xticks, dtype=int)
    ax.set_xticks(pseudotime[tick_indices])
    ax.set_xticklabels([f"{pseudotime[i]:.2f}" for i in tick_indices])

    if title:
        ax.set_title(title, fontweight="bold", pad=10)

    # Colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.08)
    cb = fig.colorbar(im, cax=cax)
    cb_label = "Z-score" if zscore else "Expression"
    cb.set_label(cb_label, fontsize=plt.rcParams.get("font.size", 7))
    cb.outline.set_linewidth(0.5)

    apply_gallery_polish(ax)

    # Save
    if save_path:
        save_fig(fig if not external_ax else ax.figure,
                 Path(save_path).stem, transparent=False)

    return ax


# ============ CLI / Demo ============

if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig

    load_sci_style("gallery")

    expression_matrix, gene_labels, pseudotime = generate_mock_data()
    ax = plot(
        expression_matrix,
        gene_labels=gene_labels,
        pseudotime=pseudotime,
        zscore=True,
        sort_genes=True,
        cmap="RdBu_r",
        title="Gene Expression Trends along Pseudotime",
        xlabel="Pseudotime",
        ylabel="Genes",
        preset="gallery",
    )
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)

    print("Gene trend heatmap demo saved.")
