# Color Palettes Reference

## Semantic Colors (project-locked)

These map **data meaning** to color, not arbitrary assignment. One table, one truth.

| 语义 | Hex | 用途 | CVD安全 |
|------|-----|------|---------|
| proposed/己方 | `#0F4D92` | 蓝色系=提出方法 | ✓ |
| baseline/对照 | `#3775BA` | 灰蓝=基线 | ✓ |
| positive/增益 | `#2E9E44` | 绿色=正面结果 | ✓ |
| negative/衰减 | `#E53935` | 红色=负面结果 | ✓ |
| neutral/无变化 | `#8491B4` | 灰紫 | ✓ |
| up/上调 | `#D55E00` | Okabe-Ito红橙 | ✓ |
| down/下调 | `#0072B2` | Okabe-Ito蓝 | ✓ |
| ns/不显著 | `#BBBBBB` | 淡灰 | ✓ |

**方向性变量规则**：Gain/Loss、Increase/Decrease、Up/Down 是方向性变量，映射到 `up`/`down` 语义色，不用 `positive`/`negative`。

### Genomics-specific palettes
- **Volcano**: Up `#D55E00` / Down `#0072B2` / NS `#BBBBBB`
- **Survival**: High `#D55E00` / Low `#0072B2` / Censored `#BBBBBB`

### NMI稠密图pastel专用色系
- `#484878`→`#B4C0E4`（基线暗→柔）
- `#E4CCD8`→`#F0C0CC`（对比基→柔）

---

## Categorical Palettes

| 名称 | Hex | N | CVD安全 | 适用 |
|------|-----|---|---------|------|
| **Okabe-Ito** | `#E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 #000000` | 8 | ✓ | Nature金标准，默认首选 |
| **Tol Bright** | `#4477AA #EE6677 #228833 #CCBB44 #66CCEE #AA3377 #BBBBBB` | 7 | ✓ | 高辨识度线条图 |
| **Tol Muted** | `#332288 #88CCEE #44AA99 #117733 #999933 #DDCC77 #CC6677 #882255 #AA4499` | 9 | ✓ | 9组以上多类别 |
| **NPG** | `#E64B35 #4DBBD5 #00A087 #3C5488 #F39B7F #8491B8 #91D1C2 #DC0000 #7E6148 #B09C85` | 10 | ✗ | Nature Reviews Cancer |
| **NEJM** | `#BC3C29 #0072B5 #E18727 #20854E #7876B1 #6F99AD #FFDC91 #EE4C97` | 8 | ✓ | NEJM医学期刊 |
| **Lancet** | `#00468B #ED0000 #42B540 #0099B5 #925E9F #FDAF91 #AD002A #ADB6B6` | 8 | ✓ | 柳叶刀 |
| **JAMA** | `#374E55 #DF8D5B #003B5C #B6370E #56B3E0 #00A087` | 6 | ✓ | 深色调高端感 |
| **JCO** | `#0073A8 #E08B28 #A0244D #56B3E0 #3C5488 #91D1C2 #DC0000 #7E6148` | 8 | ✓ | 肿瘤学 |
| **2-group** | `#2166AC #B2182B` | 2 | ✓ | Up/Down, Ctrl/Treat |
| **Morandi** | `#A8997A #B5C4B1 #C4A882 #8E9AAF #C9B1A0 #B8A9C9` | 6 | ✓ | 柔和高级感，默认项目色 |

---

## Sequential & Diverging Colormaps

| 类型 | 推荐 | CVD安全 | 禁用 |
|------|------|---------|------|
| Sequential | `viridis`, `mako`, `inferno` | ✓ | `rainbow`, `jet` |
| Diverging | `RdBu`, `coolwarm`, `roma`, `vik` | ✓ | `rainbow`, `jet` |

**绝不用rainbow/jet。** 感知不均匀、色盲不友好。

---

## Usage

```python
from style.color_palettes import get_palette, apply_palette
apply_palette("okabe_ito")   # set global palette
colors = get_palette("npg")   # get hex list
apply_palette("morandi")      # project default
```

```r
source("style/color_palettes.R")
use_pal("okabe_ito")           # set ggplot2 default
pal <- get_pal("npg")         # named hex vector
use_pal("morandi")            # project default
```

---

## Project-Level Palette Locking

One project = one palette. Lock it in `config/plot_config.yaml`:

```yaml
# config/plot_config.yaml
palette: morandi
continuous_colormap: mako
semantic:
  up: "#D55E00"
  down: "#0072B2"
  ns: "#BBBBBB"
```

Then source this file before any plotting code. See SKILL.md "Project Config" section.
