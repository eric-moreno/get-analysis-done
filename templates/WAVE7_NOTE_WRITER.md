---
analysis: "{{ analysis_name }}"
experiment: "{{ experiment }}"
date: "{{ date }}"
agent: note-writer
wave: 7
---

# Wave 7: Final Analysis Note

## Required Inputs

<!-- AGENT: Load artifacts from wave manifest. Required upstream:
- analysis/wave1/WAVE1_SUMMARY.md (foundation: objects, samples, cross-sections)
- analysis/wave2/ (selection optimization, BDT training, signal region definition)
- analysis/wave3/ (background estimation, closure tests, data/MC agreement)
- analysis/wave4/ (systematic evaluation, workspace, expected limit, fit diagnostics)
- analysis/wave5/ (pre-unblinding note draft with sections 1-8)
- analysis/wave6/ (observed results, post-fit diagnostics, problem classification)
- analysis/wave0/ANALYSIS_STRATEGY.md (analysis strategy)
- templates/ANALYSIS_NOTE_SECTIONS/ (LaTeX section templates with AGENT directives)
- gate-results/gate-6-to-7-RESULT.json (gate result confirming results quality)
-->

## 1. Section 9 Integration (DOCS-01)

<!-- AGENT: Uncomment `\input{section_09_observed}` in main.tex ONLY now (Wave 7). Populate Section 9 from Wave 6 fitter output. This is the central physics result of the analysis. -->

### Uncomment Section 9

In `main.tex`, change the commented-out Section 9 line:
```latex
% Before:
% \input{section_09_observed}

% After:
\input{section_09_observed}
```

### Populate Section 9

Read the Wave 6 fitter report and observed results to fill `section_09_observed.tex`:

```python
import json
from pathlib import Path

# Load Wave 6 observed results
obs_results = json.load(open("analysis/wave6/results/observed_limit.json"))
postfit_yields = json.load(open("analysis/wave6/results/postfit_yields.json"))

# Key values to include in Section 9:
observed_limit = obs_results["observed_limit"]
expected_limit = obs_results["expected_limit"]  # dict with median, +/-1, +/-2 sigma
mu_hat = obs_results["mu_hat"]
brazil_band = obs_results["expected_limit"]  # -2s, -1s, median, +1s, +2s

# Post-fit diagnostics
# Read diagnostic summary from Wave 6 fitter report
```

### Section 9 Content Requirements

- **Observed 95% CL upper limit** with comparison to expected median
- **Post-fit yield table** per channel per process (pre-fit vs post-fit)
- **Post-fit diagnostic summary:** NP pull status, GoF p-value, ranking highlights
- **Brazil band plot** with observed line overlaid on expected +/- 1, 2 sigma bands
- **Interpretation:** Is the observed limit within the expected band? Any excess or deficit?

## 2. Abstract and Introduction Update (DOCS-01)

<!-- AGENT: After Section 9 is populated, update the abstract and introduction for consistency with observed results. The same limit value must appear identically everywhere. -->

### Abstract Update

Update the abstract in `main.tex` to include:
- The observed 95% CL upper limit value (same number as in Section 9)
- Brief statement of consistency with expected sensitivity (or excess/deficit if applicable)
- Use `\siunitx` formatting for consistent number presentation

### Introduction Update (Section 1)

Update `section_01_introduction.tex` to include:
- A result summary paragraph at the end of the introduction
- Reference to Section 9 for full observed results
- Ensure cross-references to Section 9 resolve correctly

### Consistency Pass

After updating abstract and introduction, verify all quoted values match:
- Observed limit value: same in abstract, introduction, Section 8 expected comparison, Section 9
- Expected limit value: same in Section 8 and Section 9 comparison table
- All cross-references (`\ref{...}`, `\cite{...}`) resolve

## 3. Publication-Quality Plot Regeneration (DOCS-03)

<!-- AGENT: Regenerate ALL plots fresh with uniform mplhep experiment-specific styling. Do NOT collect plots from earlier waves -- regenerate from source data for consistent styling. All figures must be PDF vector format. -->

### Plotting Setup

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
try:
    import mplhep
    style = getattr(mplhep.style, experiment_style, None)
    if style is not None:
        plt.style.use(style)
except (ImportError, AttributeError):
    pass
