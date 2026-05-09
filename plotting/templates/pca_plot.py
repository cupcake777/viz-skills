"""
PCA 散点图 (PCA Scatter Plot)
==============================
展示多组样本在主成分空间中的聚类与分离情况，含68%置信椭圆。

适用数据类型: dimensionality_reduction / expression_matrix
必需列: PC1, PC2, group
可选列: sample_id, batch

参考: DESeq2 plotPCA, Seurat DimPlot
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from pathlib import Path

from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS

# ============ 参数配置 ============
GROUPS = ["Control", "Treatment_A", "Treatment_B"]


def generate_mock_data(n_per_group=50, n_features=200, seed=42):
    """生成演示数据: 3组RNA-seq样本，模拟PCA降维结果"""
    rng = np.random.default_rng(seed)

    centers = {
        "Control": np.array([0, 0]),
        "Treatment_A": np.array([4, 2]),
        "Treatment_B": np.array([1, -3]),
    }
    covs = {
        "Control": np.array([[1.5, 0.3], [0.3, 1.0]]),
        "Treatment_A": np.array([[2.0, -0.5], [-0.5, 1.2]]),
        "Treatment_B": np.array([[1.0, 0.8], [0.8, 2.0]]),
    }

    groups, pc1, pc2 = [], [], []
    for grp in GROUPS:
        pts = rng.multivariate_normal(centers[grp], covs[grp], n_per_group)
        groups.extend([grp] * n_per_group)
        pc1.extend(pts[:, 0])
        pc2.extend(pts[:, 1])

    var_pc1 = 42.3
    var_pc2 = 18.7

    return pd.DataFrame({
        "group": groups, "PC1": pc1, "PC2": pc2,
        "sample_id": [f"S{i+1}" for i in range(len(groups))]
    }), var_pc1, var_pc2


def _confidence_ellipse(x, y, ax, n_std=1.0, **kwargs):
    """绘制置信椭圆 (n_std=1 对应 ~68%)"""
    if len(x) < 3:
        return
    cov = np.cov(x, y)
    mean = np.array([np.mean(x), np.mean(y)])
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = eigvals.argsort()[::-1]
    eigvals, eigvecs = eigvals[order], eigvecs[:, order]
    angle = np.degrees(np.arctan2(eigvecs[1, 0], eigvecs[0, 0]))
    width, height = 2 * n_std * np.sqrt(eigvals)
    ell = Ellipse(xy=mean, width=width, height=height, angle=angle, **kwargs)
    ax.add_patch(ell)


def plot(df, pc1_col="PC1", pc2_col="PC2", group_col="group",
         var_pc1=None, var_pc2=None, show_ellipse=True, n_std=1.0,
         point_size=40, alpha=0.7, colors=None, figsize=None,
         save_path=None, ax=None, preset="publication"):
    """
    绘制PCA散点图

    Parameters
    ----------
    df : DataFrame, 必须包含 PC1, PC2, group 列
    pc1_col, pc2_col : str, 主成分列名
    group_col : str, 分组列名
    var_pc1, var_pc2 : float, 方差解释率 (%)
    show_ellipse : bool, 是否绘制置信椭圆
    n_std : float, 椭圆标准差倍数 (1=68%, 2=95%)
    point_size : int, 散点大小
    alpha : float, 散点透明度
    colors : list, 各组颜色
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if colors is None:
        colors = NATURE_COLORS

    groups = df[group_col].unique().tolist()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    for i, grp in enumerate(groups):
        mask = df[group_col] == grp
        color = colors[i % len(colors)]
        ax.scatter(df.loc[mask, pc1_col], df.loc[mask, pc2_col],
                   c=color, s=point_size, alpha=alpha, label=grp,
                   edgecolors="white", linewidths=0.5)

        if show_ellipse:
            _confidence_ellipse(df.loc[mask, pc1_col].values,
                                df.loc[mask, pc2_col].values,
                                ax, n_std=n_std,
                                edgecolor=color, facecolor=color,
                                alpha=0.12, linewidth=1.5, linestyle="--")

    xlabel = "PC1"
    if var_pc1 is not None:
        xlabel += f" ({var_pc1:.1f}% variance)"
    ylabel = "PC2"
    if var_pc2 is not None:
        ylabel += f" ({var_pc2:.1f}% variance)"

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title("PCA of Gene Expression Profiles")
    ax.legend(title="Group", frameon=True)
    ax.axhline(0, color="grey", linewidth=0.3, linestyle="-")
    ax.axvline(0, color="grey", linewidth=0.3, linestyle="-")

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    df, v1, v2 = generate_mock_data()
    plot(df, var_pc1=v1, var_pc2=v2, save_path="pca_demo.png")
    plt.close()
