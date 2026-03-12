---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: signal-lead
wave: 2
---

# Wave 2: Signal Lead Report

## Preselection (SLCT-01)

<!-- AGENT: Apply preselection cuts using SelectionEngine. Target signal efficiency > 80% and trivial background rejection > 90%. Report absolute and relative efficiencies for each cut. -->

### Preselection Cuts Applied

| Cut | Variable | Operator | Threshold | Signal Eff (abs) | Signal Eff (rel) | Background Rej (abs) |
|-----|----------|----------|-----------|-------------------|-------------------|----------------------|

### Preselection Performance

<!-- AGENT: Compare achieved signal efficiency and background rejection to targets. If targets not met, document tradeoff decision. -->

- **Signal efficiency (target > 80%):**
- **Trivial background rejection (target > 90%):**
- **Assessment:**

```python
from gad.selection import SelectionEngine, format_cutflow_table
from gad.data import create_reader

reader = create_reader("analysis_config.yaml", "STATE.md")
signal = reader.load_sample("signal")

engine = SelectionEngine("preselection")
engine.add_cut("n_charged", "n_charged", ">=", 5)
engine.add_cut("visible_energy", "visible_energy", ">", 50.0)
# AGENT: Add all preselection cuts here
selected = engine.apply(signal)
cutflow = engine.get_cutflow()
table = format_cutflow_table(cutflow)
```

## Variable Study (SLCT-02)

<!-- AGENT: Study at least 20 discriminating variables using study_variable_separation(). Rank by KS distance and ROC AUC. Include both kinematic and topological variables. -->

### Variable Rankings

| Rank | Variable | KS Distance | ROC AUC | Category |
|------|----------|-------------|---------|----------|

<!-- AGENT: Use study_variable_separation() and fill table with 20+ variables -->

```python
from gad.selection import study_variable_separation

variable_names = [
    # AGENT: List 20+ variables covering kinematic, topological, and event-shape categories
]
rankings = study_variable_separation(signal_arr, background_arr, variable_names)
# Rankings returned as list of dicts sorted by separation power
```

### Top Variables for Optimization

<!-- AGENT: Identify top 5-10 variables for optimized selection and BDT input. Justify any variables excluded despite high ranking (e.g., data/MC modeling concerns). -->

### Variable Comparison Plots

<!-- AGENT: Reference signal vs background comparison plots for top variables. Output to analysis/wave2/selection/variable_plots/ -->

```python
from gad.selection import plot_variable_comparison

for var_name in top_variables:
    plot_variable_comparison(signal_arr, background_arr, var_name,
                            f"analysis/wave2/selection/variable_plots/{var_name}.pdf")
```

## Optimized Selection (SLCT-03)

<!-- AGENT: Refine cuts beyond preselection using top-ranked variables. Report expected Asimov significance at each stage. -->

### Optimized Cut-Flow

| Stage | Cut Description | Signal Yield | Background Yield | Asimov Significance |
|-------|-----------------|--------------|------------------|---------------------|

```python
from gad.selection import asimov_significance

sig = asimov_significance(s=signal_yield, b=background_yield, sigma_b=background_uncertainty)
```

### Optimization Strategy

<!-- AGENT: Describe optimization approach (scan, iterative, simultaneous). Note any variables where BDT may replace explicit cuts. -->

## Categorization Evaluation (SLCT-05)

<!-- AGENT: Compare inclusive analysis vs categorized analysis. Use evaluate_categorization() to quantify combined significance improvement. -->

### Inclusive vs Categorized Comparison

| Configuration | Category | Signal Yield | Background Yield | Significance |
|---------------|----------|--------------|------------------|--------------|
| Inclusive      | --       |              |                  |              |
| Categorized    | Cat 1    |              |                  |              |
| Categorized    | Cat 2    |              |                  |              |
| Categorized    | Combined |              |                  |              |

<!-- AGENT: Use evaluate_categorization() to compute combined significance -->

