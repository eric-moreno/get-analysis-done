"""LaTeX compilation via subprocess."""

import logging
import os
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def compile_note(tex_dir: str, main_file: str = "main.tex") -> dict:
    """Compile a LaTeX note using pdflatex -> bibtex -> pdflatex -> pdflatex.

    Parameters
    ----------
    tex_dir : str
        Directory containing LaTeX source files.
    main_file : str
        Main .tex file name (default: main.tex).

    Returns
    -------
    dict
        {"success": bool, "pdf_path": str or None, "errors": list, "warnings": list}
    """
    tex_path = Path(tex_dir)
    base_name = main_file.rsplit(".", 1)[0]
    pdf_path = tex_path / f"{base_name}.pdf"

    errors = []
    warnings = []

    # Build sequence: pdflatex, bibtex, pdflatex, pdflatex
    commands = [
        ["pdflatex", "-interaction=nonstopmode", main_file],
        ["bibtex", base_name],
        ["pdflatex", "-interaction=nonstopmode", main_file],
        ["pdflatex", "-interaction=nonstopmode", main_file],
    ]

    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(tex_path),
                capture_output=True,
                timeout=120,
            )
            stdout_text = result.stdout.decode("utf-8", errors="replace")

            if result.returncode != 0:
                # Extract error lines from output
                for line in stdout_text.splitlines():
                    if line.startswith("!") or "Error" in line:
                        errors.append(line.strip())
                if not errors:
                    errors.append(f"{cmd[0]} exited with code {result.returncode}")
                return {
                    "success": False,
                    "pdf_path": None,
                    "errors": errors,
                    "warnings": warnings,
                }

            # Collect warnings
            for line in stdout_text.splitlines():
                if "Warning" in line:
                    warnings.append(line.strip())

        except subprocess.TimeoutExpired:
            errors.append(f"{cmd[0]} timed out after 120s")
            return {
                "success": False,
                "pdf_path": None,
                "errors": errors,
                "warnings": warnings,
            }
        except FileNotFoundError:
            errors.append(f"{cmd[0]} not found on system")
            return {
                "success": False,
                "pdf_path": None,
                "errors": errors,
                "warnings": warnings,
            }

    success = pdf_path.exists()
    return {
        "success": success,
        "pdf_path": str(pdf_path) if success else None,
        "errors": errors,
        "warnings": warnings,
    }


def check_undefined_references(tex_dir: str, main_file: str = "main.tex") -> list:
    """Parse pdflatex log for undefined references and citations.

    Parameters
    ----------
    tex_dir : str
        Directory containing LaTeX build output.
    main_file : str
        Main .tex file name (default: main.tex).

    Returns
    -------
    list[str]
        List of undefined reference/citation names.
    """
    base_name = main_file.rsplit(".", 1)[0]
    log_path = Path(tex_dir) / f"{base_name}.log"

    if not log_path.exists():
        return []

    undefined = []
    log_text = log_path.read_text(errors="replace")

    # Match: LaTeX Warning: Reference `name' on page X undefined
    for match in re.finditer(r"Reference `([^']+)' on page \d+ undefined", log_text):
        undefined.append(match.group(1))

    # Match: LaTeX Warning: Citation `name' on page X undefined
    for match in re.finditer(r"Citation `([^']+)' on page \d+ undefined", log_text):
        undefined.append(match.group(1))

    return undefined
