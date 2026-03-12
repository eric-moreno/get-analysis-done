---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: systematics-fitter
wave: 4
---

# Wave 4: Systematic Evaluator Report

## Experimental Systematics (SYST-01)

<!-- AGENT: Evaluate all experimental systematic uncertainties using up/down template pairs. Experimental systematics are correlated across all processes (shared NP name). Use SystematicEvaluator for each source. -->

### Experimental Systematic Sources

```python
from gad.systematics import SystematicEvaluator

evaluator = SystematicEvaluator()

# Weight-based systematic (e.g., b-tagging SF)
result = evaluator.evaluate_weight_variation(
    nominal_hist=nominal, up_hist=btag_up, down_hist=btag_down,
    name="btag_sf"
)
modifier = evaluator.make_modifier("btag_sf", result)
# modifier: {"name": "btag_sf", "type": "histosys", "data": {"hi_data": [...], "lo_data": [...]}}

# Normalization-only systematic (e.g., luminosity)
result = evaluator.evaluate_normalization(
    nominal_yield=1000, up_yield=1023, down_yield=977,
    name="lumi"
)
modifier = evaluator.make_modifier("lumi", result)
# modifier: {"name": "lumi", "type": "normsys", "data": {"hi": 1.023, "lo": 0.977}}
```

| Source | Type | Affected Processes | Max Fractional Effect | NP Name |
|--------|------|-------------------|----------------------|---------|
<!-- AGENT: Fill one row per experimental systematic source. NP name follows: build_modifier_name(source, correlated=True). Experimental systematics use the SAME name across all processes for correlation. -->

### Experimental Systematics Details

<!-- AGENT: For each experimental systematic, provide the up/down fractional effects per process per region. Group by source category (jet-related, b-tagging, lepton ID, luminosity/beam). -->

#### Jet-Related Systematics

| Source | Process | Region | Up Effect (%) | Down Effect (%) |
|--------|---------|--------|---------------|-----------------|
<!-- AGENT: Fill for JES, JER, etc. -->

#### B-Tagging Systematics

| Source | Process | Region | Up Effect (%) | Down Effect (%) |
|--------|---------|--------|---------------|-----------------|
<!-- AGENT: Fill for b-tag SF variations. -->

#### Lepton/Tracking Systematics

| Source | Process | Region | Up Effect (%) | Down Effect (%) |
|--------|---------|--------|---------------|-----------------|
<!-- AGENT: Fill for lepton ID, tracking efficiency, etc. -->

#### Luminosity/Beam Systematics

| Source | Process | Region | Up Effect (%) | Down Effect (%) |
|--------|---------|--------|---------------|-----------------|
<!-- AGENT: Fill for luminosity uncertainty, beam energy, etc. -->

## Theory/Modelling Systematics (SYST-02)

<!-- AGENT: Evaluate theory and modelling systematic uncertainties. Theory systematics are UNCORRELATED across different physics processes (process-specific NP name). Use SystematicEvaluator for each source. -->

### Theory Systematic Sources

```python
# Shape-based systematic (e.g., ISR variation)
result = evaluator.evaluate_shape_variation(
    nominal_hist=nominal, varied_hist=isr_up,
    name="isr", symmetrize=True
)
modifier = evaluator.make_modifier("isr_qqbar", result)
# NP name includes process: build_modifier_name("isr", process="qqbar", correlated=False)
```

| Source | Type | Affected Processes | Max Fractional Effect | NP Name Pattern |
|--------|------|-------------------|----------------------|----------------|
<!-- AGENT: Fill one row per theory systematic source. NP name follows: build_modifier_name(source, process=process, correlated=False). Theory systematics use DIFFERENT names per process for decorrelation. -->

### Theory Systematics Details

<!-- AGENT: For each theory systematic, provide the up/down fractional effects per process per region. -->

| Source | Process | Region | Up Effect (%) | Down Effect (%) | NP Name |
|--------|---------|--------|---------------|-----------------|---------|
<!-- AGENT: Fill for ISR, fragmentation, PDF, scale variations, etc. -->

## Pruning Summary

<!-- AGENT: Prune systematics with < 0.5% effect on any bin yield. Use SystematicPruner. Report number kept vs pruned. -->

### Pruning Results

```python
from gad.systematics import SystematicPruner

pruner = SystematicPruner(threshold=0.005)  # 0.5%
kept, pruned = pruner.prune(all_modifiers)
```

| Category | Total Sources | Kept | Pruned | Threshold |
|----------|--------------|------|--------|-----------|
| Experimental | | | | 0.5% |
| Theory | | | | 0.5% |
| **Total** | | | | |

### Pruned Systematics List

<!-- AGENT: List all pruned systematics with their maximum effect for documentation. -->

| Pruned Source | Max Effect (%) | Reason |
|---------------|---------------|--------|
<!-- AGENT: Fill for each pruned systematic. -->

## Summary

<!-- AGENT: Summarize systematic evaluation. List top 5 dominant systematics by impact. Note any unexpected findings. -->

### Top 5 Dominant Systematics

| Rank | Source | Type | Max Effect (%) | Notes |
|------|--------|------|---------------|-------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Key Findings

<!-- AGENT: 3-5 bullet points. Note any systematics larger than expected, any anti-correlations, or any sources requiring special treatment. -->
