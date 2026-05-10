"""
聚类热图 (Clustered Heatmap)
=============================
行列双向聚类的热图，展示表达模式。

适用数据类型: expression_matrix
必需列: 宽格式矩阵（行=基因/特征，列=样本）
可选列: 行注释、列注释

参考: R2Omics, HiPlot, seaborn.clustermap
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS, polish_legend

# ============ 参数配置 ============
CMAP_DEFAULT = "RdBu_r"           # 红蓝渐变
CMAP_SEQUENTIAL = "YlOrRd"        # 顺序渐变
ROW_CLUSTER = True
COL_CLUSTER = True
Z_SCORE_AXIS = 0                   # 0=按行标准化, 1=按列, None=不标准化


def generate_mock_data(n_genes=50, n_samples=8, seed=42):
    """生成演示数据"""
    rng = np.random.default_rng(seed)
    # 生成3个基因集群
    block1 = rng.normal(2, 0.3, (n_genes // 3, n_samples))
    block2 = rng.normal(0, 0.3, (n_genes // 3, n_samples))
    block3 = rng.normal(-1, 0.3, (n_genes - 2 * (n_genes // 3), n_samples))
    data = np.vstack([block1, block2, block3])

    gene_names = [f"Gene_{i}" for i in range(data.shape[0])]
    sample_names = [f"Sample_{i}" for i in range(data.shape[1])]
    df = pd.DataFrame(data, index=gene_names, columns=sample_names)

    # 生成注释
    row_ann = pd.DataFrame({
        "Pattern": (["Cluster_A"] * (n_genes // 3) +
                    ["Cluster_B"] * (n_genes // 3) +
                    ["Cluster_C"] * (data.shape[0] - 2 * (n_genes // 3)))
    }, index=gene_names)
    col_ann = pd.DataFrame({
        "Stage": ["Prenatal"] * (n_samples // 2) + ["Postnatal"] * (n_samples // 2)
    }, index=sample_names)
    return df, row_ann, col_ann


def plot(df, row_ann=None, col_ann=None,
         row_cluster=ROW_CLUSTER, col_cluster=COL_CLUSTER,
         z_score=Z_SCORE_AXIS, cmap=CMAP_DEFAULT,
         figsize=None, save_path=None, preset="publication", **kwargs):
    """
    绘制聚类热图

    Parameters
    ----------
    df : DataFrame, 行=特征, 列=样本
    row_ann : DataFrame, 行注释（与df index对齐）
    col_ann : DataFrame, 列注释（与df columns对齐）
    row_cluster, col_cluster : bool, 是否聚类
    z_score : 0/1/None, 标准化方向
    cmap : str, 配色
    figsize : tuple
    save_path : str
    **kwargs : 传给sns.clustermap的参数
    """
    load_sci_style(preset)

    # 解决 seaborn clustermap 与 constrained_layout 的兼容性
    plt.rcParams['figure.constrained_layout.use'] = False

    # 注释配色 — from npg palette
    _npg = get_palette("npg")
    ann_colors = {
        "Cluster_A": _npg[0], "Cluster_B": _npg[1], "Cluster_C": _npg[2],
        "Cluster_D": _npg[3], "Cluster_E": _npg[4],
        "Prenatal": _npg[0], "Postnatal": _npg[1],
        "Male": _npg[3], "Female": _npg[4],
    }

    row_colors = None
    col_colors = None

    if row_ann is not None:
        # 取第一列作为颜色Series
        row_colors = row_ann.iloc[:, 0].map(lambda x: ann_colors.get(x, ".6"))
    if col_ann is not None:
        col_colors = col_ann.iloc[:, 0].map(lambda x: ann_colors.get(x, ".6"))

    g = sns.clustermap(
        df, row_cluster=row_cluster, col_cluster=col_cluster,
        z_score=z_score, cmap=cmap,
        row_colors=row_colors, col_colors=col_colors,
        figsize=figsize or (8, 10),
        dendrogram_ratio=0.1,
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        **kwargs
    )

    g.fig.suptitle("Clustered Heatmap", y=1.02)

    for a in g.fig.axes:
        polish_legend(a, loc="best")

    if save_path:
        save_fig(g.fig, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return g


if __name__ == "__main__":
    from base_plot import load_sci_style, save_fig
    sys.path.insert(0, str(Path(__file__).parent))
    load_sci_style("gallery")
    df, row_ann, col_ann = generate_mock_data()
    g = plot(df, row_ann=row_ann, col_ann=col_ann, preset="gallery")
    name = Path(__file__).stem.replace("_plot", "").replace("_curve", "").replace("_clustered", "")
    save_fig(g.fig, name, dpi=180, fmt="both")
    plt.close(g.fig)
