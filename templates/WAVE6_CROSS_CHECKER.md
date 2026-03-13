---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: cross-checker
wave: 6
---

# Wave 6: Observed Result Verification

## Required Inputs

<!-- AGENT: Load artifacts from wave manifest. Required upstream:
- analysis/wave4/statmodel/workspace.json (validated workspace spec)
- analysis/wave6/results/observed_limit.json (primary fitter observed results)
- analysis/wave6/results/postfit_yields.json (primary fitter post-fit yields)
- BlindingManager state must be UNBLINDED
-->

## Independent Observed Limit (RSLT-03)

<!-- AGENT: Independently compute the observed limit using the same workspace but your own Fitter instance. Do NOT read the primary fitter's results before computing your own. Compare only after independent computation is complete. -->

### Independent Computation

```python
# Independent verification
from gad.statistical.workspace import WorkspaceBuilder
from gad.statistical.fitter import Fitter
import json

# Load workspace independently
spec = WorkspaceBuilder.load("analysis/wave4/statmodel/workspace.json")
fitter = Fitter(spec)

# Compute observed limit independently
xcheck_results = fitter.observed_limit()

# NOW compare with primary results
primary_results = json.load(open("analysis/wave6/results/observed_limit.json"))
```

### Limit Comparison

| Quantity | Primary | Cross-Check | Relative Diff |
|----------|---------|-------------|---------------|
| Observed limit (mu) | <!-- AGENT: value --> | <!-- AGENT: value --> | <!-- AGENT: value --> |
| mu_hat | <!-- AGENT: value --> | <!-- AGENT: value --> | <!-- AGENT: value --> |

### Verification Criteria

```python
# Verify observed limit within 1% relative difference
rel_diff = abs(xcheck_results["observed_limit"] - primary_results["observed_limit"]) / primary_results["observed_limit"]
assert rel_diff < 0.01, f"Limit disagreement: {rel_diff:.4f}"
```

| Check | Requirement | Value | Status |
|-------|-------------|-------|--------|
| Observed limit agreement | Relative diff < 1% | <!-- AGENT: value --> | <!-- AGENT: PASS/FAIL --> |
| mu_hat pull | \|pull\| < 0.5 sigma | <!-- AGENT: value --> | <!-- AGENT: PASS/FAIL --> |
| Fit convergence | Both fits converge | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |

## Independent SR Yield Verification

<!-- AGENT: Independently extract observed signal region yield from the workspace data and compare with primary analysis. -->

### SR Yield Comparison

| Channel | Primary SR Yield | Cross-Check SR Yield | Agreement |
|---------|-----------------|---------------------|-----------|
<!-- AGENT: Fill for each signal region channel. Yields must match exactly (integer observed counts). -->

## Independent Post-Fit Comparison

<!-- AGENT: Compare post-fit NP values between primary and cross-check fits. Large differences in fitted NP values would indicate instability. -->

### NP Comparison (Top 10 by Impact)

| NP Name | Primary Pull | Cross-Check Pull | Diff |
|---------|-------------|------------------|------|
<!-- AGENT: Fill for top 10 NPs by impact. Differences should be < 0.1 sigma for a stable fit. -->

## Discrepancy Investigation

<!-- AGENT: If any verification check fails, document the investigation here. Include: what failed, potential causes, resolution attempts, and recommendation (proceed / re-investigate / escalate). -->

### Discrepancies Found

<!-- AGENT: List any discrepancies, even if within tolerance. -->

### Resolution

<!-- AGENT: Document resolution or explanation for each discrepancy. -->

## Output Artifacts

| Artifact | Path |
|----------|------|
| Verification results | `analysis/wave6/crosscheck/verification_results.json` |

## Summary

<!-- AGENT: Summarize verification findings. State whether the primary observed result is independently confirmed. Flag any concerns for the lead analyst. -->

### Verification Status

- **Observed limit verified:** <!-- AGENT: yes/no -->
- **SR yield verified:** <!-- AGENT: yes/no -->
- **Post-fit NPs consistent:** <!-- AGENT: yes/no -->
- **Overall verification:** <!-- AGENT: PASS/FAIL -->
