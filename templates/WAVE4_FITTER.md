---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: systematics-fitter
wave: 4
---

# Wave 4: Fitter Report

## Workspace Construction (SYST-03)

<!-- AGENT: Build the pyhf HistFactory workspace with all channels (SR categories, CRs, VRs), samples, and NP modifiers. Validate with Asimov fit. Clip negative yields to 1e-6 floor. -->

### Workspace Definition

```python
from gad.statistical import WorkspaceBuilder

builder = WorkspaceBuilder()
builder.add_channel("SR", observed=obs_sr)
builder.add_sample("SR", "signal", sig_template, modifiers=[...])
builder.add_sample("SR", "qqbar", qqbar_template, modifiers=[...])
builder.add_channel("CR_qqbar", observed=obs_cr)
builder.add_sample("CR_qqbar", "qqbar", qqbar_cr_template, modifiers=[...])
# Add additional modifiers individually (channel_name, sample_name, modifier_dict)
for modifier in extra_modifiers:
    builder.add_modifier(modifier["channel"], modifier["sample"], modifier)
workspace = builder.build()
```

### Workspace Summary

| Property | Value |
|----------|-------|
| Number of channels | |
| Number of samples | |
| Number of NP modifiers | |
| Number of bins (total) | |

### Asimov Validation

```python
validation = builder.validate_asimov(workspace)
# validation: {"valid": bool, "pulls": dict, "max_pull": float, "fit_results": FitResults}
```

| Check | Requirement | Value | Status |
|-------|-------------|-------|--------|
| Asimov fit valid | valid = True | | |
| Max NP pull (Asimov) | max_pull < 0.5 sigma | | |
| Signal strength mu_hat | ~0.0 (bkg-only) | | |
| Negative bin yields | All >= 1e-6 | | |

## Expected Limit (SYST-04)

<!-- AGENT: Compute expected 95% CL upper limit on signal strength using CLs method with Asimov dataset. Report median and error bands. -->

### Expected Limit Computation

```python
from gad.statistical import Fitter

fitter = Fitter(workspace)
limit = fitter.expected_limit()
# limit: {"observed_limit": None, "expected_limit": float, "bands": {"-2": float, "-1": float, "+1": float, "+2": float}}
```

| Band | Expected Limit (mu) |
|------|-------------------|
| -2 sigma | |
| -1 sigma | |
| **Median** | |
| +1 sigma | |
| +2 sigma | |

### Interpretation

<!-- AGENT: Interpret the expected limit in terms of the physics signal (e.g., cross-section x BR). State whether the analysis has expected sensitivity to exclude the signal hypothesis. -->

## Fit Diagnostics (SYST-05)

<!-- AGENT: Produce comprehensive fit diagnostics from Asimov fit. Report NP pulls, NP ranking, correlation matrix, and GoF test. -->

### Nuisance Parameter Pulls

```python
from gad.statistical import Diagnostics

diag = Diagnostics(workspace, output_dir="analysis/wave4/statmodel/fit_diagnostics", experiment_style="ATLAS")
# Obtain fit_results first (required by most diagnostic methods)
fit_results = Fitter(workspace).fit(asimov=True)
diagnostics = diag.run_all_diagnostics()
# Includes: pull_plot, ranking_plot, correlation_matrix, gof_test, likelihood_scan
```

#### Pull Summary

| NP Name | Pull (sigma) | Constraint (sigma) | Status |
|---------|-------------|-------------------|--------|
<!-- AGENT: List ALL NPs with pulls > 1.0 sigma. Flag any with pulls > 2.0 sigma as FAIL. -->

- **NPs with pull > 2.0 sigma:** <!-- AGENT: count, should be 0 -->
- **NPs with pull > 1.0 sigma:** <!-- AGENT: count -->
- **Overall pull status:** PASS (no pulls > 2.0 sigma) / FAIL

#### NP Ranking (Top 10)

<!-- AGENT: Report top 10 NPs ranked by impact on signal strength mu. -->

| Rank | NP Name | Impact on mu (up) | Impact on mu (down) |
|------|---------|-------------------|---------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

#### Correlation Matrix

<!-- AGENT: Report any NP pairs with |correlation| > 0.5. Reference the full correlation matrix plot saved to analysis/wave4/statmodel/fit_diagnostics/. -->

