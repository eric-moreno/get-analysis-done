"""Self-containedness verification for analysis notes."""

import logging
import os
import re
from pathlib import Path

from gad.documentation.compiler import check_undefined_references

logger = logging.getLogger(__name__)


def verify_self_contained(note_dir: str) -> list:
    """Run all self-containedness checks on a compiled analysis note directory.

    Parameters
    ----------
    note_dir : str
        Path to the analysis note directory containing .tex files and build output.

    Returns
    -------
    list[dict]
        Each entry: {"check": str, "passes": bool, "detail": str}
    """
    note_path = Path(note_dir)
    checks = []

    # 1. All \\includegraphics references resolve to existing PDF files
    checks.append(_check_figures(note_path))

    # 2. No unfilled % AGENT: directives remain
    checks.append(_check_agent_directives(note_path))

    # 3. Bibliography file exists and is non-empty
    checks.append(_check_bibliography(note_path))

    # 4. No undefined references in pdflatex log
    checks.append(_check_undefined_refs(note_path))

    # 5. Section 9 file exists and has content (not just template)
    checks.append(_check_section_9(note_path))

    # 6. Git commit hash referenced in note
    checks.append(_check_git_hash(note_path))

    # 7. Cut-flow table exists in section_04
    checks.append(_check_cutflow_table(note_path))

    # 8. Systematics table exists in section_06 or appendix
    checks.append(_check_systematics_table(note_path))

    return checks


