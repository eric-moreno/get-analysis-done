---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: ml-specialist
wave: 2
---

# Wave 2: ML Specialist Report

## Feature Selection

<!-- AGENT: List input features for BDT training. Start from signal lead's top-ranked variables. Document any additions (e.g., derived variables) or removals (e.g., poorly modeled variables) with justification. -->

### Input Features

| Feature | Source | Separation Rank | Notes |
|---------|--------|-----------------|-------|

### Feature Modifications

<!-- AGENT: Document any changes from signal lead's recommended variable list. -->

## Training Configuration

<!-- AGENT: Document the full training setup for reproducibility. -->

### Hyperparameter Search Space

| Parameter | Range | Scale |
|-----------|-------|-------|
| max_depth | [3, 10] | int |
| learning_rate | [0.01, 0.3] | log |
| n_estimators | [100, 1000] | int |
| min_child_weight | [1, 10] | int |
| subsample | [0.6, 1.0] | uniform |
| colsample_bytree | [0.6, 1.0] | uniform |
| gamma | [0, 5] | uniform |

### Training Setup

- **Optimizer:** Optuna (n_trials)
- **n_trials:**
- **Random seed:** 42
- **Train/test split:** 80/20 stratified
- **Objective:** binary:logistic
- **Metric:** AUC
- **Sample weights:** Applied (signal reweighted to match background sum)

```python
from gad.mva import BDTTrainer
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

trainer = BDTTrainer(n_trials=100, random_state=42)
result = trainer.train(X, y, sample_weight=weights)
model = result["model"]
```

## Optimization Results

<!-- AGENT: Report best hyperparameters found by Optuna. Include convergence behavior. -->

### Best Hyperparameters

| Parameter | Value |
|-----------|-------|

### Optimization Summary

- **Best AUC:**
- **Trials completed:**
- **Convergence:** <!-- AGENT: Note whether optimization converged or if more trials would help -->
- **Optuna study log:** `analysis/wave2/mva/optuna_study.log`

## Overtraining Test

<!-- AGENT: Apply KS test between train and test BDT score distributions for signal and background separately. Both must pass for the model to be valid. -->

### KS Test Results

| Class | KS Statistic | p-value | Pass (p > 0.05) |
|-------|-------------|---------|------------------|
| Signal | | | |
| Background | | | |

- **Overall passes:**

```python
from gad.mva import check_overtraining

ot = check_overtraining(model, result["X_train"], result["X_test"],
                        result["y_train"], result["y_test"])
assert ot["overall_passes"], f"Overtraining detected: {ot}"
```

### Train/Test Overlay Plots

<!-- AGENT: Reference BDT score distribution overlays for train and test samples. Output to analysis/wave2/mva/overtraining/ -->

## Feature Importance

<!-- AGENT: Rank features by gain fraction from XGBoost. Identify dominant features and any features with negligible importance that could be removed. -->

### Feature Importance Ranking

| Rank | Feature | Gain Fraction |
|------|---------|---------------|

```python
from gad.mva import get_feature_importance

importances = get_feature_importance(model, feature_names)
# Returns list of dicts: [{"feature": name, "importance": gain_fraction}, ...]
```

### Importance Analysis

<!-- AGENT: Comment on feature importance distribution. Flag if single feature dominates (> 50% gain) or if several features have negligible importance (< 1%). -->

## Systematic Robustness

<!-- AGENT: Evaluate BDT score stability under systematic variations. For each variation, compare nominal and shifted BDT score distributions. -->

### Robustness Results

| Variation | KS Statistic | Max Score Shift | Stable |
|-----------|-------------|-----------------|--------|

```python
from gad.mva import check_systematic_robustness

robustness = check_systematic_robustness(
    model, X_nominal,
    {"JES_up": X_jes_up, "JES_down": X_jes_down,
     "btag_up": X_btag_up, "btag_down": X_btag_down},
    feature_names
)
# robustness contains per-variation: ks_stat, max_shift, is_stable
```

### Robustness Assessment

<!-- AGENT: Summarize robustness findings. Flag any variations causing significant BDT score shifts (KS > 0.1 or max_shift > 0.05). -->

## BDT Score Distributions

<!-- AGENT: Reference signal and background BDT score distributions with train/test overlays. Output to analysis/wave2/mva/ -->

### Distribution Plots

- Signal train/test overlay: `analysis/wave2/mva/bdt_score_signal.pdf`
- Background train/test overlay: `analysis/wave2/mva/bdt_score_background.pdf`
- Signal vs background comparison: `analysis/wave2/mva/bdt_score_comparison.pdf`

## ROC Curve

<!-- AGENT: Report ROC AUC and compare to cut-based selection performance from signal lead. -->

### ROC Performance

- **BDT AUC:**
- **Cut-based equivalent AUC:** <!-- AGENT: From signal lead's optimized selection -->
- **Improvement:**

### ROC Plot

- ROC curve: `analysis/wave2/mva/roc_curve.pdf`

## Summary and Recommendations

<!-- AGENT: Summarize BDT performance and validation status. -->

### Model Status

- **Trained:** Yes/No
- **Overtraining test:** PASS/FAIL
- **Systematic robustness:** PASS/FAIL
- **Recommended for use:** Yes/No

### Key Findings

<!-- AGENT: 3-5 bullet points summarizing most important findings for lead analyst. -->

### Recommendations for Wave 2 Summary

<!-- AGENT: Flag issues, concerns, or recommendations for the lead analyst. Note any CRITICAL issues (xgboost version pinning, sample weight handling, test set size). -->

**CRITICAL Notes:**
- Pin xgboost==2.1.4 (Python 3.9 compatibility)
- Always pass sample_weight to trainer
- Ensure test set > 1000 events per class for reliable KS test
