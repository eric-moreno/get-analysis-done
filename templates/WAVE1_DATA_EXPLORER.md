---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: data-explorer
wave: 1
---

# Wave 1: Data Explorer Report

## Sample Inventory

<!-- AGENT: Create a complete inventory of all data and MC samples. Use DataReader and analysis config to enumerate samples. -->

| Sample Name | Type | Events | Cross-Section [pb] | Luminosity [pb^-1] | Path |
|-------------|------|--------|---------------------|---------------------|------|

### Sample Notes

<!-- AGENT: Document any issues found during inventory: missing files, unexpected event counts, samples listed in config but not on disk, etc. -->

## Luminosity Cross-Check

<!-- AGENT: Compare the luminosity stated in the analysis config against any independent calculation (e.g., sum of run luminosities, luminosity database). Flag any discrepancy. -->

| Source | Luminosity [pb^-1] | Notes |
|--------|---------------------|-------|
| Config | | |
| Calculated | | |

### Discrepancy Flag

<!-- AGENT: If discrepancy > 1%, flag as WARNING. If > 5%, flag as BLOCKER. Document resolution. -->

**Status:** <!-- AGENT: OK / WARNING / BLOCKER -->

## Data Quality Report

<!-- AGENT: Run DataQualityScan on all sample files. Summarize findings. -->

### File Integrity

<!-- AGENT: Report on file accessibility, readability, and corruption status. -->

| File | Status | Size | Events | Notes |
|------|--------|------|--------|-------|

### Event Counts

<!-- AGENT: Compare expected vs actual event counts per sample. Flag discrepancies. -->

### Branch Consistency

<!-- AGENT: Verify all expected branches exist across all files in each sample. Report any missing or extra branches. -->

### NaN/Inf Statistics

<!-- AGENT: Report fraction of NaN and Inf values per branch. Flag branches with > 0.1% problematic values. -->

| Branch | NaN Fraction | Inf Fraction | Status |
|--------|--------------|--------------|--------|

### Duplicate Events

<!-- AGENT: Report results of duplicate event detection. Use event ID branch if available, hash-based comparison otherwise. -->

## Variable Catalog

<!-- AGENT: Run scan_variable_inventory on a representative file. Produce a complete branch listing. -->

| Branch Name | Type | Min | Max | Mean | Fill Fraction | Jagged |
|-------------|------|-----|-----|------|---------------|--------|

### Variable Notes

<!-- AGENT: Flag variables with unusual distributions, low fill fractions, or potential usefulness for event selection. -->

## Pre-filtered Data Assessment

<!-- AGENT: Check whether upstream cuts have been applied to the data files (e.g., "aftercut" files). Document which cuts are pre-applied. This affects what selections the analysis can vary. -->

### Upstream Cuts Detected

<!-- AGENT: List any pre-applied selections with evidence (e.g., variable distributions truncated, file naming conventions, metadata). -->

### Impact on Analysis

<!-- AGENT: Assess how pre-filtering affects the analysis strategy. Note any selections that cannot be loosened. -->

## Warnings and Blockers

### Blockers

<!-- AGENT: Issues that prevent proceeding to Wave 2. Must be resolved before gate passage. -->

### Warnings

<!-- AGENT: Issues that should be noted but do not block progress. May affect systematic uncertainties or analysis choices. -->

### Information

<!-- AGENT: Observations that may be useful for downstream agents but are not issues. -->
