---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 6
---

# Wave 6 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 6 outcomes. Summarize observed limit, comparison with expected, post-fit diagnostic status, cross-checker verification, and any post-unblinding problems classified. State whether the analysis result is ready for documentation. -->

## Wave 6 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Systematics Fitter | Observed limit, post-fit diagnostics, post-fit yields, CMS Combine observed | |
| Cross-Checker | Independent observed limit verification, SR yield verification | |

## Observed Results Summary

<!-- AGENT: Consolidate from fitter report. Present the key physics result. -->

### Key Result

| Quantity | Value |
|----------|-------|
| Observed 95% CL upper limit (mu) | <!-- AGENT: value --> |
| Expected median limit (mu) | <!-- AGENT: value --> |
| Observed / Expected ratio | <!-- AGENT: ratio --> |
| Best-fit mu_hat | <!-- AGENT: value --> |
| Significance (if excess) | <!-- AGENT: value or N/A --> |

### Comparison with Expected

<!-- AGENT: Interpret the observed result in context of the expected limit. Is the observed limit within the +/- 2 sigma expected band? Any indication of excess or deficit? -->

## Post-Fit Diagnostics Summary

<!-- AGENT: Consolidate diagnostic results from fitter report. -->

### NP Pull Status (Observed)

- **NPs with pull > 2.0 sigma:** <!-- AGENT: count (flag for classifier) -->
- **NPs with pull > 1.0 sigma:** <!-- AGENT: count -->

### GoF Test (Observed)

- **p-value:** <!-- AGENT: value -->
- **Status:** <!-- AGENT: PASS / FAIL -->

### Notable Observations

<!-- AGENT: Document any notable differences between observed and Asimov diagnostics (new large pulls, changed NP ranking, new correlations). -->

## Cross-Checker Verification

<!-- AGENT: Consolidate from cross-checker report. -->

| Check | Requirement | Value | Status |
|-------|-------------|-------|--------|
| Observed limit agreement | Relative diff < 1% | <!-- AGENT: value --> | |
| mu_hat pull | < 0.5 sigma | <!-- AGENT: value --> | |
| SR yield match | Exact agreement | <!-- AGENT: yes/no --> | |

## Post-Unblinding Problem Classification

<!-- AGENT: Run anomaly detection checks on the observed results. Classify any detected problems into Categories A, B, or C. -->

### Anomaly Detection

```python
from gad.statistical.classifier import PostUnblindingClassifier

classifier = PostUnblindingClassifier("STATE.md")

# Anomaly detection thresholds
# NP pull > 2.0 sigma: Category A candidate
# GoF p-value < 0.01: Category B candidate
# Observed limit outside 3-sigma expected: advisory flag
# Lead analyst makes final classification
```

### Problem Classification

<!-- AGENT: If anomalies detected, classify each. If no anomalies, state "No anomalies detected." -->

| Problem | Description | Category | Resolution |
|---------|-------------|----------|------------|
<!-- AGENT: Fill if anomalies found. Categories:
  A = Minor (document and proceed) -- e.g., single NP pull ~2.0 sigma with known cause
  B = Significant (requires re-blinding and investigation) -- e.g., GoF p-value < 0.01, unexpected large excess
  C = Critical (analysis invalid, major rework needed) -- e.g., fit does not converge, data corruption
-->

### Category Definitions

| Category | Severity | Action |
|----------|----------|--------|
| A | Minor | Document in note, proceed to Wave 7 |
| B | Significant | Re-blind, investigate, re-run affected waves, second unblinding |
| C | Critical | Analysis invalid, major rework required |

<!-- AGENT: If Category B problem found, trigger re-blinding via BlindingManager.transition("BLINDED"). The checklist will be reset, requiring full re-validation before second unblinding attempt. -->

## Analysis Note Updates

### Section 9: Observed Results

<!-- AGENT: Draft Section 9 content with observed results for the note writer to incorporate. Include: observed limit, Brazil band comparison, post-fit diagnostics summary, observed vs expected interpretation. -->

**Output:** `analysis/wave6/note/section_09_observed.tex`

### Appendix A: Blinding Protocol (Final)

<!-- AGENT: Complete Appendix A with: final unblinding timestamp, re-blinding events (if any), final checklist state, blinding audit trail. -->

**Output:** `analysis/wave6/note/appendix_a_blinding_final.tex`

## Outstanding Issues

<!-- AGENT: List any unresolved issues or items requiring attention in Wave 7. -->

1.
2.
3.

## Gate 6->7 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Gate 6->7 criterion. All criteria must pass for Wave 7 (documentation) to proceed. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| Observed limit computed | observed_limit.json exists with valid float | <!-- AGENT: value --> | <!-- AGENT: PASS/FAIL --> |
| Post-fit diagnostics | All diagnostic plots produced | <!-- AGENT: count/expected --> | <!-- AGENT: PASS/FAIL --> |
| Cross-checker verification | Relative limit diff < 1%, mu_hat pull < 0.5 | <!-- AGENT: values --> | <!-- AGENT: PASS/FAIL --> |
| Problems classified | All anomalies classified as A/B/C (if any) | <!-- AGENT: count or N/A --> | <!-- AGENT: PASS/FAIL --> |
| Section 9 drafted | section_09_observed.tex has content | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |
| Appendix A completed | appendix_a_blinding.tex has final content | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |
| No unresolved Category B | If Category B found, re-blinding occurred and analysis re-ran | <!-- AGENT: N/A or resolved --> | <!-- AGENT: PASS/FAIL --> |

### Gate Counts

- **Criteria passing:** <!-- AGENT: N --> / 7
- **Criteria failing:** <!-- AGENT: N --> / 7

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions. Category B triggers re-blinding and full re-analysis before second attempt. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Wave 7 Recommendations

<!-- AGENT: Specific guidance for Wave 7 (documentation) based on Wave 6 findings. -->

### Documentation Priorities

<!-- AGENT: List items for the note writer to focus on based on the observed results. -->

### Final Review Items

<!-- AGENT: Items for final review before publication/approval. -->
