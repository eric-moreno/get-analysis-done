---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 2
---

# Wave 2 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 2 outcomes. Summarize selection performance, BDT validation status, and background estimation readiness. Highlight any critical issues or notable findings. -->

## Wave 2 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Signal Lead | Cut-flow table, N-1 plots, variable rankings, categorization study, binned templates | |
| ML Specialist | Trained BDT model, overtraining validation, feature importance, robustness report | |
| Background Estimator | CR/VR definitions, purity validation, data/MC agreement, estimation comparison | |

## Selection Summary

<!-- AGENT: Consolidate from signal lead report. Focus on final selection description and key performance numbers. -->

### Final Selection Description

<!-- AGENT: Describe the complete event selection in plain language (preselection + optimized cuts). -->

### Key Efficiency Numbers

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Preselection signal efficiency | | > 80% | |
| Trivial background rejection | | > 90% | |
| Final selection Asimov significance | | | |
| Variables studied | | >= 20 | |

### Cut-Flow Summary

<!-- AGENT: Include or reference the final cut-flow table from signal lead report. -->

## BDT Summary

<!-- AGENT: Consolidate from ML specialist report. Focus on model performance and validation status. -->

### Best Model Performance

| Metric | Value |
|--------|-------|
| AUC | |
| Overtraining KS (signal) | |
| Overtraining KS (background) | |
| Overall passes overtraining | |

### Key Features

<!-- AGENT: List top 5 features by importance from ML specialist report. -->

| Rank | Feature | Gain Fraction |
|------|---------|---------------|

### Validation Status

- **Overtraining test:** PASS/FAIL
- **Systematic robustness:** PASS/FAIL
- **Data/MC agreement:** <!-- AGENT: From background estimator CR validation -->

## Background Estimation Summary

<!-- AGENT: Consolidate from background estimator report. Focus on methods chosen and validation status. -->

### Methods Per Background

| Background | Method Chosen | CR Purity | chi2/ndf | Status |
|------------|---------------|-----------|----------|--------|

### CR/VR Validation Status

<!-- AGENT: Summarize whether all CRs pass purity and agreement requirements. Flag any marginal cases. -->

## Categorization Decision

<!-- AGENT: Based on signal lead's categorization evaluation, make final decision on inclusive vs categorized approach. -->

| Configuration | Combined Significance | Notes |
|---------------|----------------------|-------|
| Inclusive | | |
| Categorized | | |

**Decision:** <!-- AGENT: Inclusive or Categorized -->
**Justification:** <!-- AGENT: Quantitative justification based on significance improvement -->

## Shape vs Counting Decision

<!-- AGENT: Based on signal lead's shape vs counting comparison, make final decision. Note stat-only caveat. -->

| Approach | Expected Significance (stat-only) |
|----------|-----------------------------------|
| Shape | |
| Counting | |

**Decision:** <!-- AGENT: Shape or Counting -->
**Justification:** <!-- AGENT: Quantitative justification -->
**Caveat:** This comparison is stat-only. Full evaluation with systematic uncertainties will be performed in Phase 4.

## Outstanding Issues

<!-- AGENT: List any unresolved issues, concerns, or items requiring attention in Phase 3/4. -->

1.
2.
3.

## Gate 2->3 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Wave 2 quality gate criterion. All criteria must pass for Wave 3 to proceed. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| Preselection signal efficiency | > 80% | | |
| Overtraining KS test | Both pass (p > 0.05) | | |
| CR purity (all major backgrounds) | > 50% | | |
| Data/MC agreement in CRs | chi2/ndf < 2.0 | | |
| Cut-flow table complete | All samples included | | |
| N-1 plots produced | One per cut variable | | |
| Variable study | >= 20 variables ranked | | |
| Categorization evaluated | Inclusive vs categorized compared | | |
| Shape vs counting evaluated | Both approaches compared | | |
| Binned templates produced | Ready for Phase 4 pyhf | | |

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions required before proceeding. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Wave 3 Recommendations

<!-- AGENT: Specific guidance for Wave 3 (background validation, systematics, statistical model) based on Wave 2 findings. -->

### Background Estimation Priorities

<!-- AGENT: Which backgrounds need most attention in closure tests. -->

### Systematic Uncertainty Priorities

<!-- AGENT: Which systematics are expected to dominate, based on BDT robustness check and background estimation method. -->

### Statistical Model Setup

<!-- AGENT: Recommended configuration for pyhf model based on shape/counting decision and categorization decision. -->
