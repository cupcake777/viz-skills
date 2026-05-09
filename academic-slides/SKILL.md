---
name: academic-slides
description: "学术PPT制作：组会报告与论文答辩。预设学术模板、数据图排版规范、中文学术惯例。触发词：PPT、slides、组会、答辩、报告、presentation、thesis defense。"
version: 1.1
tags: [pptx, presentation, academic, 组会, 答辩]
related_skills: [powerpoint, sci-fig, plotting-library]
canonical_source: https://github.com/cupcake777/viz-skills/tree/main/academic-slides
---

# 学术PPT制作 Skill

学术报告/答辩专用PPT制作规范。与通用`powerpoint` skill的区别：聚焦学术内容排版、数据图展示规范、中文学术场景惯例。

## 架构

```
academic-slides (skill)    ← 你现在读的：学术PPT规范+模板+排版指南
    │
    ├── powerpoint (skill) ← 底层PPT渲染引擎（pptxgenjs/python-pptx）
    │
    ├── sci-fig (skill)   ← 数据图生成规范（配色、字号、preset切换）
    │
    └── plotting-library   ← 可执行模板库（直接出图）
```

**关键原则：图用sci-fig规范生成（7pt publication版或16pt presentation版），PPT负责排版和叙事。**

---

## 场景分类

### 场景1：组会/进展报告 (Lab Meeting)

**特点：** 每周/双周一次，5-15分钟，重点展示进展和问题。

| 项目 | 规格 |
|------|------|
| 时长 | 5-15分钟 |
| 页数 | **10-12页**（背景部分10min=10-12页，不是18页） |
| 尺寸 | 16:9 (10"×5.63") |
| 字号 | 正文16pt，标题28-32pt |
| 风格 | 简洁数据导向，无装饰，信息密度高 |

⚠️ **页数控制铁律**：用户明确偏好10-12页而非18+页。信息密度要高：每页左1/3文字+右2/3图panel拼接。用户倾向于手动微调最终版而非让AI反复改。

**标准结构（10-12页准则）：**
1. **Title** — 标题 + 日期 + 姓名（1页）
2. **Background** — 概念对比/冲突/核心问题，高密度双卡片布局（1-2页）
3. **Research Question** — 两个理想标准/假说（1页）
4. **Findings** — 每1-2页一个核心发现，左文字+右panel拼接（3-5页）
5. **Summary & Implications** — 三卡片+编号要点（1页）

### 场景2：论文答辩 (Thesis Defense)

**特点：** 一次性，30-45分钟，需要完整叙事弧。

| 项目 | 规格 |
|------|------|
| 时长 | 30-45分钟 |
| 页数 | 25-40页 |
| 尺寸 | 16:9 |
| 字号 | 正文16pt，标题28-32pt |
| 风格 | 正式但不死板，storytelling |

**标准结构：**
1. **Title** — 论文题目 + 姓名 + 导师 + 日期机构（1页）
2. **Outline** — 左列目录，当前章节高亮（1页）
3. **Introduction** — 研究背景+意义（2-3页）
4. **Literature Review** — 文献综述+研究缺口（2-3页）
5. **Research Framework** — 研究框架/假说图（1页）
6. **Method** — 详细方法（2-3页）
7. **Results Chapter 1** — 核心发现1（4-6页）
8. **Results Chapter 2** — 核心发现2（4-6页）
9. **Discussion** — 总结+创新点+局限性（2-3页）
10. **Conclusion** — 结论+展望（1-2页）
11. **Acknowledgments** — 致谢（1页）
12. **Q&A** — 谢谢/提问页（1页）

---

## 学术配色方案

### Nature学术（默认）

| 元素 | 色值 | 用途 |
|------|------|------|
| Primary | `#1F2937` | 标题、正文 |
| Secondary | `#4B5563` | 副标题、说明 |
| Accent | `#E64B35` | 强调、关键数据 |
| Blue | `#3C5488` | 链接、辅助强调 |
| Green | `#00A087` | 正面结果 |
| Background | `#FFFFFF` | 白底 |
| Section break | `#1F2937` | 章节分隔页全色背景 |

### 深色学术（投影环境差时用）

| 元素 | 色值 | 用途 |
|------|------|------|
| Primary | `#F9FAFB` | 标题、正文 |
| Secondary | `#D1D5DB` | 副标题 |
| Accent | `#E64B35` | 强调 |
| Background | `#111827` | 深色底 |
| Card BG | `#1F2937` | 内容区背景 |

