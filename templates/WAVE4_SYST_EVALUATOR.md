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
    nominal_template=nominal, up_weights=btag_up, down_weights=btag_down,
    values=obs_values, bin_edges=edges
)
modifier = evaluator.make_modifier("btag_sf", result)
# result: {"up_yields": [...], "down_yields": [...], "nominal_yields": [...], "type": "histosys"}

# Normalization-only systematic (e.g., luminosity)
result = evaluator.evaluate_normalization(
    nominal_yield=1000, up_scale=1.023, down_scale=0.977
)
modifier = evaluator.make_modifier("lumi", result)
# result: {"type": "normsys", "hi": 1.023, "lo": 0.977}
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
    nominal_template=nominal, up_template=isr_up, down_template=isr_down
)
modifier = evaluator.make_modifier("isr_qqbar", result)
# result: {"up_yields": [...], "down_yields": [...], "nominal_yields": [...], "type": "histosys"}
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
result = pruner.prune_systematics(evaluations)
# result: {"kept": [...], "pruned": [...], "summary": {"n_total": int, "n_kept": int, "n_pruned": int, "threshold": float}}
kept = result["kept"]
pruned = result["pruned"]
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
