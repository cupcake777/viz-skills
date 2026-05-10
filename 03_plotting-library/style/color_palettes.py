#!/usr/bin/env python3
"""
Scientific Color Palettes — Curated collection for publication-quality figures.

Sources:
  - Okabe-Ito (2008): Gold standard for colorblind-safe categorical data
  - Paul Tol (2021): Publication-ready qualitative/diverging/sequential
  - ggsci journal palettes: NPG, NEJM, Lancet, JAMA, JCO, AAAS
  - Crameri scientific colour maps: Perceptually uniform, CVI-safe
  - Viridis family: Matplotlib default sequential

Organization:
  - QUALITATIVE: Categorical/group comparisons (bar, line, scatter)
  - SEQUENTIAL: Continuous low→high data (heatmaps, density)
  - DIVERGING: Data with meaningful center (correlation, logFC)

Usage:
  from color_palettes import PALETTES, get_palette, list_palettes
  colors = get_palette("npg")           # Returns list of hex strings
  pal = PALETTES["okabe_ito"]           # Access dict with named keys
  list_palettes()                       # Print all available palettes
"""

# =============================================================================
# QUALITATIVE PALETTES — Categorical / Group Comparisons
# ============================================================================

PALETTES = {
    # --- Okabe-Ito / Wong (Nature Methods recommendation) ---
    "okabe_ito": {
        "name": "Okabe-Ito",
        "type": "qualitative",
        "source": "Okabe & Ito (2008), Color Universal Design",
        "colorblind_safe": True,
        "colors": {
            "orange": "#E69F00",
            "sky_blue": "#56B4E9",
            "bluish_green": "#009E73",
            "yellow": "#F0E442",
            "blue": "#0072B2",
            "vermillion": "#D55E00",
            "reddish_purple": "#CC79A7",
            "black": "#000000",
        },
    },

    # --- Paul Tol Palettes ---
    "tol_bright": {
        "name": "Paul Tol Bright",
        "type": "qualitative",
        "source": "Paul Tol (2021), srON",
        "colorblind_safe": True,
        "colors": {
            "blue": "#4477AA",
            "red": "#EE6677",
            "green": "#228833",
            "yellow": "#CCBB44",
            "cyan": "#66CCEE",
            "purple": "#AA3377",
            "grey": "#BBBBBB",
        },
    },

    "tol_vibrant": {
        "name": "Paul Tol Vibrant",
        "type": "qualitative",
        "source": "Paul Tol (2021), srON — designed for TensorBoard",
        "colorblind_safe": True,
        "colors": {
            "blue": "#0077BB",
            "cyan": "#33BBEE",
            "teal": "#009988",
            "orange": "#EE7733",
            "red": "#CC3311",
            "magenta": "#EE3377",
            "grey": "#BBBBBB",
        },
    },

    "tol_muted": {
        "name": "Paul Tol Muted",
        "type": "qualitative",
        "source": "Paul Tol (2021), srON — 9 color + bad data grey",
        "colorblind_safe": True,
        "colors": {
            "indigo": "#332288",
            "cyan": "#88CCEE",
            "teal": "#44AA99",
            "green": "#117733",
            "olive": "#999933",
            "sand": "#DDCC77",
            "rose": "#CC6677",
            "wine": "#882255",
            "purple": "#AA4499",
            "bad_data": "#DDDDDD",
        },
    },

    "tol_high_contrast": {
        "name": "Paul Tol High Contrast",
        "type": "qualitative",
        "source": "Paul Tol (2021), srON — maximum contrast, 3 colors",
        "colorblind_safe": True,
        "colors": {
            "dark_blue": "#004488",
            "yellow": "#DDAA33",
            "red": "#BB5566",
        },
    },

    # --- Scientific Journal Palettes (ggsci) ---

    "npg": {
        "name": "NPG (Nature Reviews Cancer)",
        "type": "qualitative",
        "source": "Nature Publishing Group, via ggsci",
        "colorblind_safe": False,  # red+green proximity issues
        "colors": {
            "red": "#E64B35",
            "cyan_blue": "#4DBBD5",
            "green": "#00A087",
            "navy": "#3C5488",
            "salmon": "#F39B7F",
            "slate": "#8491B8",
            "mint": "#91D1C2",
            "crimson": "#DC0000",
            "brown": "#7E6148",
            "tan": "#B09C85",
        },
    },

    "nejm": {
        "name": "NEJM",
        "type": "qualitative",
        "source": "New England Journal of Medicine, via ggsci",
        "colorblind_safe": True,
        "colors": {
            "dark_red": "#BC3C29",
            "blue": "#0072B5",
            "orange": "#E18727",
            "green": "#20854E",
            "purple": "#7876B1",
            "steel": "#6F99AD",
            "gold": "#FFDC91",
            "pink": "#EE4C97",
        },
    },

    "lancet": {
        "name": "Lancet",
        "type": "qualitative",
        "source": "The Lancet, via ggsci",
        "colorblind_safe": True,
        "colors": {
            "blue": "#00468B",
            "red": "#ED0000",
            "green": "#42B540",
            "teal": "#0099B5",
            "purple": "#925E9F",
            "peach": "#FDAF91",
            "dark_red": "#AD002A",
            "grey": "#ADB6B6",
        },
    },

    "jama": {
        "name": "JAMA",
        "type": "qualitative",
        "source": "Journal of the American Medical Association, via ggsci",
        "colorblind_safe": True,
        "colors": {
            "charcoal": "#374E55",
            "orange": "#DF8D5B",
            "navy": "#003B5C",
            "rust": "#B6370E",
            "sky": "#56B3E0",
            "teal": "#00A087",
        },
    },

    "jco": {
        "name": "JCO",
        "type": "qualitative",
        "source": "Journal of Clinical Oncology, via ggsci",
        "colorblind_safe": True,
        "colors": {
            "blue": "#0073A8",
            "amber": "#E08B28",
            "magenta": "#A0244D",
            "light_blue": "#56B3E0",
            "navy": "#3C5488",
            "mint": "#91D1C2",
            "red": "#DC0000",
            "brown": "#7E6148",
        },
    },

    "aaas": {
        "name": "AAAS (Science)",
        "type": "qualitative",
        "source": "American Association for the Advancement of Science, via ggsci",
        "colorblind_safe": False,
        "colors": {
            "indigo": "#3B4BA0",
            "red": "#EB0E2F",
            "periwinkle": "#7B95D1",
            "salmon": "#EF7C5E",
            "teal": "#68AABA",
            "lavender": "#C598C5",
        },
    },

    # --- Genomics / Bioinformatics Specific ---

    "fluorophore_accessible": {
        "name": "Fluorophore Channels (Colorblind-Safe)",
        "type": "qualitative",
        "source": "Adapted from Okabe-Ito for fluorescence microscopy",
        "colorblind_safe": True,
        "colors": {
            "ch1_blue": "#0072B2",
            "ch2_orange": "#E69F00",
            "ch3_vermillion": "#D55E00",
            "ch4_magenta": "#CC79A7",
            "ch5_yellow": "#F0E442",
        },
    },

    "dna_bases_accessible": {
        "name": "DNA Bases (Colorblind-Safe)",
        "type": "qualitative",
        "source": "Adapted for sequence visualization",
        "colorblind_safe": True,
        "colors": {
            "A": "#009E73",   # green
            "C": "#0072B2",   # blue
            "G": "#E69F00",   # orange
            "T": "#D55E00",   # vermillion
        },
    },

    "dna_bases_traditional": {
        "name": "DNA Bases (Traditional, NOT colorblind-safe)",
        "type": "qualitative",
        "source": "Traditional genomics coloring — AVOID for publications",
        "colorblind_safe": False,
        "colors": {
            "A": "#00CC00",
            "C": "#0000CC",
            "G": "#FFB300",
            "T": "#CC0000",
        },
    },

    # --- UCSC Genome Browser ---
    "ucscgb": {
        "name": "UCSC Genome Browser",
        "type": "qualitative",
        "source": "UCSC Genome Browser default track colors, via ggsci",
        "colorblind_safe": False,
        "colors": {
            "c1": "#FF0000", "c2": "#CC9900", "c3": "#FF00FF",
            "c4": "#009900", "c5": "#0000FF", "c6": "#663300",
            "c7": "#00CCFF", "c8": "#9966CC", "c9": "#666600",
            "c10": "#FF6600", "c11": "#99CC00", "c12": "#990000",
            "c13": "#009999", "c14": "#993366", "c15": "#660099",
        },
    },

    # --- LocusZoom (GWAS) ---
    "locuszoom": {
        "name": "LocusZoom",
        "type": "qualitative",
        "source": "LocusZoom GWAS visualization default, via ggsci",
        "colorblind_safe": False,
        "colors": {
            "c1": "#D43F3F", "c2": "#3F7FCC", "c3": "#7F7F7F",
        },
    },

    # --- COSMIC Cancer Hallmarks ---
    "cosmic_hallmarks_light": {
        "name": "COSMIC Hallmarks (Light)",
        "type": "qualitative",
        "source": "COSMIC cancer hallmark pathways, via ggsci",
        "colorblind_safe": False,
        "colors": {
            "proliferative": "#EE7B4B",
            "growth": "#A07AB5",
            "dna_damage": "#F1AE6D",
            "immortal": "#5EB4C5",
            "angiogenesis": "#C6602D",
            "invasion": "#ABABAB",
            "immune": "#298C2F",
            "tumor_microenvironment": "#42BE73",
            "genome_instability": "#C06E9E",
            "metabolism": "#CC6677",
        },
    },
}