| NP 1 | NP 2 | Correlation |
|------|------|-------------|
<!-- AGENT: Fill for pairs with |corr| > 0.5. -->

#### Goodness-of-Fit

```python
gof = diag.gof_test()
# gof: {"gof_stat": float, "p_value": float, "saturated": bool}
```

| Metric | Value | Requirement | Status |
|--------|-------|-------------|--------|
| GoF statistic (gof_stat) | | | |
| GoF p-value | | > 0.05 | |
| Saturated model | | | |

### Diagnostic Plots

<!-- AGENT: Reference all diagnostic plots saved to analysis/wave4/statmodel/fit_diagnostics/. List: pull_plot.pdf, ranking_plot.pdf, correlation_matrix.pdf, gof_distribution.pdf. -->

## Constraint Analysis (SYST-06)

<!-- AGENT: Perform in-situ constraint analysis for top 5 dominant NPs. Compare pre-fit vs post-fit uncertainty. -->

### Top 5 NP Constraints

```python
# Requires fit_results and ranking_results from earlier diagnostic calls
ranking_results, ranking_path = diag.ranking_plot(fit_results=fit_results)
constraints = diag.constraint_analysis(fit_results, ranking_results, top_n=5)
```

| Rank | NP Name | Pre-fit Unc | Post-fit Unc | Constraint Factor | Impact on mu |
|------|---------|-------------|-------------|-------------------|-------------|
| 1 | | 1.0 | | | |
| 2 | | 1.0 | | | |
| 3 | | 1.0 | | | |
| 4 | | 1.0 | | | |
| 5 | | 1.0 | | | |

<!-- AGENT: Constraint factor = post-fit / pre-fit. Values << 1.0 indicate the fit data strongly constrains that NP. Flag any unexpected strong constraints (< 0.5) that may indicate mismodeling. -->

### Constraint Assessment

<!-- AGENT: Assess whether constraint patterns are physically reasonable. Flag any NPs where the data constrains much more than expected. -->

## CMS Combine Export (SYST-07)

<!-- AGENT: Export workspace to CMS Combine-compatible datacard format as secondary output. -->

### Export

```python
from gad.statistical import DatacardExporter

exporter = DatacardExporter()
exporter.export(workspace_spec=workspace, output_dir="analysis/wave4/statmodel/combine_datacards/")
```

| Property | Value |
|----------|-------|
| Export path | analysis/wave4/statmodel/combine_datacards/ |
| Number of datacards | |
| Shape file format | |
| Validation status | <!-- AGENT: PASS if exported without errors --> |

## Sensitivity Review (SYST-08)

<!-- AGENT: Compare baseline configuration against alternatives to assess sensitivity optimization opportunities. This is the last chance to adjust categorization/fit strategy before freeze. -->

### Configuration Comparison

```python
from gad.statistical import SensitivityOptimizer

optimizer = SensitivityOptimizer()
comparison = optimizer.compare_configurations({
    "baseline": ws_baseline,
    "coarser_binning": ws_coarse,
    "aggressive_pruning": ws_pruned,
})
```

| Configuration | Expected Limit (median) | NPs | Channels | Notes |
|---------------|------------------------|-----|----------|-------|
| Baseline | | | | |
| Coarser binning | | | | |
| Aggressive pruning | | | | |
<!-- AGENT: Add more configurations if relevant (e.g., merged categories, alternative discriminant). -->

### Sensitivity Assessment

<!-- AGENT: Recommend whether to stay with baseline or adopt an alternative. Justify quantitatively. Note: this is the LAST opportunity to change fit strategy (SYST-08). -->

**Recommended configuration:** <!-- AGENT: name -->
**Justification:** <!-- AGENT: quantitative comparison -->

## Summary

<!-- AGENT: Overall fitter report summary. State workspace validation status, expected limit, and key diagnostic findings. -->

### Validation Checklist

| Check | Status |
|-------|--------|
| Workspace Asimov validation | |
| Expected limit computed | |
| NP pulls healthy (none > 2 sigma) | |
| GoF p-value > 0.05 | |
| Constraint analysis complete | |
| CMS Combine export | |
| Sensitivity review | |
