# Visual Standards

Shared visual rules for scientific figures. Use this as the compact reference
for figure quality before looking at chart-specific recipes.

## Defaults

- Prefer R for static scientific figures.
- Use explicit width and height.
- Export final scientific figures as PDF plus PNG unless the user requests a
  different format.
- Keep plot titles and subtitles out of manuscript-style panels.
- Use captions, legends, or slide titles for narrative text.
- Use semantically stable project colors across all figures and slides.

## Typography

- Minimum text size is 16 pt for all figures produced by this skill suite.
- Traditional journal-native 6-7 pt typography is allowed only when the user
  explicitly requests it for a specific submission target.
- Presentation figures also use 16 pt minimum for tick labels, legends, and
  annotations.
- Use Arial, Helvetica, or Calibri unless the project has a defined style.
- Gene symbols should be italic where the plotting system supports it.
- Axis labels should include units when units exist.

## Color

- Prefer colorblind-aware qualitative palettes.
- Use `viridis`, `mako`, or similar perceptual maps for sequential values.
- Use `RdBu`, `coolwarm`, or another balanced diverging map for centered
  signed values.
- Do not use rainbow or jet palettes.
- Do not encode the same biological group with different colors across figures.

## Labels

- Use `ggrepel` for dense R labels.
- Label only the top hits when the figure is crowded.
- Rotate, wrap, abbreviate, or flip long categorical axes.
- Check the final exported size, not only the plotting window.

## Common Anti-Patterns

| Avoid | Prefer |
|---|---|
| bar + error bar for continuous distributions | violin/box/jitter/raincloud |
| Venn diagrams for more than 3 sets | UpSet plot |
| pie charts with many categories | ordered bar or dot plot |
| dense scatter without alpha/binning | alpha, hex bin, density contour |
| 3D bars | 2D encodings |
| unlabeled units | explicit axis units |
| full paper multi-panel figure in PPT | cropped readable panels |

## QA Checklist

- The chart type matches the scientific claim.
- Axis labels and legends are interpretable without guessing.
- Text is readable at the final output size.
- Labels do not overlap important marks.
- Colors match the project semantics.
- Bar charts start at zero when encoding magnitude.
- Statistical annotations are defined and not decorative.
- Exported files exist and use the requested size and format.
