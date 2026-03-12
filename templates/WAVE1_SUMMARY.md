---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: lead-analyst
wave: 1
---

# Wave 1 Summary

## Executive Summary

<!-- AGENT: Write a 1-paragraph overview of Wave 1 findings. Summarize the state of theory context, data quality, and object definitions. Highlight any critical issues or notable findings. -->

## Finalized Object Definitions

<!-- AGENT: Consolidate object definitions from the detector specialist report. Apply any lead analyst modifications. This is the authoritative object definition list for all downstream waves. -->

### Tracks

<!-- AGENT: Copy from detector specialist report with any modifications. Note the source and any changes. -->

### Jets

<!-- AGENT: Copy from detector specialist report with any modifications. -->

### Leptons

<!-- AGENT: Copy from detector specialist report with any modifications. -->

### Neutrals

<!-- AGENT: Copy from detector specialist report with any modifications. -->

### Modifications from Detector Specialist Defaults

<!-- AGENT: Document any changes the lead analyst made to the detector specialist's recommendations, with justification. -->

## Finalized MC Sample List

<!-- AGENT: Consolidate from data explorer inventory, with theory scout cross-section updates. This is the authoritative sample list for all downstream waves. -->

| Sample Name | Type | Events | Cross-Section [pb] | Luminosity [pb^-1] | Status |
|-------------|------|--------|---------------------|---------------------|--------|

### Cross-Section Updates

<!-- AGENT: Note any cross-section values updated from theory scout recommendations vs data explorer inventory values. -->

## Cross-Check Notes

<!-- AGENT: Document discrepancies between the three specialist reports and how they were resolved. -->

### Theory vs Data Discrepancies

<!-- AGENT: Any conflicts between theory scout predictions and data explorer observations. -->

### Object Definition Consistency

<!-- AGENT: Any issues with object definitions vs available data branches or MC truth information. -->

### Resolution Decisions

<!-- AGENT: For each discrepancy, document the resolution and rationale. -->

## Data Quality Summary

<!-- AGENT: Key findings from data explorer report. Highlight blockers, warnings, and their resolution status. -->

### Blockers Resolved

<!-- AGENT: List blockers from data explorer report and how they were resolved. If unresolved, gate fails. -->

### Active Warnings

<!-- AGENT: List warnings carried forward to Wave 2. These may affect systematic uncertainties. -->

## Theory Context

<!-- AGENT: Key findings from theory scout report relevant for analysis strategy. -->

### Signal Model Summary

<!-- AGENT: Brief summary of signal process, cross-sections, and theoretical uncertainties. -->

### Existing Limits Impact

<!-- AGENT: How existing limits inform the analysis strategy (target sensitivity, phase space focus). -->

## Wave 2 Recommendations

<!-- AGENT: Specific guidance for the event selection wave based on Wave 1 findings. -->

### Preselection Strategy

<!-- AGENT: Recommended preselection cuts based on object definitions and data characteristics. -->

### Promising Variables

<!-- AGENT: Variables identified as potentially discriminating, from theory scout and data explorer reports. -->

### Categorization Hints

<!-- AGENT: Suggested event categories based on signal topology, detector acceptance, or energy points. -->

### Potential Pitfalls

<!-- AGENT: Issues to watch for in Wave 2 based on Wave 1 findings. -->

## Gate 1->2 Evaluation

<!-- AGENT: Quantitative pass/fail assessment for each Wave 1 quality gate criterion. All criteria must pass for Wave 2 to proceed. -->

| Criterion | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| Object definitions finalized | All object types defined with cuts | | |
| MC sample list complete | All samples inventoried with cross-sections | | |
| Data quality acceptable | No unresolved blockers | | |
| Theory context documented | Signal model and existing limits compiled | | |
| Luminosity validated | Cross-check within tolerance | | |

### Gate Decision

<!-- AGENT: PASS or FAIL with summary justification. If FAIL, list specific remediation actions. -->

**Decision:** <!-- AGENT: PASS / FAIL -->
**Justification:** <!-- AGENT: 1-2 sentence summary -->
