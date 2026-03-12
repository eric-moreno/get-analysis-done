---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 4
---

# Wave 4 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 4 outcomes. Summarize workspace construction, expected limit result, fit diagnostic status, and sensitivity review outcome. Highlight any critical issues or notable findings. -->

## Wave 4 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Systematics Fitter | Systematic evaluation, workspace construction, expected limit, fit diagnostics, Combine export, sensitivity review | |

## Systematic Evaluation Summary

<!-- AGENT: Consolidate from systematic evaluator report. Focus on dominant systematics and pruning results. -->

### Dominant Systematics

| Rank | Source | Type | Max Effect (%) |
|------|--------|------|---------------|
<!-- AGENT: Copy top 5 from evaluator report. -->

### Pruning Summary

- **Total systematic sources:** <!-- AGENT: count -->
- **Kept after pruning:** <!-- AGENT: count -->
- **Pruned (< 0.5% effect):** <!-- AGENT: count -->

## Workspace Summary

<!-- AGENT: Consolidate from fitter report. Focus on workspace composition and validation. -->

| Property | Value |
|----------|-------|
| Channels | |
| Samples | |
| NP Modifiers | |
| Asimov validation | PASS / FAIL |

## Expected Limit

<!-- AGENT: Copy expected limit table from fitter report. -->

| Band | Expected Limit (mu) |
|------|-------------------|
| -2 sigma | |
| -1 sigma | |
| **Median** | |
| +1 sigma | |
| +2 sigma | |

### Physics Interpretation

<!-- AGENT: Interpret in terms of cross-section x BR or signal model parameters. -->

## Fit Diagnostics Summary

<!-- AGENT: Consolidate diagnostic results from fitter report. -->

### NP Pull Status

- **NPs with pull > 2.0 sigma:** <!-- AGENT: count (should be 0) -->
- **NPs with pull > 1.0 sigma:** <!-- AGENT: count -->

### GoF Test

- **p-value:** <!-- AGENT: value -->
- **Status:** PASS / FAIL

### Top Constraints

<!-- AGENT: List top 3 most constrained NPs from constraint analysis. -->

## Sensitivity Review Outcome

<!-- AGENT: Summarize sensitivity comparison from fitter report. State final configuration choice. -->

**Final configuration:** <!-- AGENT: baseline / alternative -->
**Justification:** <!-- AGENT: 1-sentence quantitative justification -->

## Outstanding Issues

<!-- AGENT: List any unresolved issues, concerns, or items requiring attention in Wave 5 (pre-unblinding). -->

1.
2.
3.

## Gate 4->5 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Gate 4->5 criterion. All criteria must pass for Wave 5 (pre-unblinding) to proceed. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| Workspace validates | Asimov NP pulls < 0.5 sigma | | |
| Expected limit computed | Positive and finite | | |
| NP pulls healthy | No pulls > 2.0 sigma | | |
| GoF p-value | > 0.05 | | |
| Constraint analysis complete | Top 5 NPs documented | | |
| CMS Combine datacard exported | Export successful | | |
| Sensitivity review documented | Alternatives compared | | |

### Gate Counts

- **Criteria passing:** <!-- AGENT: N --> / 7
- **Criteria failing:** <!-- AGENT: N --> / 7

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions required before proceeding to Wave 5 (pre-unblinding). -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Wave 5 Recommendations

<!-- AGENT: Specific guidance for Wave 5 (pre-unblinding review) based on Wave 4 findings. -->

### Pre-Unblinding Checklist Items

<!-- AGENT: Identify specific items the pre-unblinding review should verify based on fit diagnostic findings. -->

### Known Risks

<!-- AGENT: Document any known risks or potential issues that could affect the unblinding result (e.g., large systematic uncertainties, marginal GoF, strongly constrained NPs). -->
