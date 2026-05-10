"""基础绘图工具 — 所有模板共用的辅助函数。

统一风格加载、双版本导出、adjustText标签、字号缩放。
v2: 增加presentation gallery模式、plot area风格增强。
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patheffects
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
    
    # matplotlibrc cannot parse some values — set via Python
    from cycler import cycler
    plt.rcParams['axes.prop_cycle'] = cycler('color', NATURE_COLORS)
    
    # v2: 浅灰plot area背景（hex color在rc文件中无法解析，需Python设置）
    plt.rcParams['axes.facecolor'] = '#FAFAFA'
    
    presets = {
        "publication": {},  # matplotlibrc已经设好
        "presentation": {
            "font.size": 16,
            "axes.titlesize": 18,
            "axes.labelsize": 16,
            "axes.labelweight": "bold",
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 13,
            "legend.title_fontsize": 14,
            "lines.linewidth": 2.0,
            "lines.markersize": 8,
            "lines.markeredgewidth": 0.8,
            "axes.linewidth": 1.2,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 4.5,
            "ytick.major.size": 4.5,
            "xtick.minor.size": 2.5,
            "ytick.minor.size": 2.5,
            "figure.figsize": (10, 5.6),   # 16:9
            "figure.dpi": 150,
            "savefig.dpi": 200,
        },
        "gallery": {
            # Gallery专用preset: 大字号 + 精致风格，专为网页缩略图优化
            "font.size": 14,
            "axes.titlesize": 16,
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
            "legend.title_fontsize": 12,
            "lines.linewidth": 1.8,
            "lines.markersize": 7,
            "lines.markeredgewidth": 0.6,
            "axes.linewidth": 1.0,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 4.0,
            "ytick.major.size": 4.0,
            "figure.figsize": (8, 5.6),    # 适合Gallery卡片
            "figure.dpi": 150,
            "savefig.dpi": 180,            # Gallery不需要300dpi
        },
        "poster": {
            "font.size": 24,
            "axes.titlesize": 28,
            "axes.labelsize": 24,
            "axes.labelweight": "bold",
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
            "axes.labelweight": "bold",
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


def apply_gallery_polish(ax):
    """给axes应用Gallery级别的视觉打磨。
    
    在plot()函数最后调用，增加精致感：
    - y轴淡灰grid线
    - spine颜色微调
    - pad调整
    
    适用于所有非热图类图表。
    """
    # 水平grid线（极淡）
    ax.grid(axis='y', linestyle='--', linewidth=0.4, 
            alpha=0.5, color='#CCCCCC', zorder=0)
    ax.set_axisbelow(True)
    
    # spine微调：左+底稍深，确保视觉层次
    for spine_key in ['left', 'bottom']:
        ax.spines[spine_key].set_color('#555555')
        ax.spines[spine_key].set_linewidth(plt.rcParams.get('axes.linewidth', 0.5) * 1.2)


def polish_legend(ax, ncol=1, loc='best', frame_alpha=0.92):
    """美化和调整图例位置与风格。
    
    Args:
        ax: matplotlib axes
        ncol: 列数
        loc: 位置
        frame_alpha: 背景透明度
    """
    handles, labels = ax.get_legend_handles_labels()
    if not labels:
        return None
    leg = ax.legend(ncol=ncol, loc=loc, framealpha=frame_alpha,
                    edgecolor='#CCCCCC', fancybox=True,
                    borderpad=0.6, handlelength=1.8, handletextpad=0.6)
    leg.get_frame().set_linewidth(0.6)
    return leg


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
    fig.savefig(output_dir / "demo_fig" / f"{name}_demo.png", dpi=300, bbox_inches="tight",
                pad_inches=0.05, facecolor="white")
    
    # Presentation版（透明背景，大字号）
    if preset != "presentation":
        plt.rcParams.update({
            "font.size": 16, "axes.labelsize": 16,
            "xtick.labelsize": 14, "ytick.labelsize": 14,
            "legend.fontsize": 14, "lines.linewidth": 2.0,
        })
        fig.savefig(output_dir / "demo_fig" / f"{name}_ppt.png", dpi=200, bbox_inches="tight",
                    transparent=True, facecolor="none")
        # 回到publication
        plt.rcParams.update({
            "font.size": 7, "axes.labelsize": 7,
            "xtick.labelsize": 6, "ytick.labelsize": 6,
            "legend.fontsize": 6, "lines.linewidth": 1.0,
        })


def save_fig(fig, name, output_dir: Optional[Path] = None, 
             transparent: bool = False, dpi: int = 300, fmt: str = "png"):
    """保存图片到demo_fig/。支持PNG和PDF双格式。
    
    Args:
        fig: matplotlib figure
        name: 文件名前缀（如"volcano"），不含扩展名和_demo后缀
              也接受Path对象（自动提取stem作为前缀）
        output_dir: 输出目录（默认为plotting根目录）
        transparent: 是否透明背景
        dpi: 分辨率
        fmt: "png" | "pdf" | "both"
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent
    
    # If name is a full path (e.g. from old code), extract just the prefix
    name = Path(name).stem  # e.g. "volcano_demo" from "volcano_demo.png"
    # Remove _demo suffix if present (avoid double _demo)
    if name.endswith("_demo"):
        name = name[:-5]
    
    demo_dir = output_dir / "demo_fig"
    demo_dir.mkdir(exist_ok=True)
    
    paths = []
    for save_fmt in (["png", "pdf"] if fmt == "both" else [fmt]):
        path = demo_dir / f"{name}_demo.{save_fmt}"
        kwargs = dict(dpi=dpi, bbox_inches="tight", pad_inches=0.05,
                      facecolor="none" if transparent else "white")
        if save_fmt == "pdf":
            kwargs["backend"] = "pdf"
        else:
            kwargs["transparent"] = transparent
        fig.savefig(str(path), **kwargs)
        print(f"Saved to {path}")
        paths.append(path)
    
    return paths[0] if len(paths) == 1 else paths


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

# v2: 增强型配色 - Gallery级别更深质感
GALLERY_PALETTE = {
    "up": "#E64B35",       # 鲜明红
    "down": "#3C5488",      # 深蓝
    "ns": "#C8C8C8",        # 中灰（比旧版#DBDBDB更饱和）
    "positive": "#E64B35",
    "negative": "#4DBBD5",
    "neutral": "#8491B4",
    "highlight": "#F39B7F",
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