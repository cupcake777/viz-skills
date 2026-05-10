"""
相关性热图 (Correlation Heatmap)
================================
展示变量间的Pearson相关性，支持层次聚类排序与上三角遮罩。

适用数据类型: correlation / expression_matrix
必需列: 多个数值型变量列
可选列: group (分组标签)

参考: seaborn.clustermap, Nature Methods
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS

# ============ 参数配置 ============


def generate_mock_data(n=200, seed=42):
    """生成演示数据: 8个基因表达量，具有生物学相关性"""
    rng = np.random.default_rng(seed)

    # 基础因子 (模拟共同调控模块)
    factor1 = rng.normal(0, 1, n)
    factor2 = rng.normal(0, 1, n)
    factor3 = rng.normal(0, 1, n)

    # 基因表达量: 同一通路内的基因有正相关
    sox2 = factor1 * 0.8 + factor2 * 0.2 + rng.normal(0, 0.3, n)
    pax6 = factor1 * 0.7 - factor2 * 0.1 + rng.normal(0, 0.3, n)
    otx2 = factor1 * 0.6 + factor3 * 0.3 + rng.normal(0, 0.4, n)
    emx1 = factor1 * 0.5 + factor3 * 0.2 + rng.normal(0, 0.4, n)
    fgf8 = factor2 * 0.9 + factor3 * 0.1 + rng.normal(0, 0.3, n)
    wnt1 = factor2 * 0.6 + factor3 * 0.4 + rng.normal(0, 0.3, n)
    shh = -factor1 * 0.4 + factor3 * 0.7 + rng.normal(0, 0.3, n)
    bmp4 = factor2 * 0.3 - factor3 * 0.5 + rng.normal(0, 0.4, n)

    df = pd.DataFrame({
        "SOX2": sox2, "PAX6": pax6, "OTX2": otx2, "EMX1": emx1,
        "FGF8": fgf8, "WNT1": wnt1, "SHH": shh, "BMP4": bmp4
    })
    return df


def plot(df, mask_upper=True, cluster=True, method="ward",
         cmap="coolwarm", annot=True, figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制相关性热图

    Parameters
    ----------
    df : DataFrame, 包含多个数值列用于计算相关性
    mask_upper : bool, 是否遮罩上三角（避免重复显示）
    cluster : bool, 是否使用层次聚类重排行列顺序
    method : str, 聚类方法 (ward, complete, average, single)
    cmap : str, 配色方案
    annot : bool, 是否在格子中显示数值
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    num_df = df.select_dtypes(include=[np.number])
    corr = num_df.corr(method="pearson")

    # 层次聚类排序
    if cluster and corr.shape[0] > 2:
        dist = 1 - np.abs(corr.values)
        np.fill_diagonal(dist, 0)
        dist = np.clip(dist, 0, None)
        dist_condensed = squareform(dist, checks=False)
        link = linkage(dist_condensed, method=method)
        order = leaves_list(link)
        corr = corr.iloc[order, order]

    # 遮罩上三角
    mask = None
    if mask_upper:
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (8, 7))

    # 绘制热图
    data = corr.values.copy()
    if mask is not None:
        data_masked = np.ma.masked_where(mask, data)
    else:
        data_masked = data

    vmin, vmax = -1, 1
    im = ax.imshow(data_masked, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")

    # 色标
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Pearson r")

    # 标注数值
    if annot:
        labels = corr.columns.tolist()
        for i in range(len(labels)):
            for j in range(len(labels)):
                if mask is not None and mask[i, j]:
                    continue
                val = data[i, j]
                color = "white" if abs(val) > 0.6 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color=color)

    # 轴标签
    labels = corr.columns.tolist()
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    ax.set_title("Gene Expression Correlation Heatmap", pad=12)

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    df = generate_mock_data()
    plot(df, save_path="correlation_heatmap_demo.png")
    plt.close()