### apa_project（与sci-fig项目配色联动）

| 元素 | 色值 | 用途 |
|------|------|------|
| Fetal | `#4DBBD5` | 胎期 |
| Postnatal | `#E64B35` | 生后 |
| Switch | `#00A087` | 切换 |

---

## 排版规范

### ⚠️ Figure排版铁律（用户明确纠正，必须遵守）

1. **从主图截取panel再拼接，不要整张主图直接放** — 一张PPT放整张主图太仓促，读者看不清细节。用PIL/Pillow将主图切割为子panel（a/b/c/d），然后2-4个panel组合排版。
2. **严格保持长宽比，绝不拉伸变形** — 用`fitImage()`计算：`ratio = min(maxW/srcW, maxH/srcH)`，居中放置。pptxgenjs中没有自动fit，必须手动算。
3. **左1/3文字+右2/3图拼接** — 信息密度高，每页内容充实。
4. **每个panel标注子编号**（a/b/c/d）— 用9-10pt灰色斜体，放在panel左上角。

### 数据图在PPT中的规则

1. **图占2/3宽度留1/3给说明** — 左文字右图，不要整页一图
2. **图上方3mm留方法说明** — "PDUI difference (Fetal vs Adult,Wilcoxon test)"
3. **图下方放caption** — 8-10pt灰色标注来源/P值
4. **所有图用`transparent=True`背景** — 放到任意底色PPT上
5. **图分辨率≥200dpi** — sci-fig preset=presentation时自动满足
6. **同一报告配色一致** — 同一project用同一套PROJECT_COLORS

### 字体与字号

| 元素 | 字号 | 字重 | 字体 |
|------|------|------|------|
| 幻灯片标题 | 28-32pt | Bold | Arial / Calibri |
| 章节标题 | 24-28pt | Bold | Arial |
| 正文 | 16-18pt | Regular | Arial |
| 图注说明 | 10-12pt | Regular | 灰色 |
| 数据标注 | 14-16pt | Bold | 突出关键数字 |

### 间距

- 标题距顶部：0.5"
- 内容区距标题：0.3"
- 图与文字间距：0.2"
- 页边距：0.5-0.75"
- 段落行距：1.2-1.5倍

---

## Slide模板（pptxgenjs）

### TitleSlide
```
┌─────────────────────────────────────┐
│                                     │
│         [论文题目 32pt Bold]         │
│                                     │
│    [副标题/英文题目 18pt Regular]    │
│                                     │
│         [姓名 • 导师 • 日期]         │
│              [机构Logo]              │
└─────────────────────────────────────┘
```
- 背景：白色或Primary色全屏
- 副标题用Secondary色
- 底部放校徽/实验室logo

### SectionDivider
```
┌─────────────────────────────────────┐
│ ████                               │
│ ████  [章节标题 28pt Bold]         │
│ ████  [章节编号]                    │
│       [简短描述 16pt]               │
│                                     │
└─────────────────────────────────────┘
```
- 左侧Primary色色带(1/4宽)
- 大章节号+标题右对齐

### DataFigure（核心，最常用）
```
┌─────────────────────────────────────┐
│ [方法描述 16pt]          [P=0.003] │
│ ┌─────────────────────────────┐    │
│ │                             │    │
│ │      [数据图 transparent]   │    │
│ │                             │    │
│ └─────────────────────────────┘    │
│ [Caption/来源 10pt灰色]            │
└─────────────────────────────────────┘
```
- 图占70-80%宽度
- 右上/左上放方法描述和P值
- 下方caption用灰色小字

### TwoColumnResults
```
┌─────────────────────────────────────┐
│ [结果描述 20pt Bold]                │
│                                     │
│ ┌──────────┐    ┌──────────┐       │
│ │ [图A]    │    │ [图B]    │       │
│ │          │    │          │       │
│ └──────────┘    └──────────┘       │
│ [A关键发现]      [B关键发现]        │
└─────────────────────────────────────┘
```
- 两个图并列比较
- 每图下方1行关键发现（14pt Bold）

### MethodPipeline
```
┌─────────────────────────────────────┐
│ [方法流程]                           │
│                                     │
│  [Step1] ──→ [Step2] ──→ [Step3]   │
│  [样本]      [处理]      [分析]      │
│   n=50       QC≥0.8    DESeq2      │
│                                     │
│ [关键参数说明]                       │
└─────────────────────────────────────┘
```
- 水平流程，箭头连接
- 每步方框+下方参数