# Save all figures as PDF: fig.savefig("figures/plot_name.pdf", bbox_inches="tight")
```

### Required Plots

Regenerate all of the following as PDF vector format in `analysis/wave7/note/figures/`:

| Plot | Source Module | Description |
|------|-------------|-------------|
| Cut-flow visualization | `gad.selection` | Event yields after each selection step |
| N-1 plots | `gad.selection.plots` | Signal/background distributions with one cut removed |
| BDT score distribution | `gad.mva` | Signal vs background BDT output |
| BDT ROC curve | `gad.mva` | Receiver operating characteristic for BDT |
| Data/MC in CRs | `gad.regions` | Control region agreement plots |
| Data/MC in VRs | `gad.regions` | Validation region agreement plots |
| NP pull plot | `gad.statistical.diagnostics` | Post-fit nuisance parameter pulls (observed) |
| NP ranking plot | `gad.statistical.diagnostics` | Top NPs ranked by impact on mu (observed) |
| Correlation matrix | `gad.statistical.diagnostics` | NP correlation heatmap (observed) |
| GoF distribution | `gad.statistical.diagnostics` | Goodness-of-fit test statistic distribution |
| Likelihood scan | `gad.statistical.diagnostics` | Profile likelihood scan for mu |
| Brazil band | `gad.statistical.fitter` | Expected + observed 95% CL limit (observed line added) |
| Post-fit yield comparison | `gad.statistical` | Pre-fit vs post-fit yields per channel |
| Constraint analysis | `gad.statistical.diagnostics` | Pre-fit vs post-fit NP uncertainties |

### Styling Requirements

- All plots use mplhep experiment-specific style with graceful fallback
- Uniform font sizes, axis labels, and legend placement across all figures
- Descriptive axis labels with units where applicable
- Legend entries clearly distinguishing signal, backgrounds, and data
- All figures saved as `figures/<name>.pdf` (vector format for LaTeX)

## 4. Comparison to Previous Published Results (DOCS-02)

<!-- AGENT: Include comparison to published results from theory scout literature review and ALEPH references.yaml. Claude's discretion on format: overlay on Brazil band, dedicated comparison table + plot, or both. Must reference published results explicitly. -->

### Published Results Comparison

Compare observed results to previously published results:

1. **Source data:** Read published limits from:
   - Theory scout literature review (`analysis/wave1/LITERATURE_REVIEW.md`)
   - Experiment context references (`experiments/<experiment>/references.yaml`)

2. **Comparison methodology:**
   - Extract published upper limit values and their conditions (luminosity, energy, channel)
   - Scale or annotate for differences in analysis conditions where applicable
   - Present both this analysis result and published results clearly

3. **Presentation format** (Claude's discretion, choose one or more):
   - Overlay published result markers on the Brazil band plot
   - Dedicated comparison table: this analysis vs published results with conditions
   - Dedicated comparison plot: side-by-side or overlay visualization

4. **Content requirements:**
   - Explicit mention of "published" results and source references
   - "Comparison" methodology explanation
   - Discussion of consistency or improvements relative to published results
   - Proper citations for all referenced published analyses

## 5. Bibliography Generation (DOCS-01)

<!-- AGENT: Auto-generate references.bib from all wave reports. Collect citations from theory scout literature review, experiment context references.yaml, and any published results referenced in the note. Use BibTeX format. -->

### Citation Collection

```python
import re
from pathlib import Path

# Collect all citations from wave reports
all_citations = []

# 1. Theory scout literature review
lit_review = Path("analysis/wave1/LITERATURE_REVIEW.md").read_text()
# Extract reference entries (DOIs, arXiv IDs, INSPIRE URLs)

# 2. Experiment context references
import yaml
refs_yaml = yaml.safe_load(Path("experiments/{experiment}/references.yaml").read_text())
for ref in refs_yaml.get("references", []):
    all_citations.append(ref)

# 3. Published results used in comparison
# Extract from comparison section sources

# 4. Analysis methodology references (CLs, HistFactory, pyhf)
# Standard HEP methodology citations
```

### BibTeX File Generation

- Write `analysis/wave7/note/references.bib` with all collected entries
- Use standard BibTeX `@article{}`, `@techreport{}`, `@inproceedings{}` entry types
- Include DOI, arXiv eprint, and INSPIRE URL fields where available
- Ensure BibTeX keys are unique and descriptive (e.g., `ALEPH:2006zh`, `Cowan:2010js`)

### Citation Verification (Cross-Checker)

After bibliography generation, the cross-checker agent independently verifies every entry via INSPIRE-HEP API. See `agents/gad-cross-checker.md` Wave 7 section for verification protocol.

## 6. Self-Containedness Checklist (DOCS-04)

<!-- AGENT: Verify the analysis note is fully self-contained. A reviewer needs ONLY the PDF to reconstruct the full analysis logic. -->

### Checklist

| Check | Requirement | Status |
|-------|-------------|--------|
| All cut values in text | Every selection cut threshold appears in Section 4 text or tables | |
| All systematic values | Every systematic source, type, and value in Section 6 or appendix | |
| All yields in tables | Signal and background yields per channel in cut-flow and post-fit tables | |
| All efficiencies | Selection efficiency per process in Section 4 | |
| All fit parameters | mu_hat, observed limit, expected limit values in text | |
| Full cut-flow table | Complete cut-flow with all selection stages for signal + all backgrounds | |
| Full systematics appendix | Every systematic: source, type (norm/shape), pre/post-fit values, pruning | |
| Descriptive figure captions | Each caption explains what is plotted, what to observe, key takeaways | |
| No unfilled AGENT directives | No remaining `% AGENT:` placeholders with `[value]` or `[PASS/FAIL]` markers | |
| No code or config in note | Reproducibility via git commit hash reference, not inline code | |
| Git commit hash reference | Note references final analysis commit hash for reproducibility | |
| All figures exist as PDF | Every `\includegraphics` reference resolves to an existing PDF file | |
| Consistent number formatting | Same quantity has identical precision everywhere via `\siunitx` | |

### Self-Containedness Verification

```python
import re
from pathlib import Path