# =============================================================================
# SEQUENTIAL & DIVERGING PALETTES (colormap names for matplotlib)
# ============================================================================

SEQUENTIAL_CMAPS = {
    # --- Viridis family (matplotlib built-in, perceptually uniform) ---
    "viridis": {
        "name": "Viridis",
        "type": "sequential",
        "source": "van der Walt & Smith (2015), matplotlib default",
        "colorblind_safe": True,
        "description": "Blue→Green→Yellow, most versatile",
        "usage": "General purpose heatmaps, density plots",
    },
    "magma": {
        "name": "Magma",
        "type": "sequential",
        "source": "van der Walt & Smith (2015)",
        "colorblind_safe": True,
        "description": "Black→Purple→Orange→White, high contrast",
        "usage": "Dark backgrounds, dramatic effect",
    },
    "inferno": {
        "name": "Inferno",
        "type": "sequential",
        "source": "van der Walt & Smith (2015)",
        "colorblind_safe": True,
        "description": "Black→Purple→Red→Yellow, dramatic",
        "usage": "Publications needing strong visual impact",
    },
    "plasma": {
        "name": "Plasma",
        "type": "sequential",
        "source": "van der Walt & Smith (2015)",
        "colorblind_safe": True,
        "description": "Purple→Pink→Orange→Yellow",
        "usage": "3D surface plots, no black endpoint",
    },
    "cividis": {
        "name": "Cividis",
        "type": "sequential",
        "source": "Nuñez et al. (2018)",
        "colorblind_safe": True,
        "description": "Blue→Yellow, optimized for CVD",
        "usage": "Maximum colorblind accessibility",
    },

    # --- Crameri Scientific Colour Maps (perceptually uniform) ---
    "batlow": {
        "name": "Batlow",
        "type": "sequential",
        "source": "Crameri (2018), Scientific Colour Maps v8.0",
        "colorblind_safe": True,
        "description": "Low-contrast, perceptually uniform gold-blue",
        "usage": "General purpose, CVD-safe sequential data",
    },
    "devon": {
        "name": "Devon",
        "type": "sequential",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Warm tones, perceptually uniform",
        "usage": "Geoscience, temperature data",
    },
    "lapaz": {
        "name": "LaPaz",
        "type": "sequential",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Cool blue tones, perceptually uniform",
        "usage": "Depth/topography data, oceanography",
    },
    "hawaii": {
        "name": "Hawaii",
        "type": "sequential",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Tropical tones, vibrant sequential",
        "usage": "Eye-catching presentations",
    },
    "glasbey": {
        "name": "Glasbey",
        "type": "qualitative",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Maximally distinct categorical colors (>20)",
        "usage": "Multi-category data (>10 groups), cluster labels",
    },
    "glasbey_bw": {
        "name": "Glasbey B&W",
        "type": "qualitative",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Maximally distinct + B&W safe",
        "usage": "Publications requiring print-friendly multicolor",
    },
}

