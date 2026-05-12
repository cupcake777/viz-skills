"""
Knee Plot (Ranked Abundance Plot)
==================================
Log-log ranked barcode UMI count plot for single-cell droplet-based scRNA-seq
quality control. Inspired by CellBender's background removal methodology.

The characteristic "knee" shape separates real cells (high UMI) from
background/empty droplets (low UMI). The inflection point marks the
transition between the two populations.

适用数据类型: distribution / ranked_abundance
必需列: 1-D array of UMI counts (sorted descending)
可选参数: inflection_rank, threshold

参考: Fleming et al., Nature Methods 2023 (CellBender);
      Zheng et al., Nature Communications 2017 (Cell Ranger)
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish,
    SEMANTIC_COLORS,
)

# ============ 参数配置 ============
LINE_COLOR = SEMANTIC_COLORS.get("proposed", "#3C5488")  # deep blue
INFLECTION_COLOR = "#E53935"   # red
THRESHOLD_COLOR = "#8491B4"    # muted grey-blue
LINE_WIDTH = 1.8
CELL_PROB_COLOR = SEMANTIC_COLORS.get("positive", "#2E9E44")  # green for prob curve


# ============ Mock data ============

def generate_mock_data(n_cells=2500, n_background=7500, seed=42):
    """Generate realistic ranked barcode UMI counts.

    Simulates a 10x Chromium-style experiment:
    - Real cells: power-law distributed high UMI counts (1000–50000)
    - Background/empty droplets: low UMI counts (1–100)

    Returns
    -------
    ranked_counts : np.ndarray
        UMI counts sorted in descending order (length n_cells + n_background).
    """
    rng = np.random.default_rng(seed)

    # Real cells — power-law / log-normal distribution
    cell_umis = rng.lognormal(mean=np.log(8000), sigma=0.7, size=n_cells)
    cell_umis = np.clip(cell_umis, 500, 60000).astype(int)

    # Background droplets — low counts
    bg_umis = rng.lognormal(mean=np.log(15), sigma=1.0, size=n_background)
    bg_umis = np.clip(bg_umis, 1, 200).astype(int)

    # Combine and sort descending
    all_umis = np.concatenate([cell_umis, bg_umis])
    ranked_counts = np.sort(all_umis)[::-1]

    return ranked_counts


def detect_inflection(ranked_counts):
    """Detect the knee/inflection point using maximum curvature.

    Works in log-log space on the cumulative fraction curve.

    Returns
    -------
    inflection_rank : int
        The 1-indexed rank at the inflection point.
    """
    log_ranks = np.log10(np.arange(1, len(ranked_counts) + 1))
    log_counts = np.log10(np.maximum(ranked_counts, 1))

    # Smooth to reduce noise
    window = max(len(ranked_counts) // 200, 5)
    kernel = np.ones(window) / window
    smoothed = np.convolve(log_counts, kernel, mode="same")

    # Second derivative (curvature proxy)
    d2 = np.diff(smoothed, n=2)
    # Skip edges
    margin = window
    inflection_idx = np.argmin(d2[margin:-margin]) + margin

    return int(10 ** log_ranks[inflection_idx])


def compute_cell_probability(ranked_counts, inflection_rank, steepness=5.0):
    """Compute probability of each barcode being a real cell.

    Uses a sigmoid centered at the inflection point (in log-rank space).

    Returns
    -------
    prob : np.ndarray
        Probability values in [0, 1], same length as ranked_counts.
    """
    log_ranks = np.log10(np.arange(1, len(ranked_counts) + 1))
    log_inflection = np.log10(inflection_rank)
    # Sigmoid: high prob for rank < inflection, low for rank > inflection
    prob = 1.0 / (1.0 + np.exp(steepness * (log_ranks - log_inflection)))
    return prob


# ============ Plotting ============

def plot(
    ranked_counts,
    inflection_rank=None,
    threshold=None,
    show_probability=True,
    xlabel="Barcode rank",
    ylabel="UMI counts",
    title=None,
    figsize=None,
    save_path=None,
    ax=None,
    preset="publication",
):
    """
    Draw a log-log ranked abundance (knee) plot.

    Parameters
    ----------
    ranked_counts : array-like
        UMI counts per barcode, sorted in descending order.
    inflection_rank : int or None
        Rank at the knee point. If None, auto-detected.
    threshold : float or None
        Minimum UMI cutoff line to draw.
    show_probability : bool
        Whether to overlay the cell-probability sigmoid on a secondary y-axis.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    title : str or None
        Plot title.
    figsize : tuple or None
        Figure size in inches.
    save_path : str or None
        If given, save figure to this path.
    ax : matplotlib Axes or None
        Existing axes to draw on. If None, a new figure is created.
    preset : str
        Style preset: 'publication' | 'gallery' | 'presentation' | 'draft'

    Returns
    -------
    ax : matplotlib Axes
    """
    load_sci_style(preset)

    ranked_counts = np.asarray(ranked_counts, dtype=float)
    n = len(ranked_counts)
    ranks = np.arange(1, n + 1)

    # Auto-detect inflection
    if inflection_rank is None:
        inflection_rank = detect_inflection(ranked_counts)

    # --- Create figure ---
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (8, 5.6) if preset == "gallery" else (5, 4)
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # --- Main ranked curve (log-log) ---
    ax.plot(
        ranks, ranked_counts,
        color=LINE_COLOR, linewidth=LINE_WIDTH,
        solid_capstyle="round", zorder=3,
    )
    ax.set_xscale("log")
    ax.set_yscale("log")

    # --- Inflection point marker ---
    inflection_count = ranked_counts[min(inflection_rank - 1, n - 1)]
    ax.axvline(
        x=inflection_rank, color=INFLECTION_COLOR,
        linestyle="--", linewidth=1.2, alpha=0.85, zorder=4,
    )
    ax.annotate(
        f"Knee: rank {inflection_rank:,}\n({int(inflection_count):,} UMIs)",
        xy=(inflection_rank, inflection_count),
        xytext=(inflection_rank * 3, inflection_count * 0.3),
        fontsize=plt.rcParams.get("font.size", 7) - 1,
        color=INFLECTION_COLOR,
        arrowprops=dict(
            arrowstyle="->", color=INFLECTION_COLOR,
            lw=0.8, connectionstyle="arc3,rad=0.2",
        ),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=INFLECTION_COLOR,
                  alpha=0.9, lw=0.5),
        zorder=5,
    )

    # --- Threshold line ---
    if threshold is not None:
        ax.axhline(
            y=threshold, color=THRESHOLD_COLOR,
            linestyle=":", linewidth=1.0, alpha=0.7, zorder=2,
        )
        ax.text(
            n * 0.6, threshold * 1.15,
            f"Min UMI = {int(threshold):,}",
            fontsize=plt.rcParams.get("font.size", 7) - 2,
            color=THRESHOLD_COLOR, ha="center",
        )

    # --- Cell probability on secondary axis ---
    if show_probability:
        ax2 = ax.twinx()
        prob = compute_cell_probability(ranked_counts, inflection_rank)
        ax2.plot(
            ranks, prob,
            color=CELL_PROB_COLOR, linewidth=1.2, alpha=0.65,
            linestyle="-.", zorder=2,
        )
        ax2.set_ylabel("P(cell)", color=CELL_PROB_COLOR)
        ax2.set_ylim(-0.05, 1.05)
        ax2.set_xscale("log")
        ax2.tick_params(axis="y", labelcolor=CELL_PROB_COLOR)
        for spine in ax2.spines.values():
            spine.set_color(CELL_PROB_COLOR)
            spine.set_linewidth(0.6)

    # --- Axes labels ---
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontweight="bold", pad=8)

    # --- Polish ---
    apply_gallery_polish(ax)

    # --- Save ---
    if save_path:
        save_fig(ax.figure if external_ax else fig,
                 Path(save_path).stem, transparent=False)

    return ax


# ============ CLI / Demo ============

if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig

    load_sci_style("gallery")

    ranked = generate_mock_data(n_cells=2500, n_background=7500, seed=42)
    knee = detect_inflection(ranked)

    fig, ax_main = plt.subplots(figsize=(8, 5.6))
    ax_main = plot(
        ranked,
        inflection_rank=knee,
        threshold=500,
        show_probability=True,
        xlabel="Barcode rank",
        ylabel="UMI counts",
        title="Knee Plot — Droplet scRNA-seq Barcode Filtering",
        preset="gallery",
        ax=ax_main,
    )

    name = Path(__file__).stem
    save_fig(ax_main.figure, name, dpi=180, fmt="both")
    plt.close(ax_main.figure)

    print(f"Knee plot saved. Inflection rank: {knee:,}")
