---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 5
---

# Wave 5 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 5 outcomes. Summarize pre-unblinding review status: note sections 1-8, signal injection tests, blinding integrity verification, and unblinding checklist completion. State whether the analysis is ready for unblinding. -->

## Wave 5 Overview

### Agents and Deliverables

| Agent | Deliverables Produced | Status |
|-------|----------------------|--------|
| Note Writer | Analysis note sections 1-8, Appendix A (partial) | |
| Cross-Checker | Signal injection tests, blinding integrity verification | |

## Unblinding Checklist Evaluation

<!-- AGENT: For each checklist item, verify the condition is met by examining upstream wave outputs. Update BlindingManager with the result. ALL 7 items must be True for unblinding to proceed. -->

### Checklist Completion

```python
from gad.blinding.module import BlindingManager

bm = BlindingManager("STATE.md", "config.yaml")

# Each item maps to a machine-checkable condition
bm.update_checklist("background_validated", gate_3_4_passed)
bm.update_checklist("systematics_complete", gate_4_5_passed)
bm.update_checklist("stat_model_built", workspace_exists_and_valid)
bm.update_checklist("cross_checks_pass", crosscheck_agreement)
bm.update_checklist("note_drafted", sections_1_8_exist)
bm.update_checklist("sensitivity_understood", expected_limit_computed)
# blinding_integrity_verified already set by cross-checker

checklist = bm._read_checklist()
```

### Checklist Status

| Item | Condition | Source | Status |
|------|-----------|--------|--------|
| background_validated | Gate 3->4 passed | Wave 3 summary | <!-- AGENT: True/False --> |
| systematics_complete | Gate 4->5 passed | Wave 4 summary | <!-- AGENT: True/False --> |
| stat_model_built | Workspace exists and Asimov validates | Wave 4 fitter report | <!-- AGENT: True/False --> |
| cross_checks_pass | Cut-flow < 1%, background pull < 1 sigma | Wave 3 cross-checker | <!-- AGENT: True/False --> |
| note_drafted | Sections 1-8 .tex files exist with content | Wave 5 note writer | <!-- AGENT: True/False --> |
| sensitivity_understood | Expected limit computed and finite | Wave 4 fitter report | <!-- AGENT: True/False --> |
| blinding_integrity_verified | All integrity checks pass | Wave 5 cross-checker | <!-- AGENT: True/False --> |

- **Checklist items True:** <!-- AGENT: N --> / 7
- **All items True:** <!-- AGENT: yes/no -->

## Analysis Note Status

<!-- AGENT: Summarize which note sections are complete and their quality. Flag any sections that need revision. -->

### Section Completeness

| Section | File | Has Content | Quality |
|---------|------|-------------|---------|
| 1. Introduction | section_01_introduction.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 2. Dataset | section_02_dataset.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 3. Objects | section_03_objects.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 4. Selection | section_04_selection.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 5. Background | section_05_background.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 6. Systematics | section_06_systematics.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 7. Stat Model | section_07_statmodel.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| 8. Expected | section_08_expected.tex | <!-- AGENT: yes/no --> | <!-- AGENT: assessment --> |
| App A. Blinding | appendix_a_blinding.tex | <!-- AGENT: yes/no --> | <!-- AGENT: partial --> |

## Signal Injection Test Summary

<!-- AGENT: Consolidate from cross-checker report. -->

| mu_injected | mu_fitted | Pull (sigma) | Pass |
|------------|-----------|-------------|------|
| 0.5 | | | |
| 1.0 | | | |
| 2.0 | | | |

- **All injection tests pass:** <!-- AGENT: yes/no -->

## Blinding Integrity Summary

<!-- AGENT: Consolidate from cross-checker report. -->

| Check | Status |
|-------|--------|
| SR plots empty | |
| No SR yields in outputs | |
| Git history clean | |

- **All integrity checks pass:** <!-- AGENT: yes/no -->

## Outstanding Issues

<!-- AGENT: List any unresolved issues, concerns, or items requiring attention before unblinding. -->

1.
2.
3.

## Gate 5->6 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Gate 5->6 criterion. All criteria must pass for Wave 6 (unblinding) to proceed. -->

| Criterion | Requirement | Value | Status |
|-----------|-------------|-------|--------|
| Signal injection tests | All 3 mu values: \|pull\| < 1.0 sigma | <!-- AGENT: max pull --> | <!-- AGENT: PASS/FAIL --> |
| Blinding integrity | All checks pass (SR plots empty, no SR yields, no git SR data) | <!-- AGENT: all_pass --> | <!-- AGENT: PASS/FAIL --> |
| Unblinding checklist | All 7 items True | <!-- AGENT: N/7 --> | <!-- AGENT: PASS/FAIL --> |
| Note sections 1-8 | All .tex files exist with content | <!-- AGENT: N/8 --> | <!-- AGENT: PASS/FAIL --> |
| Cross-checker injection agreement | Results reproducible | <!-- AGENT: yes/no --> | <!-- AGENT: PASS/FAIL --> |

### Gate Counts

- **Criteria passing:** <!-- AGENT: N --> / 5
- **Criteria failing:** <!-- AGENT: N --> / 5

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions required before proceeding to Wave 6. Signal injection test failure is a HARD gate -- must be resolved before any other criteria are considered. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->

## Wave 6 Recommendations

<!-- AGENT: Specific guidance for Wave 6 (unblinding) based on Wave 5 findings. -->

### Pre-Unblinding Reminders

- Verify BlindingManager state transition to UNBLINDED before accessing SR data
- All checklist items must remain True throughout Wave 6
- If any post-unblinding anomaly triggers Category B classification, re-blinding will occur

### Known Risks

<!-- AGENT: Document any known risks that could affect the unblinding result based on Waves 1-5 findings (e.g., large systematic uncertainties, marginal GoF, strongly constrained NPs, data/MC tensions in adjacent regions). -->
