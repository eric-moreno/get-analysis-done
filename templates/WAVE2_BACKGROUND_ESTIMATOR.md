---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: background-estimator
wave: 2
---

# Wave 2: Background Estimator Report

## Background Composition

<!-- AGENT: List all major backgrounds after preselection with expected yields. Use signal lead's preselection to define the starting point. -->

### Expected Yields After Preselection

| Background Process | Expected Yield | Fraction of Total | Priority |
|--------------------|----------------|--------------------|----------|

### Background Classification

<!-- AGENT: Classify each background as major (> 10% of total) or minor. Major backgrounds require dedicated CRs; minor backgrounds may be grouped or taken from MC. -->

## Control Region Definitions

<!-- AGENT: Define one CR per major background by inverting or modifying signal region cuts. Use RegionDesigner to construct regions programmatically. -->

### CR Definitions

```python
from gad.regions import RegionDesigner
from gad.selection import SelectionEngine

sr_cuts = config.signal_region["cuts"]
designer = RegionDesigner(sr_cuts)

# AGENT: Define one CR per major background
cr_qqbar = designer.define_cr("CR_qqbar", target_background="qqbar",
                               invert_cuts=["thrust"])
```

| Region | Target Background | Inverted Cuts | Additional Cuts | Expected Purity |
|--------|-------------------|---------------|-----------------|-----------------|

### CR Design Rationale

<!-- AGENT: For each CR, explain why the chosen cut inversions enrich the target background while maintaining kinematic similarity to the SR. -->

## Control Region Validation

<!-- AGENT: Validate each CR for purity (> 50%) and data/MC agreement (chi2/ndf < 2.0). -->

### Purity Check

| CR | Target Background | Purity | Target (> 50%) | Status |
|----|-------------------|--------|-----------------|--------|

```python
from gad.regions import RegionValidator

validator = RegionValidator()
purity = validator.compute_purity(events_dict, mask_fn, "qqbar")
check = validator.check_purity(purity)
assert check["passes"], f"CR purity {purity:.2f} < 0.50"
```

### Data/MC Agreement

<!-- AGENT: Check key distributions in each CR. Report chi2/ndf for the most important kinematic variables. -->

| CR | Variable | chi2/ndf | Target (< 2.0) | Status |
|----|----------|----------|-----------------|--------|

```python
chi2 = validator.chi2_ndf(data_hist, mc_hist)
check = validator.check_agreement(chi2)
assert check["passes"], f"chi2/ndf = {chi2:.2f} > 2.0"
```

### Data/MC Comparison Plots

<!-- AGENT: Reference data/MC comparison plots for key variables in each CR. Output to analysis/wave2/regions/cr_plots/ -->

## Validation Region Definitions

<!-- AGENT: Define one VR per major background. VRs should be kinematically between CR and SR to test background modeling extrapolation. -->

### VR Definitions

```python
vr_qqbar = designer.define_vr("VR_qqbar", target_background="qqbar",
                               tighten_cuts={"thrust": 0.85})
```

| Region | Target Background | Relation to SR | Relation to CR | Expected Yield |
|--------|-------------------|----------------|----------------|----------------|

### VR Design Rationale

<!-- AGENT: Explain kinematic placement of each VR relative to CR and SR. VRs test the interpolation/extrapolation of background model. -->

## Estimation Method Comparison

<!-- AGENT: For each major background, compare MC-based and data-driven estimation methods. Use EstimationComparator to quantify differences. -->

### Method Comparison Per Background

```python
from gad.regions import EstimationComparator

comparator = EstimationComparator()
mc_est = comparator.mc_based_estimate(mc_yield=150, mc_stat_err=12, mc_syst_frac=0.15)
tf_est = comparator.transfer_factor_estimate(cr_data=200, cr_mc=180, sr_mc=150)
abcd_est = comparator.abcd_estimate(region_a=50, region_b=100, region_c=80, region_d=160)
comparison = comparator.compare_methods(mc_est, tf_est)
```

#### Background: <!-- AGENT: Repeat for each major background -->

| Method | Estimated Yield | Stat Uncertainty | Syst Uncertainty | Total Uncertainty |
|--------|----------------|------------------|------------------|-------------------|
| MC-based | | | | |
| Transfer factor | | | | |
| ABCD (if applicable) | | | | |

**Recommended method:** <!-- AGENT: Choose method with smallest total uncertainty or best-controlled systematics -->
**Justification:** <!-- AGENT: Explain recommendation -->

## Background Yield Table

<!-- AGENT: Consolidate final background estimates using recommended method per process. -->

### Yield Summary

| Process | Region | Estimated Yield | Stat Unc | Method Unc | Total Unc | Method |
|---------|--------|----------------|----------|------------|-----------|--------|

## Summary and Recommendations

<!-- AGENT: Summarize background estimation status and recommendations. -->

### Validation Status

| Check | Requirement | Status |
|-------|-------------|--------|
| CR purity (all) | > 50% | |
| Data/MC agreement (all CRs) | chi2/ndf < 2.0 | |
| VR defined (all major bkg) | 1 per major background | |
| Method comparison complete | MC vs data-driven | |

### Key Findings

<!-- AGENT: 3-5 bullet points summarizing most important findings for lead analyst. -->

### Recommendations for Wave 2 Summary

<!-- AGENT: Flag issues, concerns, or recommendations for the lead analyst. Note any backgrounds with marginal purity or poor data/MC agreement. -->
