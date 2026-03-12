# Get Analysis Done (GAD)

Agent-driven HEP analysis automation framework. GAD orchestrates a multi-wave analysis pipeline — from physics prompt to publication-quality analysis note — using specialized AI agents.

## Overview

GAD automates the full HEP analysis workflow:

| Wave | Agents | What it does |
|------|--------|-------------|
| 0 | Lead Analyst | Generates analysis strategy from physics prompt |
| 1 | Data Explorer, Detector Specialist, Theory Scout | Data inventory, detector context, theory review |
| 2 | Signal Lead, ML Specialist, Background Estimator | Event selection, BDT training, background methods |
| 3 | Background Estimator, Cross-Checker | Region definitions, validation, cross-checks |
| 4 | Systematics-Fitter, Systematic Source Evaluator | Systematic uncertainties, expected limits |
| 5 | Note Writer, Cross-Checker | Pre-unblinding review, analysis note draft |
| 6 | Fitter, Cross-Checker | Unblinding, observed limits, post-fit diagnostics |
| 7 | Note Writer, Cross-Checker | Final note with results, bibliography, compilation |

Each wave produces artifacts consumed by downstream waves. Quality gates between waves enforce correctness before proceeding.

## Installation

```bash
git clone https://github.com/eric-moreno/get-analysis-done.git
cd get-analysis-done
pip install -e ".[all,dev]"
```

### Dependencies

**Core:** numpy, pyyaml, requests

**Plotting:** matplotlib, mplhep (experiment-specific styling)

**Statistics:** pyhf, iminuit, scipy

## Project Structure

```
get-analysis-done/
├── gad/                        # Python package
│   ├── config/                 # Analysis configuration management
│   ├── data/                   # Data loading (ROOT, HDF5, CSV)
│   ├── strategy/               # Strategy generation from physics prompts
│   ├── selection/              # Event selection & cut optimization
│   ├── mva/                    # BDT/MVA training & evaluation
│   ├── regions/                # Signal/control/validation regions
│   ├── systematics/            # Systematic uncertainty handling
│   ├── statistical/            # Fitting, limit setting, diagnostics
│   ├── blinding/               # Blinding integrity & signal injection
│   └── documentation/          # Citations, plots, LaTeX compilation
├── agents/                     # Agent prompt definitions (gad-*.md)
├── templates/                  # Wave report templates & LaTeX note sections
├── wave-manifests/             # YAML manifests defining each wave's inputs/outputs
├── gate-templates/             # Quality gate criteria between waves
├── experiments/                # Experiment context definitions
│   ├── aleph/                  # ALEPH reference analysis (Zh → bbbar)
│   └── _template/              # Template for adding new experiments
├── commands/                   # Claude Code slash commands (/gad:*)
├── .gad/                       # GAD workflow engine (workflows, references, templates)
└── tests/python/               # Test suite
```

## Usage with Claude Code

GAD is designed to run inside [Claude Code](https://claude.com/claude-code). The slash commands drive the analysis:

```bash
# Start a new analysis
/gad:run-analysis

# Run a specific wave
/gad:run-wave 3

# Execute the full pipeline end-to-end
/gad:run-analysis
```

The `/gad:run-analysis` command takes a physics prompt and runs all waves autonomously, pausing only for:
- Strategy approval (after Wave 0)
- Unblinding authorization (before Wave 6)

## Adding a New Experiment

1. Copy `experiments/_template/` to `experiments/<your-experiment>/`
2. Fill in `detector.yaml` and `objects.yaml` with your experiment's specifics
3. Optionally add `mc_generators.yaml`, `performance.yaml`, `references.yaml`
4. Run `/gad:run-analysis` with your experiment context

See `experiments/aleph/` for a complete example.

## Running Tests

```bash
pytest
```

Tests are fully self-contained with mocked external dependencies (no network calls, no ROOT files needed).

## License

MIT
