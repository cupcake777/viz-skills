# Gallery Feedback Loop

How to read and process user feedback from the Gallery's interactive buttons.

## Feedback File

Default location: `../03_plotting-library/gallery_feedback.jsonl`

Each line is a JSON object:
```json
{"chart": "volcano", "action": "approve", "suggestion": "", "timestamp": "2026-04-29T09:28:29.430278+00:00"}
{"chart": "manhattan", "action": "suggest", "suggestion": "字体太小，label应该是Gene name", "timestamp": "..."}
{"chart": "heatmap_clustered", "action": "reject", "suggestion": "", "timestamp": "..."}
```

## Processing Workflow

1. **Read feedback**: `cat ../03_plotting-library/gallery_feedback.jsonl | python3 -c "import sys,json; [print(json.dumps(json.loads(l))) for l in sys.stdin]"`
2. **For each entry**:
   - `approve` → Template confirmed, no action needed
   - `reject` → Template marked unsuitable; consider removing from active catalog
   - `suggest` → **This is the actionable feedback loop**:
     a. Read the `suggestion` field
     b. Modify the corresponding template script in `../03_plotting-library/templates/`
     c. Re-render the R template, for example `Rscript ../03_plotting-library/templates/{chart}.R`
     d. Verify the fix visually
     e. Notify user for re-confirmation
3. **After processing**: Optionally archive or truncate `../03_plotting-library/gallery_feedback.jsonl`

## Common Suggest Patterns

| Suggestion | Fix |
|-------------|-----|
| "label出图框了/溢出绘图区" | Use `adjustText` library instead of manual `annotate`; add `clip_on=True` as fallback for labels that can't reposition |
| "字体太小" | Increase `fontsize` parameter (default 16pt minimum for all labels) |
| "label应该是Gene name不是variant ID" | Add `gene_col` parameter; prioritize gene names over SNP IDs for peak labels |
| "配色问题" | Check against Nature/Safe 6 palette in matplotlibrc; use project-specific `PROJECT_COLORS` |

## Applied Fixes (from user feedback, 2026-04-29)

### Volcano plot: label clipping
- Replaced manual `ax.annotate()` with `adjustText` for gene labels
- Added `clip_on=True` fallback for labels that adjustText can't reposition
- Template: `../03_plotting-library/templates/volcano.R`

### Manhattan plot: gene labels and font size
- Added `gene_col` parameter to label peaks by Gene name (not variant/rs ID)
- Set label fontsize to the 16pt minimum
- Added `adjustText` + `clip_on=True` for label anti-overlap
- Template: `../03_plotting-library/templates/manhattan.R`

## adjustText Installation

```bash
pip install adjusttext
```

Usage in Python:
```python
from adjustText import adjust_text
texts = []
for _, row in top.iterrows():
    texts.append(ax.text(row[x], row[y], row[label_col], fontsize=7))
adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.5))
```

Always provide a fallback for when adjustText is not installed (use `clip_on=True` with manual `annotate`).
