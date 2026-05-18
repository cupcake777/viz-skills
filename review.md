**🔴 需要修的问题（按优先级）：**

**1. sci-fig/SKILL.md 791行太胖了**

skill的入口文档应该精简（150行内），细节放references/。791行的SKILL意味着Codex每次绘图任务都要读这么多——你的token花掉一半在这上面，难怪两天烧完$20。建议拆分。

**2. 决策树重复了**

看88-165行，DIST/COMP/TREND先列了一遍，然后"时间/有序变化"、"基因组数据子类"、"比例/组成"又列了一遍同样的图类型。明显是合并历史版本时没去重，留两份Codex会困惑。

**3. VPS私有内容混进公共skill了**
- `/root/ops/plotting/` 硬编码路径
- "Brain API"、"Gallery"、"Telegram"、`gallery_feedback.jsonl`
- "不在VPS开新端口serve web页面"

这些是你VPS的私有infra，不该在跨设备复用的skill里。Codex在office workstation上跑也会试着访问这些，肯定失败。

**4. 配色逻辑分裂**

SKILL.md里同时存在三套语义色：
- 173-179行：`#0F4D92 proposed / #2E9E44 positive / #E53935 negative`
- 295-303行：又一套差不多的
- 340-348行：Okabe-Ito默认 + NPG各图自带

**而且我们刚做的Morandi palette和plot_config.yaml完全没接进来**。Codex看到哪套先用哪套，你的项目色板会输给skill里的defaults。

**5. 模板和skill自己打架**

`volcano.R`里写死了 `up="#D73027", down="#4575B4"`，但SKILL.md规定 `up=#D55E00, down=#0072B2`。同一个repo两套真相。

**6. 没有项目config接入机制**

skill里没有这条规则：

> "如果项目根目录有 `config/plot_config.yaml`，**先source它**，它的palette覆盖所有默认。"

这条不写进去，我们辛苦定的Morandi色就用不上。