DIVERGING_CMAPS = {
    # --- Crameri Diverging ---
    "roma": {
        "name": "Roma",
        "type": "diverging",
        "source": "Crameri (2018), Scientific Colour Maps",
        "colorblind_safe": True,
        "description": "Warm→White→Cool (brown→white→blue)",
        "usage": "Correlation matrices, logFC heatmaps",
    },
    "vik": {
        "name": "Vik",
        "type": "diverging",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Cool→White→Warm (blue→white→red-flip)",
        "usage": "Opposite direction from Roma",
    },
    "broc": {
        "name": "Broc",
        "type": "diverging",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Green→White→Blue",
        "usage": "Alternative diverging scheme",
    },
    "cork": {
        "name": "Cork",
        "type": "diverging",
        "source": "Crameri (2018)",
        "colorblind_safe": True,
        "description": "Brown→White→Teal",
        "usage": "Alternative diverging scheme",
    },

    # --- Paul Tol Diverging ---
    "tol_sunset": {
        "name": "Tol Sunset",
        "type": "diverging",
        "source": "Paul Tol (2021)",
        "colorblind_safe": True,
        "description": "Blue→Yellow→Red (11 colors)",
        "usage": "Deviation from reference, fold change",
    },
    "tol_burd": {
        "name": "Tol BuRd",
        "type": "diverging",
        "source": "Paul Tol (2021), tweaked ColorBrewer RdBu",
        "colorblind_safe": True,
        "description": "Blue→White→Red (9 colors)",
        "usage": "Classic diverging, gene expression",
    },

    # --- Matplotlib Diverging (built-in) ---
    "rdylbu": {
        "name": "RdYlBu",
        "type": "diverging",
        "source": "ColorBrewer, matplotlib built-in",
        "colorblind_safe": True,
        "description": "Red→Yellow→Blue",
        "usage": "Classic diverging, correlation",
    },
    "puor": {
        "name": "PuOr",
        "type": "diverging",
        "source": "ColorBrewer, matplotlib built-in",
        "colorblind_safe": True,
        "description": "Purple→White→Orange",
        "usage": "Alternative diverging, less common",
    },
}

