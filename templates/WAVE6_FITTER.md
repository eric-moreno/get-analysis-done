---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: systematics-fitter
wave: 6
---

# Wave 6: Observed Results

## Required Inputs

<!-- AGENT: Load artifacts from wave manifest. Required upstream:
- analysis/wave4/statmodel/workspace.json (validated workspace spec)
- analysis/wave5/WAVE5_SUMMARY.md (Gate 5->6 passed)
- BlindingManager state must be UNBLINDED (BlindingManager.is_asimov_required() returns False)
-->

## Pre-Condition: Unblinding Verification

<!-- AGENT: Before computing any observed results, verify that the blinding state allows real data access. This is a hard requirement -- do NOT proceed if is_asimov_required() returns True. -->

```python
from gad.blinding.module import BlindingManager

bm = BlindingManager("STATE.md", "config.yaml")
assert not bm.is_asimov_required(), "Blinding state does not allow observed data access"
```

## Observed Limit (RSLT-01)

<!-- AGENT: Compute the observed 95% CL upper limit on signal strength using CLs method with real data. Compare with expected limit from Wave 4. -->

### Observed Limit Computation

```python
from gad.statistical.fitter import Fitter
from gad.statistical.workspace import WorkspaceBuilder

spec = WorkspaceBuilder.load("analysis/wave4/statmodel/workspace.json")
fitter = Fitter(spec)

# Observed limit (RSLT-01)
obs_results = fitter.observed_limit()
# obs_results: {
#   "observed_limit": float,
#   "expected_limit": {"minus2": float, "minus1": float, "median": float, "plus1": float, "plus2": float},
#   "CLs_values": [...],
#   "mu_hat": float,
#   "converged": bool
# }
```

### Observed vs Expected Comparison

| Quantity | Value |
|----------|-------|
| Observed limit (mu) | <!-- AGENT: value --> |
| Expected median (mu) | <!-- AGENT: value from Wave 4 --> |
| Observed / Expected ratio | <!-- AGENT: ratio --> |
| mu_hat (best fit) | <!-- AGENT: value --> |
| Fit converged | <!-- AGENT: yes/no --> |

### Brazil Band Summary

| Band | Limit (mu) |
|------|-----------|
| Observed | <!-- AGENT: value --> |
| -2 sigma | <!-- AGENT: value --> |
| -1 sigma | <!-- AGENT: value --> |
| Expected median | <!-- AGENT: value --> |
| +1 sigma | <!-- AGENT: value --> |
| +2 sigma | <!-- AGENT: value --> |

<!-- AGENT: If observed limit falls outside the +/- 3 sigma expected band, flag as advisory for the lead analyst. This does not automatically cause a gate failure but warrants investigation. -->

## Post-Fit Diagnostics (RSLT-02)

<!-- AGENT: Produce comprehensive post-fit diagnostics using REAL data (asimov=False). Compare with Asimov diagnostics from Wave 4 to identify any data-driven effects. -->

### Diagnostic Computation

```python
from gad.statistical.diagnostics import Diagnostics

diag = Diagnostics(spec, output_dir="analysis/wave6/diagnostics")
fit_results = fitter.fit(asimov=False)

# Post-fit diagnostic plots
diag.pull_plot(fit_results)
diag.ranking_plot(fit_results)
diag.correlation_matrix(fit_results)
diag.likelihood_scan("mu")
diag.gof_test()
```

### NP Pull Summary (Observed Data)

| NP Name | Pull (sigma) | Constraint (sigma) | Status |
|---------|-------------|-------------------|--------|
<!-- AGENT: List ALL NPs with pulls > 1.0 sigma from observed fit. Flag any with pulls > 2.0 sigma as potential anomalies for PostUnblindingClassifier. -->

- **NPs with pull > 2.0 sigma:** <!-- AGENT: count -->
- **NPs with pull > 1.0 sigma:** <!-- AGENT: count -->
- **Overall pull status:** <!-- AGENT: PASS (none > 2.0) / ADVISORY (some > 2.0) -->

### NP Ranking (Top 10, Observed)

<!-- AGENT: Report top 10 NPs ranked by impact on signal strength from observed fit. Compare ranking order with Asimov ranking from Wave 4. -->

| Rank | NP Name | Impact on mu (up) | Impact on mu (down) | Asimov Rank |
|------|---------|-------------------|---------------------|-------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

### Correlation Matrix (Observed)

<!-- AGENT: Report any NP pairs with |correlation| > 0.5. Note any new correlations not present in Asimov fit. -->

| NP 1 | NP 2 | Correlation | In Asimov? |
|------|------|-------------|------------|
<!-- AGENT: Fill for pairs with |corr| > 0.5. -->

### Goodness-of-Fit (Observed)

| Metric | Value | Requirement | Status |
|--------|-------|-------------|--------|
| GoF test statistic | <!-- AGENT: value --> | | |
| GoF p-value | <!-- AGENT: value --> | > 0.05 | <!-- AGENT: PASS/FAIL --> |
| Degrees of freedom | <!-- AGENT: value --> | | |

<!-- AGENT: If GoF p-value < 0.01, flag as Category B candidate for PostUnblindingClassifier. -->

### Likelihood Scan

<!-- AGENT: Produce likelihood scan for mu. Reference plot saved to analysis/wave6/diagnostics/likelihood_scan.pdf. Note any secondary minima or non-parabolic behavior. -->

### Diagnostic Plots

<!-- AGENT: Reference all diagnostic plots saved to analysis/wave6/diagnostics/. List: pull_plot.pdf, ranking_plot.pdf, correlation_matrix.pdf, gof_distribution.pdf, likelihood_scan.pdf. -->

## Post-Fit Yields

<!-- AGENT: Extract post-fit yields per channel per process from observed fit results. Compare with pre-fit expectations. -->

### Post-Fit Yield Table

| Channel | Process | Pre-fit Yield | Post-fit Yield | Ratio |
|---------|---------|---------------|---------------|-------|
<!-- AGENT: Fill for all channels and processes. -->

## CMS Combine Observed

<!-- AGENT: Run CMS Combine with observed data for secondary verification. -->

```python
from gad.statistical.datacard import DatacardExporter

exporter = DatacardExporter(spec)
exporter.export(output_dir="analysis/wave6/combine/", observed=True)
```

## Output Artifacts

| Artifact | Path |
|----------|------|
| Observed limit results | `analysis/wave6/results/observed_limit.json` |
| Post-fit diagnostics | `analysis/wave6/diagnostics/` |
| Post-fit yields | `analysis/wave6/results/postfit_yields.json` |
| CMS Combine observed | `analysis/wave6/combine/` |

## Summary

<!-- AGENT: Overall fitter report summary. State observed limit, comparison with expected, key diagnostic findings, and any anomalies flagged for PostUnblindingClassifier. -->

### Validation Checklist

| Check | Status |
|-------|--------|
| Observed limit computed | |
| Fit converged | |
| NP pulls reviewed | |
| GoF p-value > 0.05 | |
| Post-fit yields extracted | |
| Diagnostic plots produced | |
| CMS Combine observed run | |
