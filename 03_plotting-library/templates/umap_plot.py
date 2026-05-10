"""
UMAP散点图 (UMAP 2D Scatter Plot)
==================================
展示单细胞RNA-seq数据经UMAP降维后的细胞类型聚类分布。

适用数据类型: dimensionality_reduction / single_cell
必需列: UMAP1, UMAP2, cell_type
可选列: sample_id, n_genes, cluster

参考: Seurat DimPlot, Scanpy pl.umap
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, NATURE_COLORS, polish_legend, apply_gallery_polish

# ============ 参数配置 ============

# Nature 配色

_npg = get_palette("npg")
CELL_TYPE_CONFIG = {
    "Neuron":          {"color": _npg[0], "center": (3, 4), "spread": (1.2, 1.0)},
    "Astrocyte":       {"color": _npg[1], "center": (-4, 2), "spread": (1.0, 1.3)},
    "Oligodendrocyte": {"color": _npg[2], "center": (0, -4), "spread": (1.4, 0.9)},
    "Microglia":       {"color": _npg[3], "center": (-3, -2), "spread": (0.9, 1.1)},
}


def generate_mock_data(n_per_type=80, seed=42):
    """生成单细胞UMAP降维演示数据"""
    rng = np.random.default_rng(seed)

    records = []
    for ctype, cfg in CELL_TYPE_CONFIG.items():
        center = np.array(cfg["center"])
        spread = np.array(cfg["spread"])
        # 多元正态分布生成聚类
        cov = np.diag(spread ** 2) * 0.6
        pts = rng.multivariate_normal(center, cov, n_per_type)
        # 添加少量噪声离群点
        n_outliers = max(1, int(n_per_type * 0.05))
        outlier_idx = rng.choice(n_per_type, n_outliers, replace=False)
        pts[outlier_idx] += rng.normal(0, 2.5, (n_outliers, 2))

        for p in pts:
            records.append({
                "UMAP1": p[0],
                "UMAP2": p[1],
                "cell_type": ctype,
                "n_genes": int(rng.integers(200, 6000)),
            })

    return pd.DataFrame(records)


def _draw_convex_hull(ax, points, color, alpha=0.10, linewidth=1.2):
    """绘制凸包边界"""
    if len(points) < 3:
        return
    try:
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        # 闭合多边形
        hull_points = np.vstack([hull_points, hull_points[0]])
        ax.fill(hull_points[:, 0], hull_points[:, 1],
                color=color, alpha=alpha, linewidth=0)
        ax.plot(hull_points[:, 0], hull_points[:, 1],
                color=color, alpha=0.4, linewidth=linewidth, linestyle="--")
    except Exception:
        pass  # 退化情况跳过


def plot(df, x_col="UMAP1", y_col="UMAP2", group_col="cell_type",
         show_hull=True, point_size=25, alpha=0.7, colors=None,
         figsize=None, save_path=None, ax=None, preset="publication"):
    """
    绘制UMAP散点图

    Parameters
    ----------
    df : DataFrame, 必须包含 UMAP1, UMAP2, cell_type 列
    x_col, y_col : str, UMAP维度列名
    group_col : str, 细胞类型列名
    show_hull : bool, 是否绘制聚类凸包边界
    point_size : int, 散点大小
    alpha : float, 透明度
    colors : dict, 细胞类型→颜色映射
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if colors is None:
        colors = {ct: cfg["color"] for ct, cfg in CELL_TYPE_CONFIG.items()}

    cell_types = df[group_col].unique().tolist()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (8, 7))

    for ct in cell_types:
        mask = df[group_col] == ct
        color = colors.get(ct, "#999999")
        pts = df.loc[mask, [x_col, y_col]].values

        ax.scatter(pts[:, 0], pts[:, 1], c=color, s=point_size,
                   alpha=alpha, label=ct, edgecolors="white",
                   linewidths=0.3, rasterized=True, zorder=2)

        if show_hull:
            _draw_convex_hull(ax, pts, color, alpha=0.08)

    ax.set_xlabel("UMAP1", fontsize=11)
    ax.set_ylabel("UMAP2", fontsize=11)
    ax.set_title("UMAP — Cell Type Clustering", fontsize=13)
    ax.legend(title="Cell Type", frameon=True, fontsize=9,
              title_fontsize=10, markerscale=1.5,
              loc="best", borderaxespad=0.5)

    # 移除顶部和右侧边框
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    apply_gallery_polish(ax)
    polish_legend(ax, loc="best")

    if save_path:
        save_fig(fig, Path(save_path).stem.replace("_demo", ""), transparent=False)
        print(f"Saved to {save_path}")
    return ax


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df = generate_mock_data()
    ax = plot(df, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(ax.figure, name, dpi=180, fmt="both")
    plt.close(ax.figure)
