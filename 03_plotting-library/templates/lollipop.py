"""
Lollipop Chart
===============
Ranked items with labeled endpoints, colored by category.

适用数据类型: genomics, mutation_frequency
必需列: gene, freq
可选列: pathway

参考: cBioPortal mutational landscape lollipop plots
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
sys.path.insert(0, str(Path(__file__).parent))
from base_plot import load_sci_style, save_fig, polish_legend, apply_gallery_polish


# Pathway → category mapping for the mock data
_PATHWAY_MAP = {
    'TP53': 'Tumor Suppressor', 'APC': 'Tumor Suppressor',
    'PTEN': 'Tumor Suppressor', 'RB1': 'Tumor Suppressor',
    'CDKN2A': 'Tumor Suppressor', 'NF1': 'Tumor Suppressor',
    'STK11': 'Tumor Suppressor', 'VHL': 'Tumor Suppressor',
    'CDH1': 'Tumor Suppressor',
    'PIK3CA': 'Oncogene', 'KRAS': 'Oncogene', 'EGFR': 'Oncogene',
    'ERBB2': 'Oncogene', 'CTNNB1': 'Oncogene', 'NOTCH1': 'Oncogene',
    'FBXW7': 'Oncogene',
    'TTN': 'Structural', 'MUC16': 'Structural', 'SYNE1': 'Structural',
    'LRP1B': 'Other', 'CSMD3': 'Other', 'KEAP1': 'Other',
    'FAT4': 'Epigenetic', 'KMT2D': 'Epigenetic', 'NCOR1': 'Epigenetic',
    'ARID1A': 'Epigenetic', 'SETD2': 'Epigenetic',
    'MAP3K1': 'Signaling',
    'RUNX1': 'Transcription', 'GATA3': 'Transcription',
}


def generate_mock_data(seed=7):
    """Generate mock gene mutation frequency data for a pan-cancer cohort."""
    rng = np.random.default_rng(seed)
    genes = [
        'TP53', 'PIK3CA', 'TTN', 'MUC16', 'LRP1B', 'KRAS', 'FAT4',
        'CSMD3', 'SYNE1', 'EGFR', 'APC', 'CDH1', 'KMT2D', 'MAP3K1',
        'NCOR1', 'ARID1A', 'SETD2', 'RUNX1', 'PTEN', 'NF1',
        'RB1', 'ERBB2', 'FBXW7', 'NOTCH1', 'CTNNB1', 'GATA3',
        'CDKN2A', 'VHL', 'STK11', 'KEAP1'
    ]
    mutation_freq = [42, 28, 24, 20, 18, 17, 16, 15, 14, 13,
                     12, 11, 10, 10, 9, 9, 8, 8, 7, 7,
                     6, 6, 5, 5, 4, 4, 3, 3, 3, 2]

    df = pd.DataFrame({'gene': genes, 'freq': mutation_freq})
    df['pathway'] = df['gene'].map(_PATHWAY_MAP).fillna('Other')
    df = df.sort_values('freq', ascending=True).reset_index(drop=True)
    return df


def plot(df, gene_col='gene', freq_col='freq', pathway_col='pathway',
         figsize=(9, 11), title='Most Frequently Mutated Genes in Pan-Cancer Cohort (n=500)',
         preset='gallery'):
    """
    Draw a lollipop chart of mutation frequencies colored by pathway.

    Parameters
    ----------
    df : DataFrame, must contain gene and freq columns
    gene_col : str, column with gene/feature names (y-axis labels)
    freq_col : str, column with frequency values (x-axis)
    pathway_col : str, column with category/group for coloring
    figsize : tuple, figure size in inches
    title : str, plot title
    preset : str, style preset
    """
    load_sci_style(preset)

    pal = get_palette("npg")
    categories = sorted(df[pathway_col].unique())
    colors_map = {cat: pal[i % len(pal)] for i, cat in enumerate(categories)}

    df = df.copy()
    df = df.sort_values(freq_col, ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=False)
    fig.subplots_adjust(left=0.22, right=0.85, top=0.93, bottom=0.06)

    # Stems
    for i, row in df.iterrows():
        color = colors_map.get(row[pathway_col], pal[-1])
        ax.hlines(y=i, xmin=0, xmax=row[freq_col],
                  color=color, linewidth=2, alpha=0.8)

    # Lollipop heads
    for i, row in df.iterrows():
        color = colors_map.get(row[pathway_col], pal[-1])
        ax.scatter(row[freq_col], i, s=80, color=color,
                   edgecolors='white', linewidth=0.8, zorder=5)

    # Frequency labels
    for i, row in df.iterrows():
        ax.text(row[freq_col] + 0.8, i, f"{row[freq_col]}%",
                va='center', fontsize=8.5, color='#333333')

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df[gene_col], fontsize=9.5,
                       fontfamily='monospace', fontweight='bold')
    ax.set_xlabel('Mutation Frequency (%)', fontsize=12, fontweight='bold')
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

    ax.set_xlim(0, 50)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(axis='x', labelsize=10)
    ax.xaxis.grid(True, alpha=0.2, linestyle=':')

    # Legend by pathway
    handles = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor=colors_map[p], markersize=10, label=p)
        for p in categories if p in df[pathway_col].values
    ]
    ax.legend(handles=handles, title='Pathway', loc='lower right',
              framealpha=0.9, fontsize=8.5, title_fontsize=9)

    apply_gallery_polish(ax)
    return fig, ax


if __name__ == "__main__":
    load_sci_style("gallery")
    df = generate_mock_data()
    fig, ax = plot(df, preset="gallery")
    name = Path(__file__).stem
    save_fig(fig, name, dpi=180, fmt="both")
    plt.close(fig)
