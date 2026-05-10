"""
Kaplan-Meier 生存曲线 (KM Survival Curve)
==========================================
展示不同基因表达分组的生存概率随时间变化，含95%置信区间和风险表。

适用数据类型: survival / time_to_event
必需列: time, event, group
可选列: risk_score

参考: lifelines.KaplanMeierFitter, survminer
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "style"))
from color_palettes import get_palette
from base_plot import load_sci_style, save_fig, auto_label, NATURE_COLORS, polish_legend, apply_gallery_polish

# ============ 参数配置 ============
GROUPS = ["Low_expr", "Medium_expr", "High_expr"]


def generate_mock_data(n_per_group=60, seed=42):
    """生成演示数据: 3组不同表达水平的生存数据"""
    rng = np.random.default_rng(seed)

    # 指数生存模型参数 (rate越大=风险越高=生存越差)
    rates = {"Low_expr": 0.008, "Medium_expr": 0.02, "High_expr": 0.05}
    censor_time = 60  # 最大随访月数

    dfs = []
    for grp in GROUPS:
        # 生存时间 (指数分布)
        times = rng.exponential(1.0 / rates[grp], n_per_group)
        # 删失: 约20%随机删失
        censored = rng.random(n_per_group) < 0.2
        censor_times = rng.uniform(10, censor_time, n_per_group)
        observed_times = np.where(censored, np.minimum(times, censor_times), times)
        observed_times = np.clip(observed_times, 0.1, censor_time)
        # event: 1=死亡, 0=删失
        events = np.where(censored, 0, 1)
        # 超过最大随访的也标为删失
        events = np.where(observed_times >= censor_time, 0, events)
        observed_times = np.minimum(observed_times, censor_time)

        dfs.append(pd.DataFrame({
            "time": observed_times, "event": events, "group": grp
        }))

    return pd.concat(dfs, ignore_index=True)


def _kaplan_meier(times, events):
    """手动计算KM估计 (无需lifelines)"""
    times = np.asarray(times, dtype=float)
    events = np.asarray(events, dtype=int)

    unique_times = np.sort(np.unique(times[events == 1]))
    if len(unique_times) == 0:
        return np.array([0]), np.array([1.0]), np.array([1.0]), np.array([1.0])

    n = len(times)
    survival = [1.0]
    ci_lower = [1.0]
    ci_upper = [1.0]
    t_points = [0]
    cum_var = 0.0
    s = 1.0

    for t in unique_times:
        at_risk = np.sum(times >= t)
        died = np.sum((times == t) & (events == 1))
        if at_risk == 0:
            continue
        # Greenwood variance
        if at_risk > died:
            cum_var += died / (at_risk * (at_risk - died)) if at_risk > 1 else 0
        s *= (1 - died / at_risk)
        se = s * np.sqrt(cum_var) if cum_var > 0 else 0
        survival.append(s)
        ci_lower.append(max(0, s - 1.96 * se))
        ci_upper.append(min(1, s + 1.96 * se))
        t_points.append(t)

    return np.array(t_points), np.array(survival), np.array(ci_lower), np.array(ci_upper)


def _logrank_test(times1, events1, times2, events2):
    """简化的log-rank检验"""
    all_times = np.sort(np.unique(np.concatenate([times1[events1 == 1], times2[events2 == 1]])))
    if len(all_times) == 0:
        return 1.0

    observed_diff = 0
    expected_var = 0
    for t in all_times:
        n1 = np.sum(times1 >= t)
        n2 = np.sum(times2 >= t)
        d1 = np.sum((times1 == t) & (events1 == 1))
        d2 = np.sum((times2 == t) & (events2 == 1))
        n = n1 + n2
        d = d1 + d2
        if n > 1 and n > 0:
            e1 = d * n1 / n
            observed_diff += (d1 - e1)
            if n ** 2 * (n - 1) > 0:
                expected_var += d * n1 * n2 * (n - d) / (n ** 2 * (n - 1))

    if expected_var > 0:
        chi2 = observed_diff ** 2 / expected_var
        from scipy.stats import chi2 as chi2_dist
        p = 1 - chi2_dist.cdf(chi2, 1)
    else:
        p = 1.0
    return p


def plot(df, time_col="time", event_col="event", group_col="group",
         colors=None, show_ci=True, show_risk_table=True,
         figsize=None, save_path=None, ax=None,
         preset="publication"):
    """
    绘制Kaplan-Meier生存曲线

    Parameters
    ----------
    df : DataFrame, 必须包含 time, event, group 列
    time_col : str, 随访时间列名
    event_col : str, 事件指示列名 (1=事件, 0=删失)
    group_col : str, 分组列名
    colors : list, 各组颜色
    show_ci : bool, 是否显示95%置信区间
    show_risk_table : bool, 是否显示风险表
    figsize : tuple, 图片尺寸
    save_path : str, 保存路径
    ax : matplotlib Axes, 可选
    """
    load_sci_style(preset)

    if colors is None:
        colors = NATURE_COLORS

    groups = df[group_col].unique().tolist()

    # 尝试使用lifelines
    use_lifelines = False
    kmf_objects = {}
    try:
        from lifelines import KaplanMeierFitter
        use_lifelines = True
    except ImportError:
        pass

    # 计算KM (用于p值)
    km_data = {}
    for grp in groups:
        sub = df[df[group_col] == grp]
        t = sub[time_col].values
        e = sub[event_col].values
        km_data[grp] = (t, e)

    # 绘图布局 (主图 + 风险表)
    if show_risk_table:
        if ax is None:
            fig, (ax, ax_table) = plt.subplots(2, 1, figsize=figsize or (8, 7),
                                                gridspec_kw={"height_ratios": [4, 1], "hspace": 0.08})
        else:
            ax_table = None  # 外部传入ax时无法创建risk table
            show_risk_table = False
    else:
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize or (8, 5))
        ax_table = None

    risk_info = {}
    for i, grp in enumerate(groups):
        t, e = km_data[grp]
        color = colors[i % len(colors)]

        if use_lifelines:
            kmf = KaplanMeierFitter()
            kmf.fit(t, event_observed=e, label=grp)
            kmf.plot_survival_function(ax=ax, color=color, ci_show=show_ci, ci_alpha=0.15)
            kmf_objects[grp] = kmf
            if show_risk_table:
                time_points = np.linspace(0, t.max(), 6).astype(int)
                at_risk = []
                for tp in time_points:
                    at_risk.append(int(np.sum(t >= tp)))
                risk_info[grp] = (time_points, at_risk)
        else:
            t_km, s_km, ci_lo, ci_hi = _kaplan_meier(t, e)
            ax.step(t_km, s_km, where="post", color=color, linewidth=1.5, label=grp)
            if show_ci:
                ax.fill_between(t_km, ci_lo, ci_hi, step="post",
                                alpha=0.15, color=color, linewidth=0)
            if show_risk_table:
                time_points = np.linspace(0, t.max(), 6).astype(int)
                at_risk = []
                for tp in time_points:
                    at_risk.append(int(np.sum(t >= tp)))
                risk_info[grp] = (time_points, at_risk)

    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Survival Probability")
    ax.set_title("Kaplan-Meier Survival Curves by Gene Expression Level")
    ax.legend(title="Group", frameon=True, loc="lower left")
    ax.set_xlim(0, None)

    apply_gallery_polish(ax)
    polish_legend(ax, loc="lower left")

    # 删失标记
    for i, grp in enumerate(groups):
        t, e = km_data[grp]
        color = colors[i % len(colors)]
        censored = t[e == 0]
        if len(censored) > 0:
            for ct in censored:
                t_km, s_km, _, _ = _kaplan_meier(t, e)
                idx = np.searchsorted(t_km, ct, side="right") - 1
                idx = max(0, min(idx, len(s_km) - 1))
                ax.plot(ct, s_km[idx], "|", color=color, markersize=6, alpha=0.5)

    # p值标注
    if len(groups) >= 2:
        ref = groups[0]
        p_texts = []
        for grp in groups[1:]:
            p = _logrank_test(km_data[ref][0], km_data[ref][1],
                              km_data[grp][0], km_data[grp][1])
            if p < 0.001:
                p_texts.append(f"{ref} vs {grp}: p<0.001")
            else:
                p_texts.append(f"{ref} vs {grp}: p={p:.3f}")
        p_text = "\n".join(p_texts)
        ax.text(0.98, 0.98, p_text, transform=ax.transAxes,
                va="top", ha="right",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

    # 风险表
    if show_risk_table and ax_table is not None:
        ax_table.set_xlim(ax.get_xlim())
        ax_table.set_ylim(-0.5, len(groups) - 0.5)
        ax_table.set_yticks(range(len(groups)))
        ax_table.set_yticklabels(groups)
        ax_table.set_xlabel("Time (months)")
        ax_table.invert_yaxis()

        for i, grp in enumerate(groups):
            tps, ar = risk_info[grp]
            color = colors[i % len(colors)]
            for tp, n_at_risk in zip(tps, ar):
                ax_table.text(tp, i, str(n_at_risk), ha="center", va="center",
                              color=color)
            ax_table.axhline(i - 0.5, color="lightgrey", linewidth=0.5)

        ax_table.set_title("Number at Risk", loc="left")
        ax_table.tick_params(axis="x", which="both", labelbottom=True)
        for spine in ["top", "right"]:
            ax_table.spines[spine].set_visible(False)
        ax.set_xticklabels([])

    if save_path:
        save_fig(ax.figure, Path(save_path).stem.replace("_demo", ""),
                 transparent=False)
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
