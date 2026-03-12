---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: detector-specialist
wave: 1
---

# Wave 1: Detector Specialist Report

## Object Definitions

<!-- AGENT: For each physics object type, document the selection criteria from experiment context objects.yaml. Apply any analysis-specific overrides from config.object_overrides. -->

### Tracks

<!-- AGENT: Document charged track selection. Load from ExperimentContext.get_object_definition("good_track"). -->

| Cut Variable | Operator | Threshold | Unit | Notes |
|-------------|----------|-----------|------|-------|

- **Expected Efficiency:** <!-- AGENT: from objects.yaml metadata -->
- **Expected Fake Rate:** <!-- AGENT: from performance.yaml or published values -->

### Jets

<!-- AGENT: Document jet selection criteria. Include algorithm, radius, pT threshold. -->

| Cut Variable | Operator | Threshold | Unit | Notes |
|-------------|----------|-----------|------|-------|

- **Expected Efficiency:** <!-- AGENT: from objects.yaml metadata -->
- **Expected Fake Rate:** <!-- AGENT: from performance.yaml or published values -->

### Leptons

<!-- AGENT: Document lepton identification and isolation criteria. Separate electrons and muons if applicable. -->

| Cut Variable | Operator | Threshold | Unit | Notes |
|-------------|----------|-----------|------|-------|

- **Expected Efficiency:** <!-- AGENT: from objects.yaml metadata -->
- **Expected Fake Rate:** <!-- AGENT: from performance.yaml or published values -->

### Neutrals

<!-- AGENT: Document neutral particle (photon, neutral hadron) selection criteria. -->

| Cut Variable | Operator | Threshold | Unit | Notes |
|-------------|----------|-----------|------|-------|

- **Expected Efficiency:** <!-- AGENT: from objects.yaml metadata -->
- **Expected Fake Rate:** <!-- AGENT: from performance.yaml or published values -->

## Performance Validation

<!-- AGENT: Compare object performance metrics against published detector performance values. Flag significant deviations. -->

### Tracking Resolution

<!-- AGENT: Compare momentum resolution from performance.yaml against published values. -->

| Metric | Published Value | Context Value | Status |
|--------|----------------|---------------|--------|

### Calorimeter Resolution

<!-- AGENT: Compare energy resolution for ECAL and HCAL against published values. -->

| Subsystem | Published Resolution | Context Value | Status |
|-----------|---------------------|---------------|--------|

### B-Tag Performance

<!-- AGENT: Document b-tagging working points, efficiencies, and mistag rates. Compare to published values. -->

| Working Point | Efficiency | Mistag Rate | Published Efficiency | Published Mistag | Status |
|---------------|-----------|-------------|---------------------|-----------------|--------|

## Scale Factors

<!-- AGENT: Document data/MC correction factors per object type. For Wave 1 these may be placeholder values from published recommendations pending in-situ measurement in later waves. -->

| Object Type | Scale Factor | Uncertainty | Source | Notes |
|-------------|-------------|-------------|--------|-------|

### Scale Factor Methodology

<!-- AGENT: Describe the scale factor derivation approach planned for later waves. Note which factors are placeholders vs measured. -->

## Data/MC Comparisons

<!-- AGENT: Define key distributions to compare between data and MC in a control region. This is the validation plan for Wave 2+. -->

### Control Region Definition

<!-- AGENT: Define a suitable control region for object validation. Should be orthogonal to signal region. -->

### Planned Comparisons

<!-- AGENT: List distributions to compare, with expected level of agreement and tolerance for data/MC ratio. -->

| Distribution | Region | Expected Agreement | Tolerance |
|-------------|--------|-------------------|-----------|

## Recommendations

### Finalized Object Definitions

<!-- AGENT: Summarize the recommended object definitions for lead analyst approval. Note any modifications from default experiment context definitions. -->

### Issues Requiring Lead Analyst Decision

<!-- AGENT: Flag any object definition choices that require lead analyst input (e.g., tighter/looser working points, non-standard selections). -->

### Validation Plan for Wave 2

<!-- AGENT: Outline the data/MC comparison plan that will validate these object definitions using real data. -->
