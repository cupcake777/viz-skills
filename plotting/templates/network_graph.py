"""
基因网络图 (Network Interaction Graph)
======================================
展示基因/蛋白间调控或互作关系，节点大小反映连接度，边粗细反映互作强度。

适用数据类型: network / gene_interaction
必需列 (nodes): node_id, [degree]
必需列 (edges): source, target, weight
可选列: node_type, edge_type

参考: Cytoscape, STRING network
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from pathlib import Path

from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS

# ============ 参数配置 ============
GENE_NAMES = [
    "SOX2", "PAX6", "OTX2", "EMX1", "FGF8", "WNT1", "SHH", "BMP4",
    "HES1", "NOTCH1", "DLL1", "PAX3", "EN1", "WNT3A", "LHX2"
]


def generate_mock_data(n_nodes=15, n_edges=30, seed=42):
    """生成演示数据: 基因调控网络节点与边"""
    rng = np.random.default_rng(seed)

    # 节点
    genes = GENE_NAMES[:n_nodes]
    nodes = pd.DataFrame({
        "node_id": genes,
        "node_type": [rng.choice(["TF", "Signaling", "Marker"]) for _ in genes]
    })

    # 边: 随机选择节点对并赋权重
    edges_set = set()
    sources, targets, weights = [], [], []
    attempts = 0
    while len(sources) < n_edges and attempts < 500:
        s, t = rng.choice(genes, size=2, replace=False)
        pair = tuple(sorted([s, t]))
        if pair not in edges_set:
            edges_set.add(pair)
            sources.append(pair[0])
            targets.append(pair[1])
            weights.append(rng.uniform(0.2, 1.0))
        attempts += 1

    edges = pd.DataFrame({"source": sources, "target": targets, "weight": weights})
    return nodes, edges


def _spring_layout(nodes_df, edges_df, seed=42, iterations=80):
    """简单弹簧力导向布局 (无需 networkx)"""
    rng = np.random.default_rng(seed)
    ids = nodes_df["node_id"].tolist()
    n = len(ids)
    pos = {nid: rng.uniform(-1, 1, 2) for nid in ids}

    edge_list = list(zip(edges_df["source"], edges_df["target"], edges_df["weight"]))

    k = 1.0 / np.sqrt(n)
    for _ in range(iterations):
        disp = {nid: np.zeros(2) for nid in ids}
        for i in range(n):
            for j in range(i + 1, n):
                diff = pos[ids[i]] - pos[ids[j]]
                dist = max(np.linalg.norm(diff), 0.01)
                force = (k * k / dist) * (diff / dist)
                disp[ids[i]] += force
                disp[ids[j]] -= force
        for s, t, w in edge_list:
            if s in pos and t in pos:
                diff = pos[t] - pos[s]
                dist = max(np.linalg.norm(diff), 0.01)
                force = (dist * dist / k) * w * (diff / dist)
                disp[s] += force
                disp[t] -= force
        temp = max(0.1, 1.0 - _ / iterations)
        for nid in ids:
            d = disp[nid]
            d_norm = np.linalg.norm(d)
            if d_norm > 0:
                d = d / d_norm * min(d_norm, temp)
            pos[nid] += d
            pos[nid] = np.clip(pos[nid], -3, 3)

    return pos


def plot(nodes_df, edges_df, node_col="node_id", weight_col="weight",
         node_size_range=(200, 1200), edge_width_range=(0.3, 3.0),
         cmap_edges="Blues", figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制基因互作网络图

    Parameters
    ----------
    nodes_df : DataFrame, 节点信息 (node_id, ...)
    edges_df : DataFrame, 边信息 (source, target, weight)
    node_col : str, 节点ID列名
    weight_col : str, 权重列名
    node_size_range : tuple, 节点大小范围
    edge_width_range : tuple, 边宽度范围
    cmap_edges : str, 边配色
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    # 尝试使用 networkx
    try:
        import networkx as nx
        G = nx.Graph()
        for _, row in nodes_df.iterrows():
            G.add_node(row[node_col])
        for _, row in edges_df.iterrows():
            G.add_edge(row["source"], row["target"], weight=row[weight_col])
        pos = nx.spring_layout(G, seed=42, k=2.0 / np.sqrt(len(G)))
        degrees = dict(G.degree())
        node_list = list(G.nodes())
    except ImportError:
        pos = _spring_layout(nodes_df, edges_df)
        degrees = {}
        for _, row in edges_df.iterrows():
            degrees[row["source"]] = degrees.get(row["source"], 0) + 1
            degrees[row["target"]] = degrees.get(row["target"], 0) + 1
        for nid in nodes_df[node_col]:
            if nid not in degrees:
                degrees[nid] = 0
        node_list = nodes_df[node_col].tolist()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (8, 7))

    # 节点大小 (按度缩放)
    deg_vals = np.array([degrees.get(n, 0) for n in node_list], dtype=float)
    if deg_vals.max() > deg_vals.min():
        sizes = node_size_range[0] + (deg_vals - deg_vals.min()) / (deg_vals.max() - deg_vals.min()) * (node_size_range[1] - node_size_range[0])
    else:
        sizes = np.full_like(deg_vals, np.mean(node_size_range))

    # 边 (按权重着色和缩放)
    weights = edges_df[weight_col].values
    w_norm = (weights - weights.min()) / max(weights.max() - weights.min(), 1e-10)
    edge_widths = edge_width_range[0] + w_norm * (edge_width_range[1] - edge_width_range[0])
    cmap = plt.get_cmap(cmap_edges)
    edge_colors = [cmap(0.2 + 0.7 * w) for w in w_norm]

    # 绘制边
    for idx, (_, row) in enumerate(edges_df.iterrows()):
        s, t = row["source"], row["target"]
        if s in pos and t in pos:
            x0, y0 = pos[s]
            x1, y1 = pos[t]
            ax.plot([x0, x1], [y0, y1], color=edge_colors[idx],
                    linewidth=edge_widths[idx], alpha=0.6, zorder=1)

    # 绘制节点
    node_colors = []
    for n in node_list:
        node_colors.append(NATURE_COLORS[hash(n) % len(NATURE_COLORS)])

    xs = [pos[n][0] for n in node_list]
    ys = [pos[n][1] for n in node_list]
    ax.scatter(xs, ys, s=sizes, c=node_colors, edgecolors="black",
               linewidths=0.8, zorder=2)

    # 节点标签
    for nid in node_list:
        x, y = pos[nid]
        ax.text(x, y, nid, ha="center", va="center",
                fontweight="bold", zorder=3)

    ax.set_title("Gene Regulatory Network")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
    return ax


if __name__ == "__main__":
    nodes, edges = generate_mock_data()
    plot(nodes, edges, save_path="network_graph_demo.png")
    plt.close()
