# Analysis Strategy: {{signal_process}}

**Experiment:** {{experiment_name}}
**Collider:** {{collider}}
**Centre-of-mass energy:** {{sqrt_s}} GeV
**Date:** {{date}}

---

## Executive Summary

<!-- LEAD_ANALYST: Write a 1-paragraph summary of the analysis: what is being measured/searched for, the key experimental approach, and the expected sensitivity. -->

{{executive_summary}}

## Signal Process

<!-- LEAD_ANALYST: Describe the signal process, production mechanism, decay chain, and final state topology. Reference Feynman diagram if applicable. -->

**Process:** {{signal_process}}

**Final state:** {{final_state}}

**Production mechanism:** {{production_mechanism}}

**Reference cross-section:** {{reference_cross_section}}

## Backgrounds

<!-- LEAD_ANALYST: List all expected backgrounds, ordered by expected relative yield. Infer from the signal final state and experiment context. Include both irreducible and reducible backgrounds. -->

| Background | Process | Expected Relative Yield | Estimation Method |
|-----------|---------|------------------------|-------------------|
| {{background_1}} | | | |
| {{background_2}} | | | |
| {{background_3}} | | | |

## Dataset and Luminosity

**Available samples:**

{{available_samples}}

**Integrated luminosity:** {{luminosity}}

**MC generators:** {{mc_generators}}

## Object Definitions

Objects are loaded from the experiment context (`{{experiment_name}}`).

{{object_definitions}}

<!-- LEAD_ANALYST: Note any analysis-specific object overrides needed beyond the experiment defaults. -->

**Analysis-specific overrides:** {{object_overrides}}

## Blinding Protocol

<!-- LEAD_ANALYST: Define the blinding variable, signal region boundaries, and staged unblinding plan. The blinding variable should be chosen to prevent bias in the final result. -->

**Blinding variable:** {{blinding_variable}}

**Signal region definition:** {{signal_region_definition}}

**Staged unblinding plan:**
1. N-1 distributions in control regions (fully blinded)
2. Partial unblinding: 10% random subset of SR data
3. Full unblinding after pre-unblinding checklist complete

## Event Selection Strategy

<!-- LEAD_ANALYST: Define the preselection approach, key discriminating variables, and MVA strategy. Base selections on experiment object definitions. -->

**Preselection:** {{preselection}}

**Key discriminating variables:** {{discriminating_variables}}

**MVA approach:** {{mva_approach}}

## Categorization Plan

<!-- LEAD_ANALYST: Define event categorization strategy. Mark as "inclusive" if no categorization is needed, otherwise define categories and their purpose. This section is optional for simple analyses. -->

{{categorization_plan}}

## Background Estimation

<!-- LEAD_ANALYST: For each major background, specify whether MC-based or data-driven estimation will be used. Define control regions and transfer factors where applicable. -->

{{background_estimation}}

## Systematic Uncertainties

<!-- LEAD_ANALYST: List systematic uncertainty categories. Split into experimental (detector-related) and theoretical (cross-section, PDF, scale). Reference experiment performance documentation. -->

### Experimental Systematics

{{experimental_systematics}}

### Theoretical Systematics

{{theoretical_systematics}}

## Statistical Approach

<!-- LEAD_ANALYST: Define the statistical framework: CLs method, profile likelihood ratio, Asimov dataset usage, test statistic definition. -->

**Method:** {{statistical_method}}

**Test statistic:** {{test_statistic}}

**Expected outputs:** {{expected_outputs}}

## Target Sensitivity

<!-- LEAD_ANALYST: State the expected sensitivity targets (expected upper limits, discovery significance, or measurement precision). Base on existing literature or Asimov estimates. -->

{{target_sensitivity}}

## Quality Gate Criteria

Quality gates define quantitative pass/fail criteria for each wave transition. All criteria must be met before advancing to the next wave.

### Gate 0 to 1: Strategy Approval
- [ ] Physicist has reviewed and approved ANALYSIS_STRATEGY.md
- [ ] All 13 sections are complete with analysis-specific content
- [ ] Blinding protocol is defined with clear SR boundaries

### Gate 1 to 2: Foundation Complete
- [ ] Sample inventory complete: all MC and data files cataloged
- [ ] Object definitions validated against experiment documentation
- [ ] Data quality report shows no critical issues (no corrupt files, <1% duplicate events)
- [ ] Theory review identifies key references and cross-sections

### Gate 2 to 3: Selection Optimized
- [ ] Signal efficiency > {{min_signal_efficiency}} after full selection
- [ ] Background rejection achieves S/sqrt(B) > {{min_significance_estimate}}
- [ ] N-1 plots show data/MC agreement in control regions (chi2/ndf < 2.0)
- [ ] MVA training converged with no overtraining (KS test p > 0.05)

### Gate 3 to 4: Backgrounds Validated
- [ ] All major backgrounds estimated with uncertainty < 30%
- [ ] Closure tests pass in validation regions (pull < 2.0 sigma)
- [ ] Data/MC agreement in all control regions (chi2/ndf < 2.0)
- [ ] Cross-check with alternative method agrees within 2 sigma

### Gate 4 to 5: Statistical Model Ready
- [ ] All systematic uncertainties evaluated and included in model
- [ ] Expected sensitivity computed with Asimov dataset
- [ ] Fit stability verified (likelihood scan shows single minimum)
- [ ] Nuisance parameter pulls < 2.0 sigma in Asimov fit

### Gate 5 to 6: Pre-Unblinding Complete
- [ ] Pre-unblinding checklist fully satisfied
- [ ] All quality gates 1-5 documented as passed
- [ ] Partial unblinding (10%) shows no anomalies
- [ ] Physicist approval obtained for full unblinding

### Gate 6 to 7: Results Finalized
- [ ] Observed results computed and cross-checked
- [ ] Post-fit nuisance parameter pulls < 3.0 sigma
- [ ] No unexpected features in data requiring re-analysis
- [ ] Results internally consistent across categories (if applicable)
