# viz-skills

Scientific visualization skill collection for AI agents. [Agent Skills](https://agentskills.io/) standard format — works with Codex, Claude Code, Cursor, and any compatible agent.

## Install

```bash
# Install all skills
npx skills add cupcake777/viz-skills

# Or install individual skills
npx skills add cupcake777/viz-skills sci-fig
npx skills add cupcake777/viz-skills powerpoint
npx skills add cupcake777/viz-skills academic-slides
npx skills add cupcake777/viz-skills plotting-library
```

## Skills

### [sci-fig](sci-fig/) — Scientific Figure Generation

Chart type selection, Claim-based decision tree, visual standards (color palettes, typography, presets), R/Python recipes, and a learning protocol for absorbing new figure styles.

- Claim-driven decision tree (DIST/COMP/TREND/RELATE/...)
- Mandatory output rules (PDF+PNG, no title in code, explicit dimensions)
- Project color configs (Nature, JAMA, APA lifespan, disease)
- QA checklist per preset (publication/presentation/poster/draft)
- Learning protocol: deconstruct → categorize → generate → verify → save

### [plotting-library](plotting-library/) — Executable Plotting Templates

Python plotting template library. 17+ runnable scripts with `generate_mock_data()` + `plot()`, shared `matplotlibrc` style config, and `catalog.yaml` index. The execution layer for sci-fig.

### [powerpoint](powerpoint/) — PPTX Manipulation

Read, edit (python-pptx surgical or XML unpack/edit/pack), and create (PptxGenJS) PowerPoint presentations. Includes design ideas, typography guides, QA workflow, and conversion scripts.

### [academic-slides](academic-slides/) — Academic Presentation

Lab meeting reports, thesis defenses, journal clubs. Chinese academic conventions, figure panel cropping workflow, PPT-specific color schemes, slide templates.

- 10-12 page density rule for lab meetings
- Figure iron rules: crop panels, preserve aspect ratio, left-text/right-figure
- Paper figure download patterns (Springer/Cell/Science URLs)

### [plotting/](plotting/) — Shared Execution Library

The actual Python template scripts and mock data shared by sci-fig and plotting-library. Not an Agent Skill itself — it's the runnable code referenced by the skills above.

## Architecture

```
viz-skills/
├── sci-fig/                   ← Knowledge: decision tree, QA, learning protocol
│   ├── SKILL.md
│   └── references/            ← Chart recipes, APA domain, Gallery workflow
├── plotting-library/          ← Knowledge: catalog index, template docs
│   └── SKILL.md
├── powerpoint/                ← Knowledge + scripts: PPTX manipulation
│   ├── SKILL.md
│   ├── references/            ← editing, pptxgenjs, python-pptx patterns
│   └── scripts/               ← Python scripts for PPTX pack/unpack/clean
├── academic-slides/           ← Knowledge + templates: academic presentations
│   ├── SKILL.md
│   ├── references/
│   └── templates/             ← nature-2025-pptxgenjs.js
└── plotting/                  ← Executable: Python plotting library
    ├── templates/*.py         ← 17+ standalone plot scripts
    ├── style/matplotlibrc     ← Global style config
    ├── catalog.yaml           ← Data type → chart → template mapping
    └── demo_data/             ← Mock datasets
```

## Updating

This repo is the source of truth. After editing:

```bash
# Sync skill content to local agent
cp sci-fig/SKILL.md ~/.hermes/skills/productivity/sci-fig/SKILL.md
cp powerpoint/SKILL.md ~/.hermes/skills/productivity/powerpoint/SKILL.md
# ... etc

# Sync plotting templates to execution directory
cp plotting/templates/*.py /root/ops/plotting/templates/
cp plotting/catalog.yaml /root/ops/plotting/catalog.yaml
```

## License

- Skill documentation (SKILL.md, references): CC BY-SA 4.0
- Python scripts (plotting templates, PPTX scripts): MIT
- PptxGenJS skill content: Proprietary (see [powerpoint/LICENSE.txt](powerpoint/LICENSE.txt))