"""
Trajectory Plot (Palantir-style)
================================
Directional arrow plot on 2D embeddings showing developmental trajectories
with pseudotime coloring and branch annotations. Inspired by Palantir's
trajectory inference visualization.

Applicable data type: trajectory / pseudotime / embedding
Required columns: umap_1, umap_2, pseudotime
Optional columns: branch

Reference: Setty et al., Nature Biotechnology 2019 (Palantir)
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish, polish_legend, SEMANTIC_COLORS
)

# ============ Configuration ============
BG_COLOR = "lightgrey"
BG_ALPHA = 0.3
BG_SIZE = 8
FG_SIZE = 18
FG_ALPHA = 0.85
ARROW_COLOR = "#2C2C2C"
ARROW_LINEWIDTH = 2.0
ARROW_ALPHA = 0.7
CURVE_SMOOTH = 200        # number of points per smooth curve
N_ARROWS_PER_BRANCH = 6   # number of directional arrows per branch
PSEUDOTIME_CMAP = "viridis"

BRANCH_COLORS = [
    SEMANTIC_COLORS["proposed"],    # deep blue
    SEMANTIC_COLORS["negative"],    # red
    SEMANTIC_COLORS["positive"],    # green
]


# ============ Mock data ============

def generate_mock_data(n_bg=500, n_branches=3, n_per_branch=80, seed=42):
    """Generate demo data: background embedding points + 3 branch trajectories
    emanating from a common origin with pseudotime values.

    Returns DataFrame with columns: umap_1, umap_2, pseudotime, branch
    Background cells have branch='Background' and pseudotime=NaN.
    """
    rng = np.random.default_rng(seed)

    # Background scattered cells
    bg_x = rng.normal(0, 4, n_bg)
    bg_y = rng.normal(0, 4, n_bg)
    bg_df = pd.DataFrame({
        "umap_1": bg_x,
        "umap_2": bg_y,
        "pseudotime": np.nan,
        "branch": "Background",
    })

    # Branch definitions: (angle, curvature, length)
    branch_defs = [
        {"name": "Lineage A", "angle": 70, "curvature": 0.4, "length": 8},
        {"name": "Lineage B", "angle": 190, "curvature": -0.3, "length": 7},
        {"name": "Lineage C", "angle": 310, "curvature": 0.5, "length": 7.5},
    ]

    frames = []
    origin = np.array([0.0, 0.0])

    for i, bdef in enumerate(branch_defs):
        n = n_per_branch + rng.integers(-10, 10)
        angle_rad = np.deg2rad(bdef["angle"])
        t = np.linspace(0, 1, CURVE_SMOOTH)

        # Smooth parametric curve
        base_dir = np.array([np.cos(angle_rad), np.sin(angle_rad)])
        perp = np.array([-base_dir[1], base_dir[0]])
        curve_x = origin[0] + bdef["length"] * t * base_dir[0] + bdef["curvature"] * np.sin(np.pi * t) * perp[0]
        curve_y = origin[1] + bdef["length"] * t * base_dir[1] + bdef["curvature"] * np.sin(np.pi * t) * perp[1]

        # Sample n points along the curve with noise
        idx = np.sort(rng.choice(CURVE_SMOOTH, size=n, replace=False))
        noise_scale = 0.35 + 0.15 * rng.random()
        x = curve_x[idx] + rng.normal(0, noise_scale, n)
        y = curve_y[idx] + rng.normal(0, noise_scale, n)
        pt = t[idx]  # pseudotime 0->1

        frames.append(pd.DataFrame({
            "umap_1": x,
            "umap_2": y,
            "pseudotime": pt,
            "branch": bdef["name"],
        }))

    branch_df = pd.concat(frames, ignore_index=True)

    # Store smooth curves for trajectory lines
    curves = {}
    for i, bdef in enumerate(branch_defs):
        angle_rad = np.deg2rad(bdef["angle"])
        t = np.linspace(0, 1, CURVE_SMOOTH)
        base_dir = np.array([np.cos(angle_rad), np.sin(angle_rad)])
        perp = np.array([-base_dir[1], base_dir[0]])
        cx = origin[0] + bdef["length"] * t * base_dir[0] + bdef["curvature"] * np.sin(np.pi * t) * perp[0]
        cy = origin[1] + bdef["length"] * t * base_dir[1] + bdef["curvature"] * np.sin(np.pi * t) * perp[1]
        curves[bdef["name"]] = (cx, cy, t)

    df = pd.concat([bg_df, branch_df], ignore_index=True)
    return df, curves


# ============ Plotting ============

def plot(
    df: pd.DataFrame,
    x_col: str = "umap_1",
    y_col: str = "umap_2",
    pseudotime_col: str = "pseudotime",
    branch_col: str = "branch",
    xlabel: str = "UMAP 1",
    ylabel: str = "UMAP 2",
    title: Optional[str] = None,
    figsize: Optional[Tuple[float, float]] = None,
    save_path: Optional[str] = None,
    ax: Optional[Axes] = None,
    preset: str = "publication",
    curves: Optional[dict] = None,
    cmap: str = PSEUDOTIME_CMAP,
):
    """
    Plot a Palantir-style trajectory on 2D embeddings.

    Parameters
    ----------
    df : DataFrame with embedding coordinates, pseudotime, and branch columns
    x_col, y_col : column names for 2D embedding coordinates
    pseudotime_col : column name for pseudotime values (NaN for background)
    branch_col : column name for branch assignments
    xlabel, ylabel : axis labels
    title : plot title
    figsize : figure size tuple
    save_path : path to save figure
    ax : optional matplotlib Axes
    preset : style preset ('publication'|'gallery'|'presentation'|'draft')
    curves : dict of {branch_name: (x_array, y_array, pseudotime_array)} for
             smooth trajectory lines. If None, lines are not drawn.
    cmap : colormap name for pseudotime

    Returns
    -------
    ax : matplotlib Axes
    """
    load_sci_style(preset)

    df = df.copy()
    bg_mask = df[branch_col] == "Background" if branch_col in df.columns else pd.Series(False, index=df.index)
    fg_mask = ~bg_mask

    branches = df.loc[fg_mask, branch_col].unique().tolist() if fg_mask.any() else []
    n_branches = len(branches)

    # --- Create figure ---
    external_ax = ax is not None
    if ax is None:
        if figsize is None:
            figsize = (8, 5.6) if preset == "gallery" else (5, 4)
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # --- Background scatter ---
    if bg_mask.any():
        ax.scatter(
            df.loc[bg_mask, x_col].values,
            df.loc[bg_mask, y_col].values,
            c=BG_COLOR, s=BG_SIZE, alpha=BG_ALPHA,
            edgecolors="none", rasterized=True, zorder=1,
        )

    # --- Foreground scatter (colored by pseudotime, per branch) ---
    norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
    cmap_obj = plt.get_cmap(cmap)
    scatter_handles = []

    for i, branch in enumerate(branches):
        mask = df[branch_col] == branch
        sub = df[mask]
        pt = sub[pseudotime_col].values
        x = sub[x_col].values
        y = sub[y_col].values

        sc = ax.scatter(
            x, y, c=pt, cmap=cmap, norm=norm,
            s=FG_SIZE, alpha=FG_ALPHA,
            edgecolors="white", linewidths=0.3,
            rasterized=True, zorder=3,
        )
        scatter_handles.append(sc)

    # --- Trajectory curves with directional arrows ---
    if curves is not None:
        for i, branch in enumerate(branches):
            if branch not in curves:
                continue
            cx, cy, ct = curves[branch]
            branch_color = BRANCH_COLORS[i % len(BRANCH_COLORS)]

            # Smooth trajectory line
            ax.plot(cx, cy, color=branch_color, lw=ARROW_LINEWIDTH,
                    alpha=ARROW_ALPHA, zorder=4, solid_capstyle="round")

            # Directional arrows along the curve
            arrow_indices = np.linspace(
                int(CURVE_SMOOTH * 0.15), int(CURVE_SMOOTH * 0.85),
                N_ARROWS_PER_BRANCH, dtype=int
            )
            for idx in arrow_indices:
                if idx + 1 >= len(cx):
                    break
                ax.annotate(
                    "",
                    xy=(cx[idx + 1], cy[idx + 1]),
                    xytext=(cx[idx], cy[idx]),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color=branch_color,
                        lw=ARROW_LINEWIDTH * 0.8,
                        mutation_scale=12,
                    ),
                    zorder=5,
                )

    # --- Colorbar for pseudotime ---
    if scatter_handles:
        cbar = fig.colorbar(scatter_handles[0], ax=ax, pad=0.02, shrink=0.8, aspect=30)
        cbar.set_label("Pseudotime", fontsize=plt.rcParams.get("font.size", 7))
        cbar.outline.set_linewidth(0.5)

    # --- Branch legend ---
    if n_branches > 1:
        from matplotlib.lines import Line2D
        legend_handles = []
        for i, branch in enumerate(branches):
            legend_handles.append(
                Line2D([0], [0], color=BRANCH_COLORS[i % len(BRANCH_COLORS)],
                       lw=ARROW_LINEWIDTH, label=branch)
            )
        ax.legend(handles=legend_handles, loc="best", frameon=True,
                  fontsize=plt.rcParams.get("font.size", 7) - 1,
                  handlelength=1.5, borderpad=0.6, labelspacing=0.5)

    # --- Labels ---
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontweight="bold", pad=8)

    apply_gallery_polish(ax)

    # --- Save ---
    if save_path:
        save_fig(ax.figure if external_ax else fig,
                 Path(save_path).stem.replace("_demo", ""),
                 transparent=False)

    return ax


# ============ CLI / Demo ============

if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig

    load_sci_style("gallery")

    df, curves = generate_mock_data(n_bg=500, n_branches=3, n_per_branch=80)
    ax = plot(
        df, curves=curves,
        xlabel="UMAP 1", ylabel="UMAP 2",
        title="Palantir-style Developmental Trajectory",
        preset="gallery",
    )
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
    print("Trajectory demo saved.")
