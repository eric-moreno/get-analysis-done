---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: cross-checker
wave: 3
---

# Wave 3: Cross-Checker Report

## Cut-Flow Reproduction (BKGD-03)

<!-- AGENT: Independently reproduce the full cut-flow table using the same gad modules but with independently-chosen configuration. Compare against the reference cut-flow from Wave 2. Maximum relative difference must be < 1% at every cut step. -->

### Cut-Flow Comparison

```python
from gad.regions import CrossChecker

checker = CrossChecker()
result = checker.compare_cutflows(
    reference_cutflow=reference_cutflow,
    check_cutflow=independent_cutflow,
    threshold=0.01  # 1% relative difference
)
# result contains: per-cut comparison, max_relative_diff, passes
```

| Cut Step | Reference Yield | Cross-Check Yield | Relative Diff | Pass (< 1%) |
|----------|----------------|-------------------|---------------|-------------|
<!-- AGENT: Fill one row per cut step. Relative diff = |ref - check| / ref. Use independently-chosen binning and variable ordering. -->

### Cut-Flow Summary

- **Maximum relative difference:** <!-- AGENT: value -->
- **Cut step with largest difference:** <!-- AGENT: name -->
- **Overall status:** PASS / FAIL

## Background Estimate Reproduction (BKGD-03)

<!-- AGENT: Independently reproduce the dominant background estimate using the same estimation method but with independent implementation choices. Compare against the primary estimate. Pull must be < 1.0 sigma. -->

### Background Comparison

```python
result = checker.compare_yields(
    ref_yield=ref_yield, ref_uncertainty=ref_unc,
    check_yield=check_yield, check_uncertainty=check_unc
)
# result contains: pull, relative_diff, passes
```

| Background | Reference Yield +/- Unc | Cross-Check Yield +/- Unc | Pull (sigma) | Pass (< 1.0) |
|------------|------------------------|--------------------------|--------------|---------------|
<!-- AGENT: Fill one row per major background. Pull = |ref - check| / sqrt(ref_unc^2 + check_unc^2). -->

### Reproduction Summary

- **Largest pull:** <!-- AGENT: value -->
- **Background with largest pull:** <!-- AGENT: name -->
- **Overall status:** PASS / FAIL

## Auxiliary Distributions (BKGD-04)

<!-- AGENT: Check auxiliary distributions for anomalies. These are advisory-only checks and do not cause hard gate failures. Review phi distributions, vertex distributions, and run-period stability. -->

### Auxiliary Checks

```python
comparisons = [
    {"name": "phi_distribution", "data": phi_data, "mc": phi_mc, "type": "shape"},
    {"name": "vertex_distribution", "data": vtx_data, "mc": vtx_mc, "type": "shape"},
    {"name": "run_period_stability", "data": period_yields, "mc": None, "type": "stability"},
]
result = checker.check_auxiliary(comparisons)
# result contains: per-check status, advisory_only=True
```

| Distribution | Check Type | Observation | Advisory Status |
|-------------|-----------|-------------|-----------------|
| Phi distribution | Shape agreement | <!-- AGENT: note any asymmetries --> | OK / WARNING |
| Vertex distribution | Shape agreement | <!-- AGENT: note any pile-up issues --> | OK / WARNING |
| Run-period stability | Yield stability | <!-- AGENT: note any period-to-period variation --> | OK / WARNING |

### Advisory Notes

<!-- AGENT: Document any advisory warnings. These do not block the gate but should be reviewed by the lead analyst. Note: advisory_only=True means these never cause hard gate failures. -->

## Cross-Check Summary

<!-- AGENT: Overall assessment of independent verification. Highlight any discrepancies and their likely causes. -->

### Discrepancies Found

<!-- AGENT: List any discrepancies between primary and cross-check results, even if within tolerance. Document resolution or explanation. -->

### Recommendations

<!-- AGENT: Recommendations for the lead analyst based on cross-check findings. -->