### Timeline（答辩用）
```
┌─────────────────────────────────────┐
│ [研究时间线]                         │
│                                     │
│  ━━━━●━━━━━━●━━━━━━●━━━━━━●━━     │
│  2023.9  2024.3  2024.9  2025.3    │
│  文献综述 数据收集  分析    论文     │
└─────────────────────────────────────┘
```
- 水平线+里程碑节点
- 颜色区分完成/进行中/计划

### KeyFindings
```
┌─────────────────────────────────────┐
│ [主要发现]                           │
│                                     │
│  ① [Finding 1] [图标/小图]         │
│  ② [Finding 2] [图标/小图]         │
│  ③ [Finding 3] [图标/小图]         │
│                                     │
│  [总结一句 18pt Bold Accent色]      │
└─────────────────────────────────────┘
```
- 编号+关键词+一行总结
- 每条可用Accent色图标

### ThankYou
```
┌─────────────────────────────────────┐
│                                     │
│           谢谢！                     │
│        Thank You                     │
│                                     │
│    [姓名 • email@机构]              │
│    [实验室网站/QQ群]                 │
│                                     │
└─────────────────────────────────────┘
```
- 居中，简洁
- 联系方式用Secondary色

---

## PPT生成脚本模板

- **`templates/nature-2025-pptxgenjs.js`** — Runnable pptxgenjs template: color palette, `fitImage()` for aspect-ratio-preserving panel placement, `addImg()` for base64 embedding, `titleBar()` helper, 16:9 layout constants.
- **`references/figure-panel-cropping.md`** — Panel cropping workflow: download hi-res → PIL crop panels → embed with `fitImage()` → label sub-panels. **MUST READ before making any PPT with figures.**

Key design patterns:
- `fitImage(srcW, srcH, maxW, maxH)` — calculates display size preserving aspect ratio, centers in available area. Never use `sizing: "cover"` (crops content).
- Left 1/3 text card (colored border/muted fill) + Right 2/3 panel grid — the core academic slide layout.
- Panel labels as small gray italic text at each panel's top-left corner.
- `knownDims` dict for panel filenames → [width, height] so no runtime image reads needed.
- `imgB64()` reads + base64-encodes a local PNG for inline embedding.

---

## PPT中数据图生成流程

对于PPT中的每个数据图，遵循以下流程：

1. **确定图类型** → 查sci-fig skill的决策树
2. **确定输出preset** → PPT用`presentation`（16pt基准，200dpi）
3. **生成图** → 使用plotting-library模板或手写代码
4. **导出** → `transparent=True`，`save_fig(fig, name, transparent=True)`
5. **放入PPT** → png占满内容区，左侧或上方放文字说明
6. **QA** → 在实际幻灯片尺寸下检查可读性

### 双版本导出代码

```python
from base_plot import load_sci_style, save_fig

# PPT版本（16pt, 透明背景）
load_sci_style("presentation")
fig, ax = plt.subplots(figsize=(10, 5.6))  # 16:9
# ... plot ...
save_fig(fig, "my_figure", transparent=True)  # 输出 my_figure_demo.png

# 论文版本（7pt, 白底）
load_sci_style("publication")
fig, ax = plt.subplots(figsize=(3.35, 2.76))  # Nature单栏
# ... plot ...
save_fig(fig, "my_figure_pub", transparent=False)  # 输出 my_figure_pub_demo.png
```

---

## 中文学术惯例

### 翻译规则

| 英文 | 中文PPT | 说明 |
|------|---------|------|
| Background | 研究背景 | 不用"背景介绍" |
| Method | 研究方法 | 不用"方法学" |
| Results | 研究结果 | 每章用"结果一/二/三" |
| Discussion | 讨论 | 不用"讨论与分析" |
| Conclusion | 结论与展望 | 分开说 |
| P-value | P值 | 用大写P，斜体 |
| Fold change | 倍数变化 | 不用"折叠变化" |
| APA | 可变聚腺苷酸化 | 首次出现写全称 |

### 排版细节

- 中英文之间加空格（"RNA-seq 分析" 不是 "RNA-seq分析"）
- 基因名斜体（*APOE*，*MAPT*）
- 数字和单位之间加空格（"10 kb" 不是 "10kb"）——浓度除外（"10mM"）
- P值格式：*P* < 0.05, *P* < 0.01, *P* < 0.001（不用 *P* < 0.0001，写 *P* = 1.2 × 10⁻⁵）
- 中文标点用全角，英文标点半角
- 参考文献用上标数字标注

