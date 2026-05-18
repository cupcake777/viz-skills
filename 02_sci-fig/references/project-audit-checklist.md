# Project Code Audit Checklist (14 items)

⚠️ **仅替换hex色值≠完成！** 必须全查以下14项。

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | 语义配色 | 用up/down语义映射，非硬编码hex |
| 2 | 散点图例 | scatter必须有图例 |
| 3 | 富集尺寸图例 | Line2D proxy, 非scatter([],[])假点 |
| 4 | PDF+PNG双格式 | save_fig必须同时输出 |
| 5 | Arial字体 | 非DejaVu Sans |
| 6 | #FAFAFA背景 | 非纯白 |
| 7 | labelweight=bold | 轴标签加粗 |
| 8 | alpha密度 | scatter alpha≤0.5(>50点), ≤0.3(>500点) |
| 9 | matplotlibrc加载 | 用repo的matplotlibrc，非inline plt.rcParams.update |
| 10 | text_color_on_bg | 从base_plot import，非手动阈值 |
| 11 | adjustText防重叠 | 非ax.text()静态放置，需HAS_ADJUST_TEXT fallback |
| 12 | 无panel letter | set_title不含A/B/C/D前缀 |
| 13 | DPI=300 | 非自定义值(320/180等) |
| 14 | 无硬编码hack | pad=42等hardcoded布局需移除 |
