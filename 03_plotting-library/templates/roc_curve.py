"""
ROC曲线 (ROC Curve with AUC)
==============================
展示多个分类器的受试者工作特征曲线及曲线下面积。

适用数据类型: classification / model_evaluation
必需列: fpr, tpr (每条曲线的轨迹) 或 y_true, y_score (原始分数)
可选列: classifier, auc

参考: scikit-learn, pROC
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, NATURE_COLORS, polish_legend, apply_gallery_polish

# ============ 参数配置 ============

# Nature 配色

_npg = get_palette("npg")
CLASSIFIER_CONFIG = {
    "Logistic Regression": {"auc": 0.92, "color": _npg[0], "style": "-"},
    "Random Forest":       {"auc": 0.88, "color": _npg[1], "style": "-"},
    "SVM (RBF kernel)":    {"auc": 0.78, "color": _npg[2], "style": "-"},
}


def _simulate_roc_curve(target_auc, n_points=200, seed=42):
    """
    根据目标AUC生成合理的FPR/TPR轨迹。

    使用beta分布扰动对角线来模拟不同分类器的ROC形状。
    """
    rng = np.random.default_rng(seed)

    # 从0到1均匀采样FPR
    fpr = np.linspace(0, 1, n_points)

    # 用幂函数拟合: tpr = fpr^alpha, alpha < 1 则凸起
    # AUC ≈ 1/(alpha+1) => alpha = 1/AUC - 1
    # 但要让曲线合理, 使用混合方法
    alpha = max(0.05, 1.0 / target_auc - 1.0)
    tpr_base = 1 - (1 - fpr) ** (1.0 / max(alpha, 0.1))

    # 加入少量噪声使曲线更真实
    noise = rng.normal(0, 0.01, n_points)
    tpr = np.clip(tpr_base + noise, 0, 1)
    tpr[0] = 0.0
    tpr[-1] = 1.0

    # 确保单调递增
    tpr = np.maximum.accumulate(tpr)

    return fpr, tpr


def generate_mock_data(n_points=200, seed=42):
    """生成多个分类器的ROC曲线演示数据"""
    all_records = []
    seed_offset = 0
    for name, cfg in CLASSIFIER_CONFIG.items():
        fpr, tpr = _simulate_roc_curve(cfg["auc"], n_points, seed + seed_offset)
        for f, t in zip(fpr, tpr):
            all_records.append({
                "classifier": name,
                "fpr": f,
                "tpr": t,
                "auc": cfg["auc"],
            })
        seed_offset += 10

    return pd.DataFrame(all_records)


def plot(df, fpr_col="fpr", tpr_col="tpr", group_col="classifier",
         auc_col="auc", show_diagonal=True, show_chance_ci=False,
         figsize=None, save_path=None, ax=None, preset="publication"):
    """
    绘制ROC曲线

    Parameters
    ----------
    df : DataFrame, 包含 fpr, tpr, classifier 列
    fpr_col : str, 假阳性率列名
    tpr_col : str, 真阳性率列名
    group_col : str, 分类器名称列名
    auc_col : str, AUC值列名 (用于legend标注)
    show_diagonal : bool, 是否显示随机参考线
    show_chance_ci : bool, 是否显示随机分类器95%CI区域
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    classifiers = df[group_col].unique().tolist()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (7, 6))

    # 随机分类器参考线
    if show_diagonal:
        ax.plot([0, 1], [0, 1], color="#CCCCCC", linestyle="--",
                linewidth=1, label="Random (AUC=0.50)", zorder=1)
        if show_chance_ci:
            # Bootstrap CI for random classifier (roughly ±0.05 around diagonal)
            n_boot = 100
            rng = np.random.default_rng(42)
            tprs_boot = []
            fpr_base = np.linspace(0, 1, 200)
            for _ in range(n_boot):
                tpr_boot = fpr_base + rng.normal(0, 0.03, len(fpr_base))
                tpr_boot = np.clip(tpr_boot, 0, 1)
                tprs_boot.append(tpr_boot)
            tprs_boot = np.array(tprs_boot)
            tpr_lower = np.percentile(tprs_boot, 2.5, axis=0)
            tpr_upper = np.percentile(tprs_boot, 97.5, axis=0)
            ax.fill_between(fpr_base, tpr_lower, tpr_upper,
                            color="#CCCCCC", alpha=0.2, zorder=0)

    # 绘制每条ROC曲线
    for i, clf in enumerate(classifiers):
        mask = df[group_col] == clf
        clf_df = df.loc[mask].sort_values(fpr_col)
        color = CLASSIFIER_CONFIG.get(clf, {}).get("color",
                                                    NATURE_COLORS[i % len(NATURE_COLORS)])
        style = CLASSIFIER_CONFIG.get(clf, {}).get("style", "-")
        auc_val = clf_df[auc_col].iloc[0] if auc_col in clf_df.columns else None

        label = clf
        if auc_val is not None:
            label = f"{clf} (AUC={auc_val:.2f})"

        ax.plot(clf_df[fpr_col], clf_df[tpr_col],
                color=color, linestyle=style, linewidth=2,
                label=label, zorder=3)

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.set_title("ROC Curves — Classifier Comparison", fontsize=13)
    ax.legend(loc="lower right", frameon=True, fontsize=9,
              title="Classifier", title_fontsize=10)
    ax.set_aspect("equal")

    # 美化
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    apply_gallery_polish(ax)
    polish_legend(ax, loc="lower right")

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
