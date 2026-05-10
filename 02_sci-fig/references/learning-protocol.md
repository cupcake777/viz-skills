## 学习协议

当用户发来一张觉得好的图（来自paper、网站或自己的作品）：

### L1: 拆解

分析并提取8个维度：

1. **图表类型** — 火山图?热图?ridge?dot plot?
2. **布局** — 单面板/多面板? 排列方式? 宽高比?
3. **配色** — 提取hex色值，或匹配已知palette
4. **字体** — serif/sans-serif, 大小层级, bold/italic用法
5. **轴处理** — log/sqrt刻度? 刻度标签格式? 有无grid
6. **标注** — 统计标记, 基因标签, 阈值线, 图例位置
7. **数据编码通道** — position, color, size, shape 各编码了什么
8. **好在哪里** — 1-2句话总结，为什么这张图比平均水准好

### L2: 分类

| 情况 | 操作 |
|------|------|
| 全新图表类型（模板库没有） | 创建新模板脚本 + 新recipe文档 |
| 已有类型的风格变体 | 在现有模板上加 variation 参数 + recipe文档加 Variants 段 |
| 基础recipe的普适改进 | 直接patch基础模板和recipe，加版本说明 |

### L3: 生成代码 + 渲染验证

**不是只写markdown完事。必须产出可执行代码并渲染出图让用户确认。**

1. 写出可执行模板，静态科研图优先使用 R，放到 `../03_plotting-library/templates/`
2. **执行代码，用mock数据渲染出PNG**（例如 `Rscript ../03_plotting-library/templates/xxx.R` 生成 `demo_fig/*_demo.png`）
3. 发图给用户看（Telegram发送图片或Gallery链接）
4. 用户确认后才保存：
   - 脚本存 `templates/`, mock数据存 `demo_data/`
   - 更新 `catalog.yaml`
   - recipe存 `references/`
   - 重建Gallery或更新Brain API挂载的demo图
5. 用户说修改 → 按反馈改 → 重新渲染 → 再审

**⚠️ 只存markdown recipe不入库。入库=可执行脚本+用户确认过的图。**

### L4: 保存

经用户确认后才保存：

**可执行层** (`../03_plotting-library/`):
```
templates/new_chart.R       ← 可执行脚本，含 generate_mock_data() + plot()
demo_data/new_chart_demo.tsv ← mock数据，可选
demo_fig/new_chart_demo.png  ← 渲染预览
demo_fig/new_chart_demo.pdf  ← 矢量输出
catalog.yaml                 ← 更新数据类型→模板映射
```

**知识层** (`skill references/`):
```
references/new_chart.md     ← recipe文档（When/Learn/Code/Params/Pitfalls/Variants）
```

### L5: 应用

后续绘图时，检查优先级：
1. 当前项目是否已指定palette？用那个
2. 用户是否为该图表类型发过示例图？优先用那个变体
3. 跟数据/分析场景匹配的变体？用那个
4. 都没有 → 用基础recipe + `templates/base_plot.R` 默认风格

---