---

## 论文Figure抓取（Journal Club专用）

从论文直接下载figures嵌入PPT，不要让用户手动截图。

### Springer/Nature URL模式

论文DOI格式 `10.1038/s41586-025-09703-7`，figure URL：

```
https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2F{DOI_SUFFIX}/MediaObjects/{JOURNAL_CODE}_{FIG_ID}_Fig{N}_HTML.png
```

示例：`s41586-025-09703-7` → DOI_SUFFIX = `s41586-025-09703-7`, JOURNAL_CODE = `41586_2025_9703`

```bash
# 批量下载
for i in 1 2 3 4 5; do
  curl -sL -o "Fig${i}.png" \
    "https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fs41586-025-09703-7/MediaObjects/41586_2025_9703_Fig${i}_HTML.png"
done
```

### Cell/Elsevier URL模式

```
https://ars.els-cdn.com/content/image/1-s2.0-{PII}-gr{N}.lrg.jpg
```

### Science/AAAS URL模式

在论文HTML页面搜索 `<img>` 标签的 `data-src` 或 `src` 属性，通常包含 `science.org` 域名的高清PNG。

### 通用方案

如果上述模式不work，用 `web_extract` 抓取论文页面HTML，搜索 `MediaObjects` 或 `fig` 关键词提取图片URL。

**黄金规则：论文PPT必须有原文figure，不是纯文字描述。**

---

## 常见反模式

| ❌ 不要 | ✅ 应该 | 原因 |
|---------|--------|------|
| 一页PPT放整张主图 | 截取panel拼接(2-4个) | 一整张图太仓促，看不清细节 |
| 一页PPT放3+个主图 | 左1/3文字+右2/3 panel拼接 | 信息密度高但不拥挤 |
| 图片拉伸变形 | `fitImage`保持长宽比居中 | 变形=不专业 |
| 18页背景讲10分钟 | 10-12页，每页内容充实 | 密度>页数 |
| 全文字PPT | 图文3:1 | 讲10秒看30秒 |
| 内容页用纯白无结构 | 左图右文或上文下图 | 有引导视线 |
| 每页换配色 | 全局一致配色 | 专业感 |
| 小于14pt字体 | 16pt以上 | 投影仪上太小 |
| 中文PPT中英混排空格 | 中英文间加空格 | 排版规范 |
| 动画切换效果 | 无或仅淡入 | 分散注意力 |
| 全段文字读稿 | 关键词+图 | PPT辅助讲述 |
| 纯文字描述figure | 直接下载嵌入原文figure | 投影时读者对照原文 |
| 每页同一版式(标题+bullet) | 变换布局(DataFigure/Card/两列) | 单调版式=乏味=走神 |
| 白底无任何视觉结构 | 用色带/卡片/图标分区 | 专业感与可读性 |
| 用AI工具简单生成不审校 | QA循环(at least 1轮fix-verify) | 首次渲染几乎总有bug |

---

## 与sci-fig联动快速参考

生成PPT中数据图的命令模式：

```
用户: "生成一个PPT用的火山图，展示APA差异基因"

agent内部流程:
1. load_sci_style("presentation")  # 16pt基准
2. 使用plotting-library/volcano.py模板
3. save_fig(fig, "volcano_apa", transparent=True)
4. 告诉用户图已生成，可拖入PPT
5. 如果用户要PPT完整制作，切到powerpoint skill生成.pptx
```

---

## QA清单（PPT专用）

在交付PPT前检查：

**可读性**
- [ ] 所有文字 ≥ 14pt（投影环境）
- [ ] 数据图标题 ≥ 16pt
- [ ] 图例文字 ≥ 14pt
- [ ] 在1米距离投影看能否阅读

**一致性**
- [ ] 全局配色一致（同一project用同一套色彩）
- [ ] 字体统一（一种标题字体+一种正文字体）
- [ ] 间距统一（0.3"或0.5"倍数）
- [ ] 图风格一致（都用transparent背景或都用白底）

**学术规范**
- [ ] 统计值格式正确（*P* < 0.05斜体）
- [ ] 基因名斜体（*TP53*不是TP53）
- [ ] 图注标注来源和方法
- [ ] 中英文之间有空格
- [ ] 参考文献格式统一

**叙事**
- [ ] 每页有1个核心信息
- [ ] Results页有"看了什么→发现了什么→所以呢"的逻辑
- [ ] 最后2页有结论和next steps
- [ ] 预期问题有备选slides