# Telegram Chart Delivery

Generate matplotlib charts as PNG and send via Telegram as native photos.

## Steps
1. Install matplotlib if needed: `pip3 install matplotlib -q`
2. Write chart script using dark-theme template
3. Save PNG to `/tmp/chart_<name>.png` (dpi=150, dark bg)
4. Send in response via `MEDIA:/tmp/chart_<name>.png`

## Dark Theme Template
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1a1a2e')
# ... plot logic ...
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')
plt.tight_layout()
plt.savefig('/tmp/chart_X.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
```

For text on charts: always set `textprops={'color': 'white'}` and title with `color='white'`.

## Pitfalls
- **Chinese fonts NOT available** on VPS — use English labels only, or install `fonts-wqy-zenhei`
- **vision_analyze hallucinates on self-generated charts** — don't trust its descriptions
- **matplotlib may not be pre-installed** — always check or install first
- **Do NOT use `Agg` backend in venv** — use system python3 if venv lacks matplotlib

## Telegram Delivery
Include in response: `MEDIA:/tmp/chart_X.png`