# =============================================================================
# APA / GENOMICS SPECIALTY
# ============================================================================

GENOMICS_PALETTES = {
    "gwas_significance": {
        "name": "GWAS Manhattan Significance",
        "type": "qualitative",
        "source": "Standard GWAS convention",
        "colorblind_safe": False,
        "description": "Chromosome alternating colors for Manhattan plots",
        "colors": {
            "chr_even": "#3366CC",
            "chr_odd": "#CC3333",
            "genome_wide_line": "#D55E00",
            "suggestive_line": "#0072B2",
        },
    },
    "volcano_up_down_ns": {
        "name": "Volcano Plot (Up/Down/NS)",
        "type": "qualitative",
        "source": "Standard differential expression convention",
        "colorblind_safe": True,
        "colors": {
            "up_regulated": "#D55E00",    # vermillion
            "down_regulated": "#0072B2",  # blue
            "not_significant": "#BBBBBB",  # grey
            "threshold_line": "#000000",   # black
        },
    },
    "apa_pattern": {
        "name": "APA Usage Pattern",
        "type": "qualitative",
        "source": "Convention for 3'UTR alternative polyadenylation",
        "colorblind_safe": True,
        "colors": {
            "proximal": "#E64B35",    # NPG red
            "distal": "#4DBBD5",     # NPG cyan
            "no_change": "#8491B8",  # NPG slate
        },
    },
    "survival_curves": {
        "name": "KM Survival Curves",
        "type": "qualitative",
        "source": "High-contrast pairs for risk group comparison",
        "colorblind_safe": True,
        "colors": {
            "group_high": "#D55E00",   # vermillion
            "group_low": "#0072B2",   # blue
            "censored": "#BBBBBB",    # grey
            "confidence_band_high": "#D55E0040",
            "confidence_band_low": "#0072B240",
        },
    },
}

