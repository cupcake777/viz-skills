# Plotting Library 📊

个人科研绘图方法库：数据类型 → 视觉编码 → 可复用代码模板

## 设计原则

1. **数据驱动**：先定义数据schema，再选图表类型
2. **可复制粘贴**：每个模板独立运行，含mock data，不依赖外部服务
3. **风格统一**：全局 `style/matplotlibrc` 控制字体、配色、尺寸
4. **按需扩展**：新增图表只需加模板文件+更新catalog.yaml

## 快速使用

```python
# 1. 查找适合你数据的图表
# 编辑 catalog.yaml 或搜索关键词

# 2. 复制模板
cp templates/volcano.py my_plot.py

# 3. 替换数据路径
# 修改脚本中的 data_path 指向你的数据

# 4. 运行
python my_plot.py
```

## 目录结构

```
plotting-library/
├── README.md                 # 本文件
├── catalog.yaml              # 数据类型→图表索引
├── style/
│   └── matplotlibrc          # 全局风格配置
├── templates/                # 绘图模板（每个独立可运行）
│   ├── volcano.py
│   ├── manhattan.py
│   ├── heatmap_clustered.py
│   ├── apa_pattern.py
│   └── ...
└── demo_data/                # mock数据文件
    ├── volcano_demo.tsv
    └── ...
```

## 图表索引

见 `catalog.yaml`，支持按以下维度检索：
- **data_type**: 差异表达、QTL、APA模式、富集分析...
- **visual_type**: 散点、柱状、热图、桑基、火山...
- **tags**: 自由标签，逗号分隔

## 模板规范

每个模板文件包含：
1. 模块docstring：描述、适用数据类型、参数说明
2. `generate_mock_data()`: 生成演示数据
3. `plot(df, **kwargs)`: 核心绘图函数
4. `__main__` 块：自包含运行示例

## 风格配置

修改 `style/matplotlibrc` 可统一所有图表的：
- 字体族与字号
- 配色方案
- 图表尺寸与DPI
- 边距与间距