def _check_figures(note_path: Path) -> dict:
    """Check that all \\includegraphics references resolve to existing files."""
    missing = []
    tex_files = list(note_path.rglob("*.tex"))

    for tex_file in tex_files:
        content = tex_file.read_text(errors="replace")
        for match in re.finditer(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", content):
            fig_ref = match.group(1)
            # Try exact path and with .pdf extension
            candidates = [
                note_path / fig_ref,
                note_path / f"{fig_ref}.pdf",
                note_path / f"{fig_ref}.png",
            ]
            if not any(c.exists() for c in candidates):
                missing.append(fig_ref)

    if missing:
        return {
            "check": "figures_exist",
            "passes": False,
            "detail": f"Missing figures: {', '.join(missing)}",
        }
    return {"check": "figures_exist", "passes": True, "detail": "All figures found"}


def _check_agent_directives(note_path: Path) -> dict:
    """Check that no unfilled % AGENT: directives remain."""
    unfilled = []
    tex_files = list(note_path.rglob("*.tex"))

    for tex_file in tex_files:
        content = tex_file.read_text(errors="replace")
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            # Match % AGENT: or <!-- AGENT: directives (not regular comments)
            if re.match(r"^%\s*AGENT:", stripped):
                unfilled.append(f"{tex_file.name}:{i}")

    if unfilled:
        return {
            "check": "no_agent_directives",
            "passes": False,
            "detail": f"Unfilled AGENT directives at: {', '.join(unfilled)}",
        }
    return {"check": "no_agent_directives", "passes": True, "detail": "No unfilled AGENT directives"}


def _check_bibliography(note_path: Path) -> dict:
    """Check that references.bib exists and is non-empty."""
    bib_files = list(note_path.rglob("*.bib"))
    if not bib_files:
        return {
            "check": "bibliography_exists",
            "passes": False,
            "detail": "No .bib file found",
        }

    for bib in bib_files:
        if bib.stat().st_size > 0:
            return {
                "check": "bibliography_exists",
                "passes": True,
                "detail": f"Bibliography found: {bib.name}",
            }

    return {
        "check": "bibliography_exists",
        "passes": False,
        "detail": "All .bib files are empty",
    }


def _check_undefined_refs(note_path: Path) -> dict:
    """Check for undefined references in pdflatex log."""
    undefined = check_undefined_references(str(note_path))
    if undefined:
        return {
            "check": "no_undefined_refs",
            "passes": False,
            "detail": f"Undefined references: {', '.join(undefined)}",
        }
    return {"check": "no_undefined_refs", "passes": True, "detail": "No undefined references"}


def _check_section_9(note_path: Path) -> dict:
    """Check that Section 9 file exists and has substantive content."""
    # Look for section_09 or section_9 files
    candidates = list(note_path.rglob("*section*09*")) + list(note_path.rglob("*section*9*"))
    tex_candidates = [c for c in candidates if c.suffix == ".tex"]

    if not tex_candidates:
        return {
            "check": "section_9_exists",
            "passes": False,
            "detail": "No Section 9 file found",
        }

    for f in tex_candidates:
        content = f.read_text(errors="replace").strip()
        # Check it's not just a template (has more than comments and section header)
        lines = [l for l in content.splitlines()
                 if l.strip() and not l.strip().startswith("%")]
        # Need at least a section header + some content
        if len(lines) >= 3:
            return {
                "check": "section_9_exists",
                "passes": True,
                "detail": f"Section 9 found with content: {f.name}",
            }

    return {
        "check": "section_9_exists",
        "passes": False,
        "detail": "Section 9 file exists but appears to be empty/template",
    }


def _check_git_hash(note_path: Path) -> dict:
    """Check that a git commit hash is referenced in the note."""
    tex_files = list(note_path.rglob("*.tex"))
    # Match 7+ hex chars (short hash) or 40 hex chars (full hash) or \\texttt{hash}
    hash_pattern = re.compile(r"(?:\\texttt\{[0-9a-f]{7,40}\}|[0-9a-f]{40})")

    for tex_file in tex_files:
        content = tex_file.read_text(errors="replace")
        if hash_pattern.search(content):
            return {
                "check": "git_hash_referenced",
                "passes": True,
                "detail": f"Git hash found in {tex_file.name}",
            }

    return {
        "check": "git_hash_referenced",
        "passes": False,
        "detail": "No git commit hash found in any .tex file",
    }


def _check_cutflow_table(note_path: Path) -> dict:
    """Check that a cut-flow table exists in section_04."""
    candidates = list(note_path.rglob("*section*04*")) + list(note_path.rglob("*section*4*"))
    tex_candidates = [c for c in candidates if c.suffix == ".tex"]

    for f in tex_candidates:
        content = f.read_text(errors="replace")
        if r"\begin{tabular}" in content or r"\begin{longtable}" in content:
            return {
                "check": "cutflow_table_exists",
                "passes": True,
                "detail": f"Cut-flow table found in {f.name}",
            }

    return {
        "check": "cutflow_table_exists",
        "passes": False,
        "detail": "No tabular environment found in section 04 files",
    }


def _check_systematics_table(note_path: Path) -> dict:
    """Check that a systematics table exists in section_06 or appendix."""
    candidates = (
        list(note_path.rglob("*section*06*"))
        + list(note_path.rglob("*section*6*"))
        + list(note_path.rglob("*appendix*"))
    )
    tex_candidates = [c for c in candidates if c.suffix == ".tex"]

    for f in tex_candidates:
        content = f.read_text(errors="replace")
        if r"\begin{tabular}" in content or r"\begin{longtable}" in content:
            return {
                "check": "systematics_table_exists",
                "passes": True,
                "detail": f"Systematics table found in {f.name}",
            }

    return {
        "check": "systematics_table_exists",
        "passes": False,
        "detail": "No tabular environment found in section 06 or appendix files",
    }


def generate_verification_report(checks: list) -> str:
    """Format checks into a markdown report.

    Parameters
    ----------
    checks : list[dict]
        List of check results from verify_self_contained.

    Returns
    -------
    str
        Markdown-formatted report.
    """
    passed = sum(1 for c in checks if c["passes"])
    total = len(checks)

    lines = [
        "# Self-Containedness Verification Report",
        "",
        f"**Result: {passed}/{total} checks passed**",
        "",
        "| Check | Status | Detail |",
        "|-------|--------|--------|",
    ]

    for c in checks:
        status = "PASS" if c["passes"] else "FAIL"
        lines.append(f"| {c['check']} | {status} | {c['detail']} |")

    lines.append("")
    return "\n".join(lines)