def verify_self_contained(note_dir):
    """Check that the analysis note is self-contained."""
    checks = []
    note_dir = Path(note_dir)

    # Check all figures referenced exist
    for tex_file in note_dir.glob("*.tex"):
        content = tex_file.read_text()
        figs = re.findall(r'\\includegraphics.*?\{(.+?)\}', content)
        for fig in figs:
            fig_path = note_dir / fig
            if not fig_path.exists():
                fig_path = note_dir / "figures" / fig
            checks.append({
                "check": f"Figure exists: {fig}",
                "passes": fig_path.exists()
            })

    # Check no unfilled AGENT directive placeholders
    for tex_file in note_dir.glob("*.tex"):
        content = tex_file.read_text()
        placeholders = re.findall(r'% AGENT:.*\[(?:value|PASS/FAIL|count|yes/no)\]', content)
        checks.append({
            "check": f"No unfilled placeholders in {tex_file.name}",
            "passes": len(placeholders) == 0
        })

    # Check bibliography exists
    bib_path = note_dir / "references.bib"
    checks.append({
        "check": "Bibliography file exists",
        "passes": bib_path.exists()
    })

    return checks

checks = verify_self_contained("analysis/wave7/note")
for c in checks:
    status = "PASS" if c["passes"] else "FAIL"
    print(f"[{status}] {c['check']}")
```

## 7. Compilation (DOCS-01)

<!-- AGENT: Compile the complete analysis note to PDF using the standard HEP LaTeX toolchain. -->

### Compilation Sequence

```python
import subprocess
from pathlib import Path

def compile_note(tex_dir, main_file="main.tex"):
    """Compile LaTeX note with bibliography.

    Runs: pdflatex -> bibtex -> pdflatex -> pdflatex
    Returns dict with success (bool), pdf_path (str), errors (list).
    """
    base = Path(main_file).stem
    results = {"success": False, "pdf_path": None, "errors": []}

    commands = [
        ["pdflatex", "-interaction=nonstopmode", main_file],
        ["bibtex", base],
        ["pdflatex", "-interaction=nonstopmode", main_file],
        ["pdflatex", "-interaction=nonstopmode", main_file],
    ]

    for cmd in commands:
        try:
            proc = subprocess.run(
                cmd, cwd=tex_dir, capture_output=True,
                text=True, timeout=120, check=False
            )
        except subprocess.TimeoutExpired:
            results["errors"].append(f"Timeout: {' '.join(cmd)}")
            return results

    # Verify PDF exists
    pdf_path = Path(tex_dir) / f"{base}.pdf"
    if pdf_path.exists():
        results["success"] = True
        results["pdf_path"] = str(pdf_path)
    else:
        results["errors"].append("PDF not generated")

    # Check for undefined references in log
    log_path = Path(tex_dir) / f"{base}.log"
    if log_path.exists():
        log_content = log_path.read_text()
        undef_refs = re.findall(r"LaTeX Warning: Reference .* undefined", log_content)
        undef_cites = re.findall(r"LaTeX Warning: Citation .* undefined", log_content)
        if undef_refs:
            results["errors"].append(f"Undefined references: {len(undef_refs)}")
        if undef_cites:
            results["errors"].append(f"Undefined citations: {len(undef_cites)}")

    return results

result = compile_note("analysis/wave7/note")
assert result["success"], f"Compilation failed: {result['errors']}"
print(f"PDF generated: {result['pdf_path']}")
```

### Post-Compilation Verification

- PDF file exists at `analysis/wave7/note/main.pdf`
- No undefined references in pdflatex log
- No undefined citations in pdflatex log
- All figures rendered (check PDF page count is reasonable)
- Bibliography section contains entries (not empty)

## Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Complete analysis note (LaTeX) | `analysis/wave7/note/main.tex` | Full note with all sections 1-9 + appendices |
| Section 9: Observed Results | `analysis/wave7/note/section_09_observed.tex` | Observed limit, post-fit yields, diagnostics |
| Publication figures | `analysis/wave7/note/figures/*.pdf` | All plots as PDF vector format |
| Bibliography | `analysis/wave7/note/references.bib` | Auto-generated BibTeX from all wave reports |
| Compiled PDF | `analysis/wave7/note/main.pdf` | Final analysis note PDF |
| Citation verification report | `analysis/wave7/crosscheck/citation_verification_report.md` | Cross-checker verification output |
| Supplementary material | `analysis/wave7/note/SUPPLEMENTARY_MATERIAL.md` | Additional distributions and checks |
| Wave 7 report | `analysis/wave7/WAVE7_NOTE_WRITER.md` | Filled report from this template |

## Summary

<!-- AGENT: Summarize the Wave 7 documentation process. State: (1) whether Section 9 was successfully integrated with observed results, (2) number of plots regenerated and styling consistency, (3) bibliography entry count and citation verification outcome, (4) self-containedness checklist result, (5) PDF compilation status, (6) comparison to published results included. -->