```python
from gad.mva import evaluate_categorization

result = evaluate_categorization(
    yields_inclusive={"signal": 0.0, "background": 0.0},
    yields_categorized=[
        {"signal": 0.0, "background": 0.0},
        {"signal": 0.0, "background": 0.0},
    ]
)
# result contains: combined_significance, improvement_fraction, per_category_significance
```

### Categorization Recommendation

<!-- AGENT: Recommend inclusive or categorized based on significance improvement. Note if improvement is marginal (< 5%) and inclusive preferred for simplicity. -->

## Shape vs Counting (SLCT-06)

<!-- AGENT: Compare shape-based (binned template fit) vs counting-based (single bin) approaches. Note: this comparison is stat-only; systematic uncertainties may change the conclusion. -->

### Shape vs Counting Comparison

| Approach | Expected Significance (stat-only) | Notes |
|----------|-----------------------------------|-------|
| Shape    |                                   |       |
| Counting |                                   |       |

```python
from gad.mva import compare_shape_vs_counting

comparison = compare_shape_vs_counting(
    shape_significance=0.0,
    counting_significance=0.0
)
# comparison contains: preferred, improvement_fraction, caveat
```

### Shape vs Counting Recommendation

<!-- AGENT: Recommend approach with justification. Explicitly note stat-only caveat: full comparison requires Phase 4 systematic evaluation. -->

## Cut-Flow Table (SLCT-09)

<!-- AGENT: Produce the final cut-flow table with ALL samples (signal and each background). Include absolute efficiency, relative efficiency, and weighted yields. This is a key deliverable. -->

### Final Cut-Flow

| Cut | Signal | Signal Eff (rel) | Background 1 | Bkg1 Eff (rel) | Background 2 | Bkg2 Eff (rel) | ... |
|-----|--------|-------------------|---------------|-----------------|---------------|-----------------|-----|

<!-- AGENT: Use format_cutflow_table() with all samples to produce complete table -->

## N-1 Plots (SLCT-09)

<!-- AGENT: Produce one N-1 plot per cut variable. Each plot shows the variable distribution after applying all cuts EXCEPT the one being studied, with the cut value indicated by a vertical line. -->

### N-1 Plot List

| Variable | Cut Value | Output Path |
|----------|-----------|-------------|

```python
from gad.selection import plot_n_minus_1

for cut_index in range(len(engine.cuts)):
    plot_n_minus_1(events_dict, engine, cut_index,
                   f"analysis/wave2/selection/n_minus_1/{engine.cuts[cut_index]['name']}.pdf")
```

## Signal Acceptance x Efficiency

<!-- AGENT: Compute signal acceptance x efficiency for each energy point or signal mass point. This quantifies the analysis reach per production mode. -->

| Energy Point [GeV] | Generated Events | Events After Selection | Acceptance x Efficiency |
|---------------------|------------------|------------------------|--------------------------|

## Binned Templates (SLCT-09)

<!-- AGENT: Produce binned template histograms for the final discriminant variable (BDT score or key kinematic variable). These templates are the Phase 4 input for pyhf statistical model. -->

### Template Configuration

<!-- AGENT: Specify binning strategy (uniform, variable-width, optimized), number of bins, range. -->

```python
from gad.selection import create_binned_template

template = create_binned_template(
    values=bdt_scores,
    weights=event_weights,
    bins=20,
    range=(0.0, 1.0),
    strategy="uniform"
)
# template contains: bin_edges, yields, errors (for pyhf consumption)
```

### Template Summary

| Sample | Total Yield | Bins | Output Path |
|--------|-------------|------|-------------|

## Summary and Recommendations

<!-- AGENT: Summarize key findings and recommendations for lead analyst consolidation. -->

### Key Numbers

- **Preselection signal efficiency:**
- **Optimized selection Asimov significance:**
- **Variables studied:**
- **Categorization improvement:**
- **Preferred approach (shape/counting):**

### Recommendations for Wave 2 Summary

<!-- AGENT: Flag issues, concerns, or recommendations for the lead analyst. -->
