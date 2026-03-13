---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: cross-checker
wave: 5
---

# Wave 5: Pre-Unblinding Cross-Checks

## Required Inputs

<!-- AGENT: Load artifacts from wave manifest. Required upstream:
- analysis/wave4/statmodel/workspace.json (validated workspace spec)
- analysis/wave1/ through analysis/wave4/ (wave directories for integrity check)
- BlindingManager state (must be BLINDED or PARTIALLY_UNBLINDED, not yet UNBLINDED)
-->

## Signal Injection Tests

<!-- AGENT: Run signal injection tests at mu=0.5, 1.0, 2.0 using the validated workspace. These tests verify that the statistical machinery correctly recovers injected signal strengths from Asimov data. All three mu values must produce pulls < 1.0 sigma for Gate 5->6 to pass. This is a HARD gate failure criterion. -->

### Injection Test Procedure

```python
from gad.statistical.injection import SignalInjectionTester
from gad.statistical.workspace import WorkspaceBuilder

# Load validated workspace
spec = WorkspaceBuilder.load("analysis/wave4/statmodel/workspace.json")

# Run signal injection tests
tester = SignalInjectionTester(spec)
injection_results = tester.run_all(mu_values=(0.5, 1.0, 2.0))
# injection_results: {
#   "tests": [
#     {"mu_injected": 0.5, "mu_hat": float, "pull": float, "converged": bool},
#     {"mu_injected": 1.0, "mu_hat": float, "pull": float, "converged": bool},
#     {"mu_injected": 2.0, "mu_hat": float, "pull": float, "converged": bool},
#   ],
#   "all_pass": bool  # True if all |pull| < 1.0
# }
```

### Injection Results

| mu_injected | mu_hat | Pull (sigma) | Converged | Pass (|pull| < 1.0) |
|------------|-----------|-------------|-----------|---------------------|
| 0.5 | <!-- AGENT: value --> | <!-- AGENT: value --> | <!-- AGENT: yes/no --> | |
| 1.0 | <!-- AGENT: value --> | <!-- AGENT: value --> | <!-- AGENT: yes/no --> | |
| 2.0 | <!-- AGENT: value --> | <!-- AGENT: value --> | <!-- AGENT: yes/no --> | |

- **All tests pass:** <!-- AGENT: yes/no -->
- **Maximum |pull|:** <!-- AGENT: value -->

<!-- AGENT: If any test fails (|pull| >= 1.0 or not converged), this is a HARD gate failure. Document the failure and recommend investigation before proceeding. -->

## Blinding Integrity Verification

<!-- AGENT: Verify that no signal region data has leaked into any analysis output. Run all integrity checks across wave directories 1-4. All checks must pass for Gate 5->6. -->

### Integrity Check Procedure

```python
from gad.blinding.integrity import BlindingIntegrityChecker

# Run all integrity checks
checker = BlindingIntegrityChecker(".")
integrity_results = checker.run_all(
    wave_dirs=["analysis/wave1", "analysis/wave2", "analysis/wave3", "analysis/wave4"]
)
# integrity_results: {
#   "checks": [
#     {"check": "sr_plots_empty", "passes": bool, "details": str},
#     {"check": "no_sr_yields_in_outputs", "passes": bool, "details": str},
#     {"check": "git_history_clean", "passes": bool, "details": str},
#   ],
#   "all_pass": bool
# }
```

### Integrity Results

| Check | Description | Status | Details |
|-------|-------------|--------|---------|
| SR plots empty | No signal region data plots in `plots/signal_region/` | <!-- AGENT: PASS/FAIL --> | <!-- AGENT: details --> |
| No SR yields in outputs | No signal region observed yields in wave outputs | <!-- AGENT: PASS/FAIL --> | <!-- AGENT: details --> |
| Git history clean | No signal region data committed to repository | <!-- AGENT: PASS/FAIL --> | <!-- AGENT: details --> |

- **All integrity checks pass:** <!-- AGENT: yes/no -->

## Checklist Update

<!-- AGENT: Update the blinding integrity checklist item based on integrity check results. -->

```python
from gad.blinding.module import BlindingManager

bm = BlindingManager("STATE.md", "config.yaml")
bm.update_checklist("blinding_integrity_verified", integrity_results["all_pass"])
```

## Output Artifacts

| Artifact | Path |
|----------|------|
| Injection test results | `analysis/wave5/crosscheck/injection_results.json` |
| Integrity check results | `analysis/wave5/crosscheck/integrity_results.json` |

## Summary

<!-- AGENT: Summarize cross-check findings. State whether signal injection tests all pass, blinding integrity is verified, and whether Gate 5->6 cross-check criteria are met. Flag any concerns for the lead analyst. -->
