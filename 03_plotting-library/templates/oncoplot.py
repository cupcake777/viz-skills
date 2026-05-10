"""
Oncoplot (OncoPrint)
====================
Mutation landscape heatmap showing mutation patterns across samples.

适用数据类型: genomics, somatic_mutations
必需输入: mutation matrix (genes x samples), gene list, sample list

参考: cBioPortal OncoPrint, GenVisR
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
sys.path.insert(0, str(Path(__file__).parent))
from base_plot import load_sci_style, save_fig, polish_legend, apply_gallery_polish

# Mutation type codes
MUTATION_TYPES = {
    0: 'None', 1: 'Missense', 2: 'Nonsense', 3: 'Frameshift',
    4: 'Splice site', 5: 'In-frame indel', 6: 'Amplification', 7: 'Deletion'
}


def generate_mock_data(seed=12):
    """Generate mock mutation matrix for an oncoplot.

    Returns
    -------
    matrix : np.ndarray of shape (n_genes, n_samples), values 0-7
    genes : list of str
    samples : list of str
    """
    rng = np.random.default_rng(seed)
    genes = ['TP53', 'PIK3CA', 'KRAS', 'PTEN', 'APC', 'EGFR', 'TTN', 'CDH1',
             'ARID1A', 'KMT2D', 'FBXW7', 'ERBB2']
    samples = [f'S{i:03d}' for i in range(1, 26)]

    freq = [0.40, 0.28, 0.20, 0.18, 0.15, 0.12, 0.10, 0.09,
            0.08, 0.07, 0.06, 0.05]

    matrix = np.zeros((len(genes), len(samples)), dtype=int)
    for gi, f in enumerate(freq):
        n_mut = max(1, int(f * len(samples)))
        mut_samples = rng.choice(len(samples), n_mut, replace=False)
        for si in mut_samples:
            weights = [0, 50, 15, 15, 10, 5, 3, 2]
            matrix[gi, si] = rng.choice(range(8),
                                        p=np.array(weights) / sum(weights))

    # Add co-occurrence patterns
    for si in range(0, 8):
        matrix[0, si] = rng.choice([1, 2, 3])
        matrix[1, si] = rng.choice([1, 6])

    # Sort by mutation burden
    sample_order = np.argsort(-matrix.sum(axis=0))
    gene_order = np.argsort(-matrix.sum(axis=1))
    matrix = matrix[gene_order][:, sample_order]
    genes_sorted = [genes[i] for i in gene_order]
    samples_sorted = [samples[i] for i in sample_order]

    return matrix, genes_sorted, samples_sorted


def plot(matrix, genes, samples, figsize=(16, 10),
         title='OncoPrint: Mutation Landscape of Cancer Cohort',
         preset='gallery'):
    """
    Draw an OncoPrint-style mutation landscape plot.

    Parameters
    ----------
    matrix : np.ndarray, shape (n_genes, n_samples), int values 0-7
        0=None, 1=Missense, 2=Nonsense, 3=Frameshift,
        4=Splice site, 5=In-frame indel, 6=Amplification, 7=Deletion
    genes : list of str, gene names (rows)
    samples : list of str, sample IDs (columns)
    figsize : tuple, figure size
    title : str, suptitle
    preset : str, style preset
    """
    load_sci_style(preset)

    # Use NPG palette for mutation types (skip index 0 = None)
    pal = get_palette("npg")
    type_colors = {
        0: '#F5F5F5',   # None — light grey (not from palette)
        1: pal[1],      # Missense — cyan_blue
        2: pal[0],      # Nonsense — red
        3: pal[2],      # Frameshift — green
        4: pal[4],      # Splice site — salmon
        5: pal[5],      # In-frame indel — slate
        6: pal[7],      # Amplification — crimson
        7: pal[3],      # Deletion — navy
    }

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[0.85, 0.15],
        height_ratios=[0.12, 0.88],
        hspace=0.02, wspace=0.02
    )

    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)

    n_genes = len(genes)
    n_samples = len(samples)

    # ── Main heatmap ──
    for gi in range(n_genes):
        for si in range(n_samples):
            val = matrix[gi, si]
            rect = plt.Rectangle(
                (si, gi), 1, 1,
                facecolor=type_colors[val],
                edgecolor='white', linewidth=0.3
            )
            ax_main.add_patch(rect)
            if val > 0:
                if val in [2, 3, 4]:  # Truncating — X marker
                    ax_main.plot(si + 0.5, gi + 0.5, marker='x',
                                 color='white', markersize=4,
                                 markeredgewidth=1.5)
                elif val == 6:  # Amp — triangle up
                    ax_main.plot(si + 0.5, gi + 0.3, marker='^',
                                 color='white', markersize=5)
                elif val == 7:  # Del — triangle down
                    ax_main.plot(si + 0.5, gi + 0.3, marker='v',
                                 color='white', markersize=5)

    ax_main.set_xlim(0, n_samples)
    ax_main.set_ylim(0, n_genes)
    ax_main.set_xticks([])
    ax_main.set_yticks(np.arange(0.5, n_genes + 0.5))
    ax_main.set_yticklabels(genes, fontsize=9.5,
                            fontfamily='monospace', fontweight='bold')
    ax_main.invert_yaxis()
    ax_main.set_xlabel('')
    ax_main.tick_params(left=False)
    ax_main.spines[:].set_visible(False)

    # ── Top bar: mutations per sample ──
    mut_counts = (matrix > 0).sum(axis=0)
    ax_top.bar(range(n_samples), mut_counts, color=pal[3],
               width=0.8, align='edge')
    ax_top.set_xlim(0, n_samples)
    ax_top.set_ylabel('# Mutations', fontsize=9, fontweight='bold')
    ax_top.set_xticks([])
    ax_top.spines['top'].set_visible(False)
    ax_top.spines['right'].set_visible(False)
    ax_top.spines['bottom'].set_visible(False)
    ax_top.tick_params(bottom=False, labelsize=8)

    # ── Right bar: % altered per gene ──
    alt_pct = (matrix > 0).sum(axis=1) / n_samples * 100
    ax_right.barh(range(n_genes), alt_pct, color=pal[0],
                  height=0.8, align='edge')
    ax_right.set_ylim(0, n_genes)
    ax_right.set_xlabel('% Altered', fontsize=9, fontweight='bold')
    ax_right.set_yticks([])
    ax_right.invert_yaxis()
    ax_right.spines['top'].set_visible(False)
    ax_right.spines['right'].set_visible(False)
    ax_right.spines['left'].set_visible(False)
    ax_right.tick_params(left=False, labelsize=8)

    # ── Title ──
    if title:
        full_title = f"{title} (n={n_samples})"
        fig.suptitle(full_title, fontsize=14, fontweight='bold', y=0.98)

    # ── Legend ──
    legend_elements = [
        mpatches.Patch(facecolor=type_colors[1], edgecolor='gray',
                       label='Missense'),
        mpatches.Patch(facecolor=type_colors[2], edgecolor='gray',
                       label='Nonsense'),
        mpatches.Patch(facecolor=type_colors[3], edgecolor='gray',
                       label='Frameshift'),
        mpatches.Patch(facecolor=type_colors[4], edgecolor='gray',
                       label='Splice site'),
        mpatches.Patch(facecolor=type_colors[5], edgecolor='gray',
                       label='In-frame indel'),
        mpatches.Patch(facecolor=type_colors[6], edgecolor='gray',
                       label='Amplification'),
        mpatches.Patch(facecolor=type_colors[7], edgecolor='gray',
                       label='Deletion'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4,
               fontsize=9, framealpha=0.9, bbox_to_anchor=(0.5, 0.01))

    return fig, ax_main


if __name__ == "__main__":
    load_sci_style("gallery")
    matrix, genes, samples = generate_mock_data()
    fig, ax = plot(matrix, genes, samples, preset="gallery")
    name = Path(__file__).stem
    save_fig(fig, name, dpi=180, fmt="both")
    plt.close(fig)
