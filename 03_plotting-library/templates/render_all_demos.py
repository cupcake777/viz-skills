#!/usr/bin/env python3
"""批量重新渲染所有demo图（Gallery级别视觉提升v2）

改动要点：
- matplotlibrc v2: 浅灰plot area背景(#FAFAFA), legend圆角框, 轴标签加粗
- base_plot.py v2: 新增gallery preset, apply_gallery_polish(), polish_legend()
- 每个模板使用gallery preset渲染，并应用polish
"""
import sys
import os
import importlib

# 确保模板目录在path上
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTTING_DIR = os.path.dirname(TEMPLATE_DIR)
if TEMPLATE_DIR not in sys.path:
    sys.path.insert(0, TEMPLATE_DIR)

# 要渲染的模板列表（Python模板）
PYTHON_TEMPLATES = [
    "volcano",
    "raincloud", 
    "grouped_bar",
    "enrichment_bubble",
    "pca_plot",
    "km_survival",
    "roc_curve",
    "apa_pattern",
    "box_violin",
    "upset_plot",
    "sankey",
    "network_graph",
]

# 需要R的模板（跳过）
R_ONLY_TEMPLATES = [
    "manhattan", "heatmap_clustered", "correlation_heatmap",
    "forest_plot", "lollipop", "oncoplot", "ridgeline",
    "enrichment_circos", "umap_plot",
]

def render_template(name):
    """渲染单个Python模板的demo图"""
    print(f"\n{'='*60}")
    print(f"Rendering: {name}")
    print(f"{'='*60}")
    
    try:
        # 导入模块
        module = importlib.import_module(name)
        
        # 生成mock数据
        if hasattr(module, 'generate_mock_data'):
            df = module.generate_mock_data()
        else:
            print(f"  Skip: No generate_mock_data()")
            return False
        
        # 渲染（使用gallery preset）
        preset = "gallery"
        if hasattr(module, 'plot'):
            fig = module.plot(df, preset=preset)
            if fig is None:
                # plot可能不返回fig，检查当前figure
                import matplotlib.pyplot as plt
                fig = plt.gcf()
        else:
            print(f"  Skip: No plot()")
            return False
        
        # 应用gallery polish（如果plot内部没做）
        ax = fig.axes[0] if fig.axes else None
        if ax is not None:
            # 只对非热图类加grid
            from base_plot import apply_gallery_polish, polish_legend
            # 检查是否已有grid
            if not any(l.get_alpha() > 0 for l in ax.yaxis.get_gridlines()):
                apply_gallery_polish(ax)
            # 检查是否有legend
            if ax.get_legend() is not None:
                polish_legend(ax)
        
        # 保存
        from base_plot import save_fig
        save_fig(fig, name, dpi=180)
        
        import matplotlib.pyplot as plt
        plt.close('all')
        print(f"  ✓ Done: {name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error rendering {name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("Gallery Demo Re-render v2")
    print("=" * 60)
    
    results = {}
    for name in PYTHON_TEMPLATES:
        results[name] = render_template(name)
    
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    success = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"  Success: {success}/{len(results)}")
    print(f"  Failed:  {failed}/{len(results)}")
    
    for name, ok in results.items():
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")
    
    print(f"\n  R-only templates (need Rscript): {', '.join(R_ONLY_TEMPLATES)}")
    print(f"  These need manual Rscript rendering.")


if __name__ == "__main__":
    main()