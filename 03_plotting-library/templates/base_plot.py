"""基础绘图工具 — 所有模板共用的辅助函数。

统一风格加载、双版本导出、adjustText标签、字号缩放。
"""

import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Tuple, List

# ─── 风格加载 ──────────────────────────────────────────

STYLE_PATH = Path(__file__).parent.parent / "style" / "matplotlibrc"


def load_sci_style(preset: str = "publication") -> dict:
    """加载全局matplotlibrc风格，返回可覆盖的preset参数。
    
    Args:
        preset: "publication"(7pt), "presentation"(16pt), "poster"(24pt), "draft"(12pt)
    
    Returns:
        dict: 可传入 plt.rcParams.update() 的preset覆盖字典
    """
    matplotlib.rc_file(str(STYLE_PATH))
    
    # matplotlibrc cannot parse cycler — set it via Python
    from cycler import cycler
    plt.rcParams['axes.prop_cycle'] = cycler('color', NATURE_COLORS)
    
    presets = {
        "publication": {},  # matplotlibrc已经设好
        "presentation": {
            "font.size": 16,
            "axes.titlesize": 18,
            "axes.labelsize": 16,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 14,
            "legend.title_fontsize": 16,
            "lines.linewidth": 2.0,
            "lines.markersize": 8,
            "lines.markeredgewidth": 0.8,
            "axes.linewidth": 1.5,
            "xtick.major.width": 1.0,
            "ytick.major.width": 1.0,
            "figure.figsize": (10, 5.6),   # 16:9
            "figure.dpi": 150,
            "savefig.dpi": 200,
        },
        "poster": {
            "font.size": 24,
            "axes.titlesize": 28,
            "axes.labelsize": 24,
            "xtick.labelsize": 20,
            "ytick.labelsize": 20,
            "legend.fontsize": 20,
            "legend.title_fontsize": 24,
            "lines.linewidth": 3.0,
            "lines.markersize": 12,
            "axes.linewidth": 2.0,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        },
        "draft": {
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "figure.figsize": (8, 6),
            "figure.dpi": 100,
            "savefig.dpi": 100,
        },
    }
    
    override = presets.get(preset, {})
    if override:
        plt.rcParams.update(override)
    return override


# ─── 双版本导出 ──────────────────────────────────────────

def save_dual(fig, name: str, output_dir: Optional[Path] = None, 
              preset: str = "publication"):
    """保存publication + presentation双版本。
    
    Args:
        fig: matplotlib figure
        name: 文件名前缀（不含扩展名）
        output_dir: 输出目录，默认为plotting根目录
        preset: 当前preset，决定哪个是主版本
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    # Publication版
    fig.savefig(output_dir / f"{name}_demo.png", dpi=300, bbox_inches="tight",
                pad_inches=0.02, facecolor="white")
    
    # Presentation版（透明背景，大字号）
    if preset != "presentation":
        plt.rcParams.update({
            "font.size": 16, "axes.labelsize": 16,
            "xtick.labelsize": 14, "ytick.labelsize": 14,
            "legend.fontsize": 14, "lines.linewidth": 2.0,
        })
        fig.savefig(output_dir / f"{name}_ppt.png", dpi=200, bbox_inches="tight",
                    transparent=True, facecolor="none")
        # 回到publication
        plt.rcParams.update({
            "font.size": 7, "axes.labelsize": 7,
            "xtick.labelsize": 6, "ytick.labelsize": 6,
            "legend.fontsize": 6, "lines.linewidth": 1.0,
        })


def save_fig(fig, name: str, output_dir: Optional[Path] = None, 
             transparent: bool = False, dpi: int = 300):
    """保存单版本图片。
    
    Args:
        fig: matplotlib figure
        name: 文件名前缀
        output_dir: 输出目录
        transparent: 是否透明背景（PPT用时True）
        dpi: 分辨率
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    path = output_dir / f"{name}_demo.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.02,
                transparent=transparent, facecolor="none" if transparent else "white")
    print(f"Saved to {path}")
    return path


# ─── adjustText标签 ──────────────────────────────────────

def auto_label(ax, texts: List[str], x: List, y: List, 
               sizes=None, fontsize: int = 7, **kwargs):
    """自动防重叠标注。
    
    优先用 adjustText.adjust_text，回退用 ax.annotate。
    
    Args:
        ax: matplotlib axes
        texts: 标签文本列表
        x: x坐标
        y: y坐标  
        sizes: 点大小（可选）
        fontsize: 字号
        **kwargs: 传给 adjust_text 的参数
    """
    try:
        from adjustText import adjust_text
        annotations = []
        for t, xi, yi in zip(texts, x, y):
            ann = ax.annotate(t, (xi, yi), fontsize=fontsize, 
                            fontweight="bold", ha="center", va="bottom")
            annotations.append(ann)
        adjust_text(annotations, ax=ax, 
                    arrowprops=dict(arrowstyle="-", color="0.5", lw=0.5),
                    force_text=(0.3, 0.3), 
                    force_points=(0.3, 0.3),
                    **kwargs)
    except ImportError:
        # 回退：简单偏移标注
        for t, xi, yi in zip(texts, x, y):
            ax.annotate(t, (xi, yi), fontsize=fontsize,
                       fontweight="bold", ha="center", va="bottom",
                       xytext=(0, 5), textcoords="offset points",
                       clip_on=True)


# ─── 配色工具 ─────────────────────────────────────────────

# Nature Primary 6
NATURE_COLORS = ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4"]

# APA研究专用
APA_STAGE_COLORS = {
    "Fetal": "#4DBBD5",
    "Neonatal": "#00A087", 
    "Infant": "#3C5488",
    "Child": "#91D1C2",
    "Adolescent": "#F39B7F",
    "Adult": "#E64B35",
    "Aged": "#8491B4",
}

APA_PATTERN_COLORS = {
    "Lengthening": "#E64B35",     # 红色 - 3'UTR延长
    "Shortening": "#4DBBD5",      # 蓝色 - 3'UTR缩短
    "Switch": "#00A087",          # 绿色 - 模式切换
    "No change": "#B0B0B0",       # 灰色 - 无变化
}

NEURO_COLORS = {
    "Control": "#3C5488",
    "MDD": "#E64B35",
    "SCZ": "#4DBBD5",
    "BD": "#00A087",
    "ASD": "#F39B7F",
}


def get_stage_cmap(stages=None):
    """获取发育阶段连续色标。
    
    Returns matplotlib colormap适合发育渐变(mako风格)。
    """
    from matplotlib.colors import LinearSegmentedColormap
    if stages is None:
        stages = ["Fetal", "Infant", "Child", "Adolescent", "Adult", "Aged"]
    colors = [APA_STAGE_COLORS.get(s, "#999999") for s in stages]
    return LinearSegmentedColormap.from_list("stages", colors, N=256)