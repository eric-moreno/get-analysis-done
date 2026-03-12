---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 3
---

# Wave 3 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 3 outcomes. Summarize closure test results, cross-check verification status, data/MC agreement, and background yield table completeness. Highlight any critical issues or notable findings. -->

## Wave 3 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Background Estimator | Closure tests, data/MC comparisons, background yield table | |
| Cross-Checker | Cut-flow reproduction, background estimate reproduction, auxiliary distribution checks | |

## Closure Test Summary

<!-- AGENT: Consolidate from background estimator report. Focus on overall pass/fail and any marginal results. -->

### Results

| VR | Pull (sigma) | Status |
|----|-------------|--------|
<!-- AGENT: Copy from background estimator closure test table. -->

### Assessment

<!-- AGENT: Overall closure test assessment. Note any VRs with pulls between 1.5 and 2.0 sigma that merit monitoring. -->

## Cross-Check Summary

<!-- AGENT: Consolidate from cross-checker report. Focus on maximum discrepancies. -->

### Cut-Flow Reproduction

- **Maximum relative difference:** <!-- AGENT: value from cross-checker -->
- **Status:** PASS / FAIL

### Background Reproduction

- **Maximum pull:** <!-- AGENT: value from cross-checker -->
- **Status:** PASS / FAIL

### Auxiliary Distribution Advisories

<!-- AGENT: List any advisory warnings from cross-checker. Note that these are advisory only and do not block the gate. -->

## Data/MC Agreement Summary

<!-- AGENT: Consolidate data/MC agreement results from background estimator. -->

| Region | Worst chi2/ndf | Status |
|--------|---------------|--------|
<!-- AGENT: One row per region showing worst-case distribution. -->

## Background Yield Table

<!-- AGENT: Copy or reference final yield table from background estimator report. -->

## Outstanding Issues

<!-- AGENT: List any unresolved issues, marginal results, or items requiring attention in Wave 4. -->

1.
2.
3.

## Gate 3->4 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Gate 3->4 criterion. All criteria must pass for Wave 4 to proceed. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| Closure tests | All VR pulls < 2.0 sigma | | |
| Cross-check cut-flow | Max relative diff < 1% | | |
| Cross-check background | Pull < 1.0 sigma | | |
| Data/MC agreement | All distributions chi2/ndf < 2.0 | | |
| Background yield table | Complete for all processes and regions | | |

### Gate Counts

- **Criteria passing:** <!-- AGENT: N --> / 5
- **Criteria failing:** <!-- AGENT: N --> / 5

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions required before proceeding to Wave 4. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Wave 4 Recommendations

<!-- AGENT: Specific guidance for Wave 4 (systematics evaluation, statistical model, expected results) based on Wave 3 findings. -->

### Systematic Uncertainty Priorities

<!-- AGENT: Which systematics are expected to dominate, based on closure test results and data/MC comparisons. -->

### Statistical Model Setup

<!-- AGENT: Recommended configuration for pyhf model based on yield table, closure test results, and any issues found. -->

### Sensitivity Expectations

<!-- AGENT: Preliminary sensitivity expectations based on S/B ratios from yield table and known systematic impacts. -->
