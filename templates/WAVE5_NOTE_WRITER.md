---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: note-writer
wave: 5
---

# Wave 5: Pre-Unblinding Analysis Note

## Required Inputs

<!-- AGENT: Load artifacts from wave manifest. Required upstream:
- analysis/wave1/WAVE1_SUMMARY.md (foundation: objects, samples, cross-sections)
- analysis/wave2/ (selection optimization, BDT training, signal region definition)
- analysis/wave3/ (background estimation, closure tests, data/MC agreement)
- analysis/wave4/ (systematic evaluation, workspace, expected limit, fit diagnostics)
- analysis/wave0/ANALYSIS_STRATEGY.md (analysis strategy for reference)
- templates/ANALYSIS_NOTE_SECTIONS/ (LaTeX section templates with AGENT directives)
-->

## Section Drafting Instructions

<!-- AGENT: For each section below, read the corresponding LaTeX template from templates/ANALYSIS_NOTE_SECTIONS/, find all % AGENT: directives, and populate from the corresponding wave reports. Do NOT touch Section 9 (observed results -- post-unblinding only). -->

### Verification: All Sections Exist

```python
# Verify all sections exist
from pathlib import Path
sections_dir = Path("analysis/wave5/note/sections")
required = [f"section_0{i}" for i in range(1, 9)]
for prefix in required:
    matches = list(sections_dir.glob(f"{prefix}_*.tex"))
    assert len(matches) > 0, f"Missing section: {prefix}"
    for m in matches:
        content = m.read_text()
        assert len(content) > 200, f"Section {m.name} appears to be template-only (too short)"
```

## Section 1: Introduction

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_01_introduction.tex. Fill in: analysis motivation, signal process description, previous results, document structure overview. Source from ANALYSIS_STRATEGY.md executive summary and theory scout report. -->

**Source:** Wave 0 (ANALYSIS_STRATEGY.md), Wave 1 (theory scout report)
**Output:** `analysis/wave5/note/sections/section_01_introduction.tex`

## Section 2: Dataset and Samples

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_02_dataset.tex. Fill in: data samples with luminosity, MC samples with generators and cross-sections, sample validation summary. Source from data explorer and theory scout reports. -->

**Source:** Wave 1 (data explorer report, theory scout report)
**Output:** `analysis/wave5/note/sections/section_02_dataset.tex`

## Section 3: Object Definitions

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_03_objects.tex. Fill in: reconstructed object definitions (electrons, muons, jets, b-jets, MET), identification criteria, calibration and scale factors. Source from detector specialist report and experiment context. -->

**Source:** Wave 1 (detector specialist report, experiment context)
**Output:** `analysis/wave5/note/sections/section_03_objects.tex`

## Section 4: Event Selection

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_04_selection.tex. Fill in: preselection criteria, signal region definition, cut-flow table with yields, N-1 plots, BDT/MVA discriminant description and performance. Source from signal lead and ML specialist reports. -->

**Source:** Wave 2 (signal lead report, ML specialist report)
**Output:** `analysis/wave5/note/sections/section_04_selection.tex`

## Section 5: Background Estimation

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_05_background.tex. Fill in: background estimation methods per process (MC-based vs data-driven), control region definitions, transfer factor derivation, closure tests in VRs, data/MC comparison plots. Source from background estimator report. -->

**Source:** Wave 3 (background estimator report)
**Output:** `analysis/wave5/note/sections/section_05_background.tex`

## Section 6: Systematic Uncertainties

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_06_systematics.tex. Fill in: systematic uncertainty sources (experimental and theory), evaluation methods, correlation scheme, pruning summary, dominant systematics table. Source from systematic evaluator report. -->

**Source:** Wave 4 (systematic evaluator report)
**Output:** `analysis/wave5/note/sections/section_06_systematics.tex`

## Section 7: Statistical Model

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_07_statmodel.tex. Fill in: HistFactory workspace description, channel definitions, sample composition, NP modifiers, fit methodology (CLs with profile likelihood ratio), Asimov validation results. Source from fitter report. -->

**Source:** Wave 4 (fitter report)
**Output:** `analysis/wave5/note/sections/section_07_statmodel.tex`

## Section 8: Expected Results

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/section_08_expected.tex. Fill in: expected 95% CL upper limit with Brazil band, fit diagnostics summary (NP pulls, ranking, GoF), constraint analysis, sensitivity review outcome. Source from fitter report. NOTE: This section contains ONLY Asimov/expected results. No observed data. -->

**Source:** Wave 4 (fitter report)
**Output:** `analysis/wave5/note/sections/section_08_expected.tex`

## Appendix A: Blinding Protocol (Partial)

<!-- AGENT: Read templates/ANALYSIS_NOTE_SECTIONS/appendix_a_blinding.tex. Fill in: blinding variable definition, staged unblinding sequence (waves 0-7), blinding integrity verification plan. Leave the re-blinding events log and final unblinding outcome empty (post-unblinding). Source from ANALYSIS_STRATEGY.md blinding section and BlindingManager state. -->

**Source:** Wave 0 (ANALYSIS_STRATEGY.md), BlindingManager state
**Output:** `analysis/wave5/note/sections/appendix_a_blinding.tex`

## Section 9: Observed Results (DO NOT FILL)

<!-- AGENT: DO NOT write this section. Section 9 is populated ONLY after unblinding in Wave 6. Leave the template as-is. The file section_09_observed.tex should exist as a template but must NOT contain any observed data values. -->

## Output Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Section 1: Introduction | `analysis/wave5/note/sections/section_01_introduction.tex` | |
| Section 2: Dataset | `analysis/wave5/note/sections/section_02_dataset.tex` | |
| Section 3: Objects | `analysis/wave5/note/sections/section_03_objects.tex` | |
| Section 4: Selection | `analysis/wave5/note/sections/section_04_selection.tex` | |
| Section 5: Background | `analysis/wave5/note/sections/section_05_background.tex` | |
| Section 6: Systematics | `analysis/wave5/note/sections/section_06_systematics.tex` | |
| Section 7: Statistical Model | `analysis/wave5/note/sections/section_07_statmodel.tex` | |
| Section 8: Expected Results | `analysis/wave5/note/sections/section_08_expected.tex` | |
| Appendix A: Blinding (partial) | `analysis/wave5/note/sections/appendix_a_blinding.tex` | |

## Summary

<!-- AGENT: Summarize the note-writing process. State which sections were completed, any issues encountered (missing data, ambiguous directives), and readiness for pre-unblinding review. -->
