# Pipeline Validation Test Specification

## ALEPH e+e- -> Zh -> bbbar End-to-End Validation

### 1. Test Overview

This specification defines the end-to-end validation test for the GAD (Generic Analysis Descriptor) pipeline. The test uses the ALEPH experiment context to execute a complete Higgs boson search in the Zh -> bbbar final state, exercising every pipeline component from physics prompt through final analysis note.

**Experiment:** ALEPH (LEP, CERN)
**Process:** e+e- -> Zh -> bbbar at sqrt(s) = 189--209 GeV
**Experiment context:** `experiments/aleph/` (detector, objects, MC generators, performance, references)
**Execution mode:** Fully autonomous via `/gad:run-analysis` (auto-approve strategy, auto-advance waves, auto-unblind)

The ALEPH Zh -> bbbar search was chosen because:
- Published results exist for quantitative comparison (ALEPH Collaboration combined Higgs search)
- The analysis exercises all 8 waves and all quality gates
- The physics is well-understood with documented signal and background processes
- The experiment context files are fully defined in `experiments/aleph/`

The validation proves the system can run hands-off from physics prompt to final analysis note PDF.

---

### 2. Physics Prompt

The exact prompt to feed `/gad:run-analysis`:

```
Search for the Higgs boson in the Zh -> bbbar final state using ALEPH data at sqrt(s) = 189-209 GeV.
Use the ALEPH experiment context from experiments/aleph/.

Signal processes:
  - e+e- -> Zh -> nu_nu bbbar (missing energy channel)
  - e+e- -> Zh -> qqbar bbbar (four-jet channel)
  - e+e- -> Zh -> l+l- bbbar (leptonic channel)

Main backgrounds:
  - e+e- -> qqbar (hadronic Z decays)
  - e+e- -> WW (W-pair production)
  - e+e- -> ZZ (Z-pair production)

Blinding variable: reconstructed Higgs candidate mass.
```

**Configuration overrides for validation:**
- `auto_approve_strategy: true` -- skip human review of analysis strategy
- `auto_advance_waves: true` -- advance through gates without human checkpoint
- `auto_unblind: true` -- proceed through unblinding without human approval
- `max_gate_retries: 2` -- allow up to 2 retries per gate failure

---

### 3. Wave-by-Wave Expected Behavior

#### Wave 0: Strategy Generation

- **Agents:** lead-analyst
- **Expected artifacts:**
  - `strategy/ANALYSIS_STRATEGY.md` -- complete strategy document
  - `gate-results/gate-0-to-1-RESULT.json` -- gate evaluation
- **Gate 0->1 criteria:**
  - Strategy document exists
  - Physics prompt coverage = 1.0 (all signal/background processes addressed)
  - Signal region defined
  - Gate criteria approved by lead analyst
- **Known limitations:** Strategy is generated from prompt + experiment context only; no data-driven tuning at this stage.

#### Wave 1: Data Exploration

- **Agents:** data-explorer, detector-specialist, theory-scout
- **Expected artifacts:**
  - `foundation/DATA_SUMMARY.md` -- dataset overview and quality
  - `foundation/DETECTOR_EFFECTS.md` -- detector response characterization
  - `foundation/LITERATURE_REVIEW.md` -- theory context and references
  - `gate-results/gate-1-to-2-RESULT.json`
- **Gate 1->2 criteria:**
  - Data summary exists with sample counts
  - Detector effects documented
  - Literature review contains references
  - Key distributions validated
- **Known limitations:** Requires actual ROOT data files at paths in ALEPH samples config. If data absent, fails here (see Section 5).

#### Wave 2: Selection and MVA

- **Agents:** signal-lead, ml-specialist, background-estimator
- **Expected artifacts:**
  - `selection/CUTFLOW.md` -- cut-by-cut efficiency table
  - `selection/REGIONS.md` -- signal/control region definitions
  - `selection/MVA_STUDY.md` -- multivariate analysis results
  - `gate-results/gate-2-to-3-RESULT.json`
- **Gate 2->3 criteria:**
  - Cutflow exists with signal efficiency > 0
  - At least 1 signal region and 1 control region defined
  - MVA discriminant evaluated
  - Background rejection documented
- **Known limitations:** MVA training depends on available statistics. With limited ALEPH data, BDT performance may be modest.

#### Wave 3: Background Validation

- **Agents:** background-estimator, cross-checker
- **Expected artifacts:**
  - `background/BACKGROUND_YIELDS.md` -- data/MC comparison in control regions
  - `background/VALIDATION_PLOTS.md` -- distribution comparisons
  - `gate-results/gate-3-to-4-RESULT.json`
- **Gate 3->4 criteria:**
  - Background yields exist for all control regions
  - Data/MC agreement within statistical uncertainties
  - Cross-checker validates yields independently
  - No significant shape discrepancies
  - Transfer factors computed
- **Known limitations:** Limited control region statistics at LEP energies.

