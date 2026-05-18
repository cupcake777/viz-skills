# R/Python Theme Templates

## R (ggplot2)

```r
theme_sci <- function(base_size = 7) {
  theme_classic(base_size = base_size) +
    theme(
      text = element_text(family = "Arial"),
      axis.title = element_text(size = base_size),
      axis.text = element_text(size = base_size - 1, color = "grey30"),
      legend.title = element_text(size = base_size, face = "bold"),
      legend.text = element_text(size = base_size - 1),
      strip.text = element_text(size = base_size, face = "bold"),
      strip.background = element_blank(),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      plot.margin = margin(5, 5, 5, 5, "pt")
    )
}
```

## Python (matplotlib)

```python
SCI_RC = {
    "font.family": "Arial",
    "font.size": 7,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "axes.labelweight": "bold",
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": "#FAFAFA",
    "figure.facecolor": "white",
    "figure.dpi": 300,
}

def apply_sci_theme():
    plt.rcParams.update(SCI_RC)

def apply_gallery_polish(ax):
    ax.yaxis.grid(True, axis='y', linestyle='--', linewidth=0.4,
                  alpha=0.5, color='#CCCCCC', zorder=0)
    ax.set_axisbelow(True)
    for spine_key in ['left', 'bottom']:
        ax.spines[spine_key].set_color('#555555')
        ax.spines[spine_key].set_linewidth(
            plt.rcParams.get('axes.linewidth', 0.5) * 1.2)

def polish_legend(ax, ncol=1, loc='best', frame_alpha=0.92):
    leg = ax.legend(ncol=ncol, loc=loc, framealpha=frame_alpha,
                    edgecolor='#CCCCCC', fancybox=True,
                    borderpad=0.6, handlelength=1.8, handletextpad=0.6)
    leg.get_frame().set_linewidth(0.6)
    return leg
```

## Loading matplotlibrc

```python
from pathlib import Path
import matplotlib
STYLE_PATH = Path(__file__).parent.parent / "style" / "matplotlibrc"
matplotlib.rc_file(str(STYLE_PATH), plt.rcParams)
```

**注意**: matplotlibrc不支持hex色值和行内注释。hex色通过 `plt.rcParams` 设置，注释独占一行。
