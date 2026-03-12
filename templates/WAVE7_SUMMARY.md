---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 7
---

# Wave 7 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 7 outcomes. Summarize note compilation status, citation verification outcome, plot count and styling, self-containedness check result, and comparison to published results. State whether the analysis note is ready for circulation/review. -->

## Wave 7 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Note Writer | Complete analysis note (sections 1-9 + appendices), all figures as PDF, bibliography, compiled PDF | |
| Cross-Checker | Citation verification report | |

## Note Compilation Status

<!-- AGENT: Consolidate from note writer report. -->

| Check | Result |
|-------|--------|
| PDF compiles without errors | <!-- AGENT: yes/no --> |
| Undefined references | <!-- AGENT: count (should be 0) --> |
| Undefined citations | <!-- AGENT: count (should be 0) --> |
| PDF page count | <!-- AGENT: count --> |
| All figures rendered | <!-- AGENT: yes/no --> |

## Citation Verification

<!-- AGENT: Consolidate from cross-checker citation verification report. -->

| Metric | Value |
|--------|-------|
| Total BibTeX entries | <!-- AGENT: count --> |
| Verified via DOI | <!-- AGENT: count --> |
| Verified via arXiv | <!-- AGENT: count --> |
| Verified via INSPIRE | <!-- AGENT: count --> |
| Unverified (flagged) | <!-- AGENT: count (must be 0) --> |

### Flagged Entries

<!-- AGENT: List any citations that could not be verified. These must be resolved (removed or manually confirmed) before note circulation. If all verified, state "None -- all citations independently verified." -->

## Plot Summary

<!-- AGENT: List all regenerated plots with styling status. -->

| Plot | File | Format | mplhep Styled |
|------|------|--------|---------------|
| Cut-flow | `figures/cutflow.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| N-1 plots | `figures/n_minus_1_*.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| BDT score | `figures/bdt_score.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| BDT ROC | `figures/bdt_roc.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| CR data/MC | `figures/cr_*.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| VR data/MC | `figures/vr_*.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| NP pulls | `figures/pull_plot.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| NP ranking | `figures/ranking_plot.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| Correlation | `figures/correlation_matrix.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| GoF | `figures/gof_distribution.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| Likelihood scan | `figures/likelihood_scan.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| Brazil band | `figures/brazil_band.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| Post-fit yields | `figures/postfit_yields.pdf` | PDF | <!-- AGENT: yes/fallback --> |
| Constraint | `figures/constraint_analysis.pdf` | PDF | <!-- AGENT: yes/fallback --> |

- **Total plots:** <!-- AGENT: count -->
- **All PDF format:** <!-- AGENT: yes/no -->
- **Uniform styling:** <!-- AGENT: yes/no (all same mplhep style) -->

## Self-Containedness Check

<!-- AGENT: Report results of the self-containedness verification. -->

| Check | Status |
|-------|--------|
| All cut values in text/tables | <!-- AGENT: PASS/FAIL --> |
| All systematic values documented | <!-- AGENT: PASS/FAIL --> |
| All yields in tables | <!-- AGENT: PASS/FAIL --> |
| Full cut-flow table | <!-- AGENT: PASS/FAIL --> |
| Full systematics appendix | <!-- AGENT: PASS/FAIL --> |
| Descriptive figure captions | <!-- AGENT: PASS/FAIL --> |
| No unfilled AGENT directives | <!-- AGENT: PASS/FAIL --> |
| No code or config in note | <!-- AGENT: PASS/FAIL --> |
| Git commit hash referenced | <!-- AGENT: PASS/FAIL --> |
| All figures exist as PDF | <!-- AGENT: PASS/FAIL --> |
| Consistent number formatting | <!-- AGENT: PASS/FAIL --> |

## Comparison to Published Results

<!-- AGENT: Summarize the comparison to previously published results. State which published results were compared, the presentation format chosen, and the outcome. -->

| This Analysis | Published Result | Source | Conditions |
|---------------|-----------------|--------|------------|
| <!-- AGENT: observed limit --> | <!-- AGENT: published limit --> | <!-- AGENT: reference --> | <!-- AGENT: lumi, energy --> |

## Outstanding Issues

<!-- AGENT: List any unresolved issues or items requiring attention during review. -->

1.
2.
3.

## Gate 7 Completion Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each completion criterion. All criteria must pass for the analysis note to be considered ready for circulation. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| PDF compiles | No pdflatex errors, PDF exists | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |
| All citations verified | 0 unverified BibTeX entries (INSPIRE-HEP check) | <!-- AGENT: 0/N unverified --> | <!-- AGENT: PASS/FAIL --> |
| No unfilled directives | 0 remaining `% AGENT:` placeholders with [value] markers | <!-- AGENT: count --> | <!-- AGENT: PASS/FAIL --> |
| All figures as PDF | Every `\includegraphics` resolves to existing PDF file | <!-- AGENT: count found/expected --> | <!-- AGENT: PASS/FAIL --> |
| Section 9 populated | section_09_observed.tex contains observed limit, yields, diagnostics | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |
| Self-contained | All self-containedness checklist items pass | <!-- AGENT: N/N pass --> | <!-- AGENT: PASS/FAIL --> |
| Published comparison | Note includes comparison to previously published results (DOCS-02) | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |
| Bibliography generated | references.bib exists with entries from all wave reports | <!-- AGENT: N entries --> | <!-- AGENT: PASS/FAIL --> |

### Gate Counts

- **Criteria passing:** <!-- AGENT: N --> / 8
- **Criteria failing:** <!-- AGENT: N --> / 8

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Final Review Recommendations

<!-- AGENT: Items for the lead analyst or collaboration review. -->

### Priority Items

<!-- AGENT: Key items reviewers should focus on. -->

### Known Limitations

<!-- AGENT: Any analysis limitations or caveats that reviewers should be aware of. -->
