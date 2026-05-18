"""
Forest Plot
============
Display odds ratios / hazard ratios with confidence intervals.

适用数据类型: survival_analysis, regression_results
必需列: variable, hr, ci_low, ci_high, pval
可选列: group, n

参考: Clinical epidemiology forest plots
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
from base_plot import load_sci_style, save_fig, polish_legend, apply_gallery_polish, \
    text_color_on_bg, SEMANTIC_COLORS

# ============ 参数配置 ============
SIG_P_THRESHOLD = 0.05


def generate_mock_data(seed=42):
    """Generate mock Cox regression results."""
    rng = np.random.default_rng(seed)
    data = pd.DataFrame({
        'variable': [
            'Age (per 10 years)', 'Male sex', 'BMI (per 5 kg/m2)',
            'Smoking (current)', 'Hypertension', 'Diabetes',
            'Hyperlipidemia', 'eGFR (per 10 mL/min)', 'Prior CVD',
            'Heart failure', 'Atrial fibrillation', 'Chronic lung disease'
        ],
        'group': [
            'Demographics', 'Demographics', 'Demographics',
            'Lifestyle', 'Comorbidities', 'Comorbidities',
            'Comorbidities', 'Lab values', 'Cardiac history',
            'Cardiac history', 'Cardiac history', 'Comorbidities'
        ],
        'hr': [1.12, 1.35, 1.08, 1.67, 1.45, 1.58, 1.22, 0.88, 1.89, 2.10, 1.42, 1.31],
        'ci_low': [1.01, 1.15, 0.95, 1.32, 1.20, 1.28, 1.02, 0.78, 1.55, 1.72, 1.18, 1.08],
        'ci_high': [1.24, 1.59, 1.23, 2.11, 1.76, 1.95, 1.46, 0.99, 2.30, 2.56, 1.71, 1.59],
        'pval': [0.032, 0.001, 0.18, '<0.001', '<0.001', '<0.001', 0.028, 0.035,
                 '<0.001', '<0.001', 0.003, 0.008],
        'n': [5200] * 12
    })
    data = data.sort_values('hr', ascending=True).reset_index(drop=True)
    return data


def _parse_pval(pval):
    """Parse a p-value that may be a string like '<0.001'."""
    return float(str(pval).replace('<', ''))


def plot(df, variable_col='variable', hr_col='hr', ci_low_col='ci_low',
         ci_high_col='ci_high', pval_col='pval',
         p_thresh=SIG_P_THRESHOLD, figsize=(10, 8),
         title='Multivariable Cox Regression: Predictors of Primary Outcome',
         preset='gallery'):
    """
    Draw a forest plot of hazard/odds ratios with confidence intervals.

    Parameters
    ----------
    df : DataFrame, must contain hr, ci_low, ci_high, pval columns
    variable_col : str, column with variable names (y-axis labels)
    hr_col : str, column with hazard/odds ratio point estimates
    ci_low_col : str, column with lower CI bound
    ci_high_col : str, column with upper CI bound
    pval_col : str, column with p-values (numeric or string like '<0.001')
    p_thresh : float, significance threshold for coloring
    figsize : tuple, figure size in inches
    title : str, plot title
    preset : str, style preset ("gallery", "publication", etc.)
    """
    load_sci_style(preset)

    pal = get_palette("npg")
    # Semantic color mapping (nature-skills): blue=protective, red=harmful, gray=NS
    COLOR_HARMFUL = SEMANTIC_COLORS["negative"]   # #E53935 red
    COLOR_PROTECTIVE = SEMANTIC_COLORS["proposed"]  # #0F4D92 deep blue
    COLOR_NS = SEMANTIC_COLORS["ns"]               # #BBBBBB gray

    df = df.copy()
    df = df.sort_values(hr_col, ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=False)
    fig.subplots_adjust(left=0.38, right=0.88, top=0.92, bottom=0.08)

    y_pos = np.arange(len(df))

    for i, row in df.iterrows():
        pv = _parse_pval(row[pval_col])
        hr_val = row[hr_col]
        # Direction-aware semantic coloring: harmful (HR>1) vs protective (HR<1) vs NS
        if pv >= p_thresh:
            color = COLOR_NS
        elif hr_val > 1:
            color = COLOR_HARMFUL
        else:
            color = COLOR_PROTECTIVE
        ax.errorbar(
            row[hr_col], i,
            xerr=[[row[hr_col] - row[ci_low_col]],
                  [row[ci_high_col] - row[hr_col]]],
            fmt='o', color=color, markersize=8, capsize=4,
            capthick=1.5, linewidth=1.5,
            markeredgecolor='white', markeredgewidth=0.5, zorder=5
        )

    # Reference line at HR=1
    ax.axvline(x=1, color='grey', linestyle='--', linewidth=1, alpha=0.7, zorder=1)

    # Shading for protective / harmful regions (semantic colors)
    xmin = max(ax.get_xlim()[0], 0.5)
    xmax = ax.get_xlim()[1]
    ax.axvspan(xmin, 1, alpha=0.04, color=COLOR_PROTECTIVE, zorder=0)
    ax.axvspan(1, xmax if xmax > 2.5 else 2.5, alpha=0.04, color=COLOR_HARMFUL, zorder=0)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df[variable_col], fontsize=10, fontfamily='sans-serif')
    ax.set_xlabel('Hazard Ratio (95% CI)', fontsize=12, fontweight='bold')
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

    ax.set_xlim(0.5, 2.8)
    ax.tick_params(axis='x', labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)

    # Add HR text on right side
    for i, row in df.iterrows():
        ax.text(2.65, i,
                f"{row[hr_col]:.2f} ({row[ci_low_col]:.2f}--{row[ci_high_col]:.2f})",
                va='center', ha='left', fontsize=8, color='#333333')

    # Column header
    ax.text(2.65, len(df) + 0.3, 'HR (95% CI)', fontsize=8,
            fontweight='bold', ha='left', va='center')

    # Legend — semantic: Harmful (HR>1, p<0.05), Protective (HR<1, p<0.05), NS
    harm_patch = mpatches.Patch(color=COLOR_HARMFUL, label=f'HR > 1, p < {p_thresh}')
    prot_patch = mpatches.Patch(color=COLOR_PROTECTIVE, label=f'HR < 1, p < {p_thresh}')
    nonsig_patch = mpatches.Patch(color=COLOR_NS, label=f'p ≥ {p_thresh}')
    ax.legend(handles=[harm_patch, prot_patch, nonsig_patch], loc='lower right',
              framealpha=0.9, fontsize=9, fancybox=True)

    # Grid
    ax.xaxis.grid(True, alpha=0.3, linestyle=':')

    apply_gallery_polish(ax)
    return fig, ax


if __name__ == "__main__":
    load_sci_style("gallery")
    df = generate_mock_data()
    fig, ax = plot(df, preset="gallery")
    name = Path(__file__).stem
    save_fig(fig, name, dpi=180, fmt="both")
    plt.close(fig)
