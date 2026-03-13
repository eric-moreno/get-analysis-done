# GAD (Get Analysis Done)

Multi-agent HEP analysis framework. Orchestrates 11 specialist agents across 8 analysis waves to produce a complete, blinding-compliant, peer-reviewable analysis note from a physics prompt.

## Setup

```bash
./install.sh
```

This links the workflow engine (`~/.claude/get-analysis-done/`) and slash commands (`~/.claude/commands/gad/`), and installs the Python package.

## Key Commands

- `/gad:run-analysis` — Full pipeline: Wave 0 (strategy) through Wave 7 (documentation)
- `/gad:run-wave N` — Execute a single wave
- `/gad:help` — Complete command reference

## Architecture

- **Python package (`gad/`)**: Analysis modules (data, selection, MVA, regions, systematics, statistical, blinding, documentation)
- **Agent prompts (`agents/`)**: 11 specialist agents (lead-analyst, data-explorer, signal-lead, ml-specialist, etc.)
- **Wave manifests (`wave-manifests/`)**: YAML configs defining inputs/outputs/agents per wave
- **Gate templates (`gate-templates/`)**: Quality gate criteria between waves
- **Workflow engine (`.gad/`)**: Node.js orchestration (gad-tools.cjs), workflow definitions, templates
- **Slash commands (`commands/`)**: Claude Code command definitions (`/gad:*`)
- **Experiment configs (`experiments/`)**: Detector/object definitions per experiment

## Testing

```bash
pytest
```

Tests are self-contained with mocked dependencies (no ROOT files or network needed).

## Conventions

- Python code in `gad/` follows standard Python conventions (snake_case, type hints where present)
- Agent prompts are markdown files in `agents/` with YAML frontmatter
- Wave manifests define `clear_context`, `load_artifacts`, `agents`, and `outputs`
- Gate criteria are quantitative and measurable (never subjective)
- Blinding protocol is non-negotiable: signal region masked until quality gates pass
