---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: background-estimator
wave: 3
---

# Wave 3: Background Estimator Report

## Closure Tests (BKGD-01)

<!-- AGENT: Run closure tests in all validation regions using CR-extrapolated predictions (transfer factor method, NOT pure MC). Use ClosureTester.run_all_closure_tests() with total uncertainty (stat + syst combined). All VRs must have pull < 2.0 sigma to pass. -->

### Closure Test Results

```python
from gad.regions import ClosureTester, RegionValidator

tester = ClosureTester()
results = tester.run_all_closure_tests(vr_configs)
# results contains per-VR: predicted, observed, pull, passes
```

| VR Name | Predicted | Observed | Pull (sigma) | Pass (< 2.0) |
|---------|-----------|----------|--------------|---------------|
<!-- AGENT: Fill one row per validation region. Pull = |observed - predicted| / total_uncertainty. -->

### Closure Test Summary

- **Total VRs tested:** <!-- AGENT: count -->
- **VRs passing:** <!-- AGENT: count passing -->
- **VRs failing:** <!-- AGENT: list any failing VR names -->
- **Overall status:** PASS / FAIL

## Data/MC Comparisons (BKGD-02)

<!-- AGENT: Validate data/MC agreement in all CRs and VRs for key kinematic distributions. Target chi2/ndf < 2.0 for all distributions. Use RegionValidator.chi2_ndf(). -->

### Distribution Agreement

```python
validator = RegionValidator()
for dist_name, data_hist, mc_hist in distributions:
    chi2 = validator.chi2_ndf(data_hist, mc_hist)
    check = validator.check_agreement(chi2)
```

| Region | Distribution | chi2/ndf | Pass (< 2.0) |
|--------|-------------|----------|---------------|
<!-- AGENT: Fill one row per distribution per region. Include at least the discriminant variable and any variable with known mismodeling. -->

### Data/MC Comparison Plots

<!-- AGENT: Reference data/MC comparison plots saved to analysis/wave3/background/data_mc_plots/. Include ratio panels showing data/MC with uncertainty bands. -->

### Agreement Summary

- **Total distributions checked:** <!-- AGENT: count -->
- **Distributions passing:** <!-- AGENT: count passing -->
- **Distributions failing:** <!-- AGENT: list any failing -->
- **Overall status:** PASS / FAIL

## Background Yield Table (BKGD-05)

<!-- AGENT: Consolidate final background yields for all processes in all regions using the recommended estimation method from Wave 2. Use YieldTable to build the complete table. -->

### Yield Table

```python
from gad.regions import YieldTable

table = YieldTable()
table.add_process("qqbar", region_yields={"SR": (150.0, 12.0, 15.0), "CR_qqbar": (500.0, 22.0, 25.0)})
# add_process(name, region_yields={region: (yield, stat_unc, syst_unc)}, is_signal=False)
table.add_process("signal", region_yields={"SR": (10.0, 3.2, 1.0)}, is_signal=True)
df = table.build()
total_bkg = table.total_background()
```

| Process | Region | Yield | Stat Unc | Syst Unc | Total Unc | Method |
|---------|--------|-------|----------|----------|-----------|--------|
<!-- AGENT: Fill one row per process per region. Use format: yield +/- stat +/- syst. Include all backgrounds and signal. -->

### Total Background per Region

| Region | Total Background | Total Uncertainty | S/B |
|--------|-----------------|-------------------|-----|
<!-- AGENT: Compute from YieldTable.total_background(). Signal excluded from total. -->

## Summary and Recommendations

<!-- AGENT: Summarize closure test results, data/MC agreement status, and yield table completeness. Flag any issues for lead analyst review. -->

### Key Findings

<!-- AGENT: 3-5 bullet points summarizing most important findings. -->

### Issues for Lead Analyst

<!-- AGENT: Flag any marginal closure tests (1.5 < pull < 2.0), poor data/MC agreement, or unexpected yield ratios. -->