# =============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_palette(name: str, as_list: bool = True) -> list | dict:
    """Get a qualitative color palette by name.

    Args:
        name: Palette name (e.g., 'npg', 'okabe_ito', 'tol_bright', 'nejm')
        as_list: If True, return list of hex strings; if False, return full dict

    Returns:
        List of hex color strings (as_list=True) or full palette dict
    """
    key = name.lower().replace("-", "_").replace(" ", "_")

    # Search in all palette collections
    for collection in [PALETTES, GENOMICS_PALETTES]:
        if key in collection:
            if as_list:
                return list(collection[key]["colors"].values())
            return collection[key]

    raise ValueError(
        f"Unknown palette '{name}'. "
        f"Use list_palettes() to see available options."
    )


def list_palettes() -> None:
    """Print all available palette names with brief info."""
    print("=== Qualitative Palettes ===")
    for key, pal in PALETTES.items():
        n = len(pal["colors"])
        cvd = "✓" if pal.get("colorblind_safe") else "✗"
        print(f"  {key:25s}  {pal['name']:40s}  {n} colors  CVD:{cvd}")

    print("\n=== Genomics Palettes ===")
    for key, pal in GENOMICS_PALETTES.items():
        n = len(pal["colors"])
        cvd = "✓" if pal.get("colorblind_safe") else "✗"
        print(f"  {key:25s}  {pal['name']:40s}  {n} colors  CVD:{cvd}")

    print("\n=== Sequential Colormaps (matplotlib) ===")
    for key, info in SEQUENTIAL_CMAPS.items():
        cvd = "✓" if info.get("colorblind_safe") else "✗"
        print(f"  {key:20s}  {info['name']:25s}  CVD:{cvd}  → {info['description']}")

    print("\n=== Diverging Colormaps (matplotlib) ===")
    for key, info in DIVERGING_CMAPS.items():
        cvd = "✓" if info.get("colorblind_safe") else "✗"
        print(f"  {key:20s}  {info['name']:25s}  CVD:{cvd}  → {info['description']}")


def apply_palette(name: str, n_colors: int = None) -> list:
    """Set matplotlib color cycle to a named palette and return colors.

    Args:
        name: Palette name (e.g., 'npg', 'okabe_ito')
        n_colors: If set, interpolate to exactly this many colors

    Returns:
        List of hex color strings applied to matplotlib
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    colors = get_palette(name, as_list=True)

    if n_colors and n_colors != len(colors):
        # Interpolate to desired number of colors
        from matplotlib.colors import to_rgba
        rgba_colors = [to_rgba(c) for c in colors]
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            f"custom_{name}", rgba_colors, N=n_colors
        )
        colors = [mpl.colors.to_hex(cmap(i / n_colors)) for i in range(n_colors)]

    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=colors)
    return colors


def demo_palette(name: str, save_path: str = None) -> None:
    """Generate a demo plot showing a palette's colors as a horizontal bar.

    Args:
        name: Palette name
        save_path: If provided, save to this path; otherwise show
    """
    import matplotlib.pyplot as plt
    import numpy as np

    colors = get_palette(name, as_list=True)
    pal_info = get_palette(name, as_list=False)

    fig, ax = plt.subplots(figsize=(max(8, len(colors) * 0.8), 1.5))
    for i, c in enumerate(colors):
        ax.barh(0, 1, left=i, color=c, edgecolor="white", linewidth=1.5)
        ax.text(i + 0.5, -0.4, c, ha="center", va="top", fontsize=7,
                fontfamily="monospace")

    ax.set_xlim(0, len(colors))
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    title = pal_info.get("name", name)
    cvd = "CVD-safe" if pal_info.get("colorblind_safe") else "NOT CVD-safe"
    ax.set_title(f"{title}  ({cvd})", fontsize=11, fontweight="bold")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved to {save_path}")
    else:
        plt.show()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            list_palettes()
        elif cmd == "show":
            name = sys.argv[2] if len(sys.argv) > 2 else "npg"
            colors = get_palette(name)
            print(f"{name}: {colors}")
        elif cmd == "demo":
            name = sys.argv[2] if len(sys.argv) > 2 else "npg"
            out = sys.argv[3] if len(sys.argv) > 3 else None
            demo_palette(name, save_path=out)
        elif cmd == "apply":
            name = sys.argv[2] if len(sys.argv) > 2 else "npg"
            colors = apply_palette(name)
            print(f"Applied {name}: {colors}")
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: color_palettes.py [list|show|demo|apply] [palette_name]")
    else:
        list_palettes()