#### Wave 4: Systematics and Statistical Model

- **Agents:** systematic-source-evaluator, systematics-fitter
- **Expected artifacts:**
  - `systematics/NP_RANKING.md` -- nuisance parameter impact ranking
  - `systematics/SYSTEMATIC_TABLE.md` -- systematic uncertainty summary
  - `fit/EXPECTED_LIMIT.md` -- expected exclusion limit (Asimov)
  - `gate-results/gate-4-to-5-RESULT.json`
- **Gate 4->5 criteria:**
  - Systematic uncertainties evaluated and ranked
  - Statistical model builds without errors
  - Expected limit computed on Asimov dataset
  - Nuisance parameter pulls within +/-2 sigma
  - Fit converges
  - Constraint analysis shows no overconstrained NPs
  - Post-fit impacts documented
- **Known limitations:** Limited number of systematic sources compared to LHC analyses. Some systematics may be unconstrained.

#### Wave 5: Pre-Unblinding Review

- **Agents:** cross-checker, note-writer
- **Expected artifacts:**
  - `note/ANALYSIS_NOTE_DRAFT.md` -- draft note with blinded results
  - `preunblinding/CHECKLIST.md` -- pre-unblinding review checklist
  - `gate-results/gate-5-to-6-RESULT.json`
- **Gate 5->6 criteria:**
  - Signal injection test passes (signal recoverable)
  - Pre-unblinding checklist items all satisfied
  - Draft note sections 1-8 populated
  - Expected limit documented
  - All systematic sources reviewed
  - Cross-checker endorses readiness
- **Known limitations:** Signal injection test sensitivity depends on expected signal yield.

#### Wave 6: Unblinding and Results

- **Agents:** systematics-fitter, cross-checker
- **Expected artifacts:**
  - `results/OBSERVED_RESULTS.md` -- observed limit and p-values
  - `results/POST_FIT_DIAGNOSTICS.md` -- post-fit checks
  - `gate-results/gate-6-to-7-RESULT.json`
- **Gate 6->7 criteria:**
  - Observed result exists
  - Cross-check agreement within 10% tolerance
  - Post-fit diagnostics complete
  - Result summary documented
- **Known limitations:** Category B discrepancy (if found) triggers re-blinding per protocol.

#### Wave 7: Documentation

- **Agents:** note-writer
- **Expected artifacts:**
  - `note/ANALYSIS_NOTE_FINAL.md` -- final note with observed results
  - `note/SUPPLEMENTARY_MATERIAL.md` -- supplementary material
- **Gate 7 completion criteria (8 checks):**
  1. PDF compiles without LaTeX errors
  2. All citations verified via INSPIRE-HEP
  3. No unfilled AGENT directives remaining
  4. All figures in PDF format
  5. Section 9 (observed results) populated
  6. Self-containedness check passes (all 8 verification items)
  7. Comparison to published results included
  8. Bibliography generated from verified citations
- **Known limitations:** INSPIRE-HEP API availability required for citation verification.

---

### 4. Pass/Fail Criteria

The pipeline validation PASSES if ALL of the following are satisfied:

| Criterion | Description | Threshold |
|-----------|-------------|-----------|
| Wave completion | All 8 waves (0--7) complete without unrecoverable gate failure | 8/8 waves |
| Gate passage | All quality gates pass (0->1 through 6->7) | 7/7 gates |
| PDF compilation | Analysis note compiles to PDF without LaTeX errors | 0 errors |
| Undefined references | No undefined LaTeX references or citations | 0 undefined |
| Citation verification | All bibliography entries verified via INSPIRE-HEP | 100% verified |
| Published comparison | Expected limit within order-of-magnitude of published ALEPH result | See below |
| Self-containedness | All `verify_self_contained` checks pass | 8/8 checks |
| Note completeness | All 9 sections + appendix present with non-trivial content | 10/10 sections |

**Published result comparison (DOCS-02):**

The ALEPH Collaboration published a combined Higgs search result:
- **Combined observed limit:** m_H > 114.4 GeV at 95% CL (combined search across all channels)
- **Reference:** "Search for the Standard Model Higgs boson at LEP", ALEPH, DELPHI, L3, OPAL (LEP Working Group), Phys. Lett. B 565 (2003) 61-75

For the single-channel Zh -> bbbar validation:
- The expected upper limit on the production cross-section should be a physically reasonable value
- "Order-of-magnitude agreement" means: the GAD-computed expected cross-section limit is within a factor of 10 of the published ALEPH single-channel sensitivity
- The observed limit (if data is available) should not be wildly inconsistent with the expected limit
- A mass limit comparison is acceptable: the expected exclusion reach should be in the range of 100--120 GeV for Zh -> bbbar alone (the combined limit of 114.4 GeV uses all channels)

**What constitutes a PASS for the comparison:**
- The computed limit is physically reasonable (positive, finite)
- The limit is within order-of-magnitude of published ALEPH sensitivity
- The comparison section in the note documents the published reference and explains any differences

**What constitutes a FAIL for the comparison:**
- The computed limit is unphysical (negative, zero, or infinite)
- The limit deviates by more than an order of magnitude without explanation
- No comparison to published results is included in the note

---

### 5. Data Requirements

**Required data files:**
The ALEPH ROOT data files must be available at the paths specified in the ALEPH samples configuration. The expected directory structure follows the experiment context defined in `experiments/aleph/`.

**If data is absent:**
- The pipeline will fail at Wave 1 (data exploration) when `DataReader` attempts to load ROOT files
- This is an EXPECTED failure mode, not a bug
- The validation test documents this requirement and the expected failure point
- Component validation tests (in `test_pipeline_validation.py`) verify structural correctness WITHOUT requiring data

**Data format expectations:**
- ROOT files with TTree structure
- Branches matching the object definitions in `experiments/aleph/objects.yaml`
- Signal and background MC samples with appropriate cross-section weights
- Data samples from sqrt(s) = 189--209 GeV running periods

---

### 6. Failure Handling

Per project convention (Claude's discretion on failure handling):

**Gate failure protocol:**
1. If a quality gate fails, the system retries up to 2 times (configured via `max_gate_retries: 2` in gate templates)
2. Each retry invokes the diagnosis agent specified in the gate template (`on_failure.diagnosis_agent`)
3. The diagnosis agent analyzes the failure, suggests fixes, and the wave re-executes
4. If the gate still fails after 2 retries, the system:
   - Documents the failure in a gate failure report (using `gate-templates/GATE_FAILURE.md`)
   - Flags the failure for investigation
   - Does NOT abort the entire validation (other components may still be testable)

**Categorization of failures:**
- **Recoverable:** Gate metric slightly below threshold, missing optional artifact, transient API error
- **Unrecoverable:** Data files absent, fundamental physics misconfiguration, compilation tool missing

**Validation test outcomes:**
- **PASS:** All 8 waves complete, all gates pass, note compiles, criteria met
- **PARTIAL PASS:** Some waves complete, failures documented and explainable (e.g., data absent)
- **FAIL:** Pipeline crashes, produces unphysical results, or fails without clear diagnosis

---

### 7. Comparison to Published Results (DOCS-02)

**Primary reference:**
- "Search for the Standard Model Higgs boson at LEP"
- LEP Working Group for Higgs Boson Searches (ALEPH, DELPHI, L3, OPAL)
- Phys. Lett. B 565 (2003) 61-75
- DOI: 10.1016/S0370-2693(03)00614-2
- INSPIRE: https://inspirehep.net/literature/620903

**Published numbers for comparison:**
| Quantity | Published Value | Source |
|----------|----------------|--------|
| Combined observed limit | m_H > 114.4 GeV at 95% CL | LEP combined, Phys. Lett. B 565 (2003) 61 |
| ALEPH single-experiment sensitivity | m_H ~ 113 GeV expected | ALEPH contribution to LEP combination |
| Zh -> bbbar branching ratio (at m_H = 115 GeV) | ~73% | Standard Model prediction |
| LEP2 integrated luminosity (ALEPH) | ~630 pb^-1 (189--209 GeV) | ALEPH data-taking summary |

**Acceptable deviation ranges:**
- Expected mass limit: 100--120 GeV for single-channel (Zh -> bbbar accounts for largest sensitivity)
- Cross-section limit: within factor of 10 of published ALEPH sensitivity at any given m_H
- CLs values: should follow expected statistical behavior (monotonic in m_H near exclusion boundary)

**What the note must contain:**
1. Table comparing GAD-computed limits to published ALEPH values
2. Discussion of differences (single channel vs. combined, simplified vs. full systematics)
3. Citation of the primary LEP Higgs search reference
4. Statement on whether the validation passes the order-of-magnitude criterion

---

### 8. Execution Checklist

Before running the validation:

- [ ] ALEPH experiment context complete (`experiments/aleph/` has all 5 YAML files)
- [ ] All 8 wave manifests present and valid (`wave-manifests/wave-{0..7}.yaml`)
- [ ] All 7 gate templates present and valid (`gate-templates/gate-{0..1}-to-{1..7}.yaml`)
- [ ] All 11 agent definitions present (`agents/gad-*.md`)
- [ ] All note section templates present (`templates/ANALYSIS_NOTE_SECTIONS/`)
- [ ] `gad.documentation` module importable (citations, plots, compiler, verification)
- [ ] ALEPH ROOT data files available (or document expected Wave 1 failure)
- [ ] LaTeX distribution available (pdflatex, bibtex)
- [ ] Python environment has required packages (pyhf, uproot, mplhep, yaml, requests)

**Automated component checks:** See `tests/python/test_pipeline_validation.py` for automated verification of items 1--6 above.
