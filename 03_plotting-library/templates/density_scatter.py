"""
Density Scatter Plot (UMAP-style)
==================================
Large-dataset scatter with density-based coloring, inspired by the UMAP paper
(McInnes et al., 2018). Uses kernel density estimation to color points by local
density, revealing structure in high-overlap regions. Adaptive point sizing and
rasterized rendering keep even 50k+ points performant.

适用数据类型: dimensionality_reduction / high_density_scatter
必需列: x, y
可选列: (none — coloring is computed from density, not from group labels)

参考: UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction
      McInnes, Healy & Melville (2018), arXiv:1802.03426
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from typing import Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from base_plot import (
    load_sci_style, save_fig, apply_gallery_polish, SEMANTIC_COLORS
)

# ============ 参数配置 ============

DEFAULT_CMAP = "viridis"        # 默认色图 ('viridis', 'inferno', 'plasma')
VMIN_PCT = 2                    # 密度百分位下限（用于裁剪色彩范围）
VMAX_PCT = 98                   # 密度百分位上限
POINT_ALPHA = 0.8               # 散点透明度
POINT_EDGE_WIDTH = 0.0          # 散点边框宽度（密集图中设为 0 减少视觉噪声）
POINT_EDGE_COLOR = "none"       # 散点边框颜色
COLORBAR_FRACTION = 0.046       # colorbar 宽度比例
COLORBAR_PAD = 0.04             # colorbar 与 axes 间距
KDE_SAMPLES_GRID = 200          # histogram2d 回退方案的网格分辨率


# ============ Density estimation ============

def _estimate_density_kde(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """使用 scipy.stats.gaussian_kde 估算每个点的密度值。"""
    from scipy.stats import gaussian_kde
    xy = np.vstack([x, y])
    kde = gaussian_kde(xy)
    return kde(xy)


def _estimate_density_hist2d(x: np.ndarray, y: np.ndarray,
                              grid_size: int = KDE_SAMPLES_GRID) -> np.ndarray:
    """回退方案：使用 numpy histogram2d + 最近邻查找估算密度。"""
    # 二维直方图
    hist, xedges, yedges = np.histogram2d(
        x, y, bins=grid_size, density=True
    )
    # 找到每个点所属的 bin
    x_bin = np.clip(np.searchsorted(xedges, x, side="right") - 1, 0, hist.shape[0] - 1)
    y_bin = np.clip(np.searchsorted(yedges, y, side="right") - 1, 0, hist.shape[1] - 1)
    return hist[x_bin, y_bin]


def estimate_density(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """估算二维点云的密度。优先使用 scipy KDE，不可用时回退到 histogram2d。

    Parameters
    ----------
    x, y : np.ndarray, shape (n,)

    Returns
    -------
    density : np.ndarray, shape (n,), 每个点的密度估计值
    """
    try:
        return _estimate_density_kde(x, y)
    except ImportError:
        pass
    except Exception:
        pass
    # 回退
    return _estimate_density_hist2d(x, y)


# ============ Mock data ============

def generate_mock_data(n: int = 5000, n_clusters: int = 4,
                       seed: int = 42) -> pd.DataFrame:
    """生成 UMAP 风格的演示数据。

    Parameters
    ----------
    n : int
        总点数 (默认 5000)
    n_clusters : int
        高斯聚类数量 (3-5)
    seed : int
        随机种子

    Returns
    -------
    DataFrame with columns ['x', 'y']
    """
    rng = np.random.default_rng(seed)

    # 随机聚类中心，在 [-10, 10] 范围内
    centers = rng.uniform(-8, 8, size=(n_clusters, 2))

    # 每个聚类的协方差（略有不同大小和形状）
    all_points = []
    counts = rng.multinomial(n, np.ones(n_clusters) / n_clusters)

    for i in range(n_clusters):
        ni = counts[i]
        # 各向异性扩散
        spread = rng.uniform(0.8, 2.0, 2)
        angle = rng.uniform(0, np.pi)
        rot = np.array([[np.cos(angle), -np.sin(angle)],
                        [np.sin(angle),  np.cos(angle)]])
        cov = rot @ np.diag(spread ** 2) @ rot.T
        pts = rng.multivariate_normal(centers[i], cov, ni)
        all_points.append(pts)

    points = np.vstack(all_points)

    # 添加少量均匀噪声离群点
    n_outliers = max(10, int(n * 0.02))
    outliers = rng.uniform(-12, 12, size=(n_outliers, 2))
    points = np.vstack([points, outliers])

    # 随机打散（模拟真实 UMAP 输出）
    rng.shuffle(points)

    return pd.DataFrame({"x": points[:, 0], "y": points[:, 1]})


# ============ Plotting ============

def plot(df: pd.DataFrame,
         x_col: str = "x",
         y_col: str = "y",
         cmap: str = DEFAULT_CMAP,
         vmin_pct: float = VMIN_PCT,
         vmax_pct: float = VMAX_PCT,
         point_size: Union[str, float, int] = "adaptive",
         xlabel: str = "UMAP 1",
         ylabel: str = "UMAP 2",
         title: Optional[str] = None,
         figsize: Optional[Tuple[float, float]] = None,
         save_path: Optional[str] = None,
         ax: Optional[Axes] = None,
         preset: str = "publication") -> Axes:
    """绘制密度着色散点图（UMAP 风格）。

    每个点根据其在 2D 空间中的局部密度着色，密度高的区域颜色更深/更暖。
    适合大数据集（数千至数万点），rasterized 渲染保持 PDF/SVG 体积可控。

    Parameters
    ----------
    df : DataFrame
        必须包含 x_col 和 y_col 指定的数值列。
    x_col, y_col : str
        列名。
    cmap : str
        matplotlib 色图名称。
    vmin_pct, vmax_pct : float
        密度色彩范围的百分位裁剪（默认 2nd / 98th）。
    point_size : str or number
        'adaptive' 时使用 s = max(100/sqrt(n), 1)；否则使用给定数值。
    xlabel, ylabel : str
        坐标轴标签。
    title : str or None
        图标题。
    figsize : tuple or None
        图片尺寸。
    save_path : str or None
        保存路径（可选）。
    ax : matplotlib Axes or None
        复用已有 axes。
    preset : str
        风格预设 ('publication', 'presentation', 'poster', 'draft', 'gallery').

    Returns
    -------
    matplotlib Axes
    """
    load_sci_style(preset)

    x = df[x_col].values.astype(float)
    y = df[y_col].values.astype(float)
    n = len(x)

    # --- 1. 估算密度 ---
    density = estimate_density(x, y)

    # --- 2. 按密度排序（低密度先画，高密度在上层） ---
    order = np.argsort(density)
    x_sorted = x[order]
    y_sorted = y[order]
    density_sorted = density[order]

    # --- 3. 百分位裁剪色彩范围 ---
    vmin = np.percentile(density_sorted, vmin_pct)
    vmax = np.percentile(density_sorted, vmax_pct)

    # --- 4. 自适应点大小 ---
    if point_size == "adaptive":
        s = max(100.0 / np.sqrt(n), 1.0)
    else:
        s = float(point_size)

    # --- 5. 绘图 ---
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (8, 7))
    else:
        fig = ax.figure

    sc = ax.scatter(
        x_sorted, y_sorted,
        c=density_sorted,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        s=s,
        alpha=POINT_ALPHA,
        edgecolors=POINT_EDGE_COLOR,
        linewidths=POINT_EDGE_WIDTH,
        rasterized=True,
        zorder=2,
    )

    # --- 6. 色条 ---
    cbar = fig.colorbar(sc, ax=ax, fraction=COLORBAR_FRACTION, pad=COLORBAR_PAD)
    cbar.set_label("Point density", fontsize=10)
    cbar.outline.set_linewidth(0.5)

    # --- 7. 坐标轴标签和标题 ---
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold")

    # 去掉上、右边框
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 等比例坐标轴（UMAP 通常等比例显示）
    ax.set_aspect("equal", adjustable="datalim")

    apply_gallery_polish(ax)

    if save_path:
        save_fig(fig, Path(save_path).stem, transparent=False)
        print(f"Saved to {save_path}")

    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    load_sci_style("gallery")
    df = generate_mock_data(n=5000, n_clusters=4, seed=42)
    ax = plot(df, preset="gallery", title="Density Scatter — 5 000 points")
    name = Path(__file__).stem
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
