"""Tests for gad.documentation -- citations, plots, compiler."""

import json
import os
import textwrap
from unittest.mock import MagicMock, patch, mock_open

import pytest


# ---------------------------------------------------------------------------
# Citation verification tests
# ---------------------------------------------------------------------------

class TestVerifyCitation:
    """Tests for verify_citation."""

    def test_valid_doi_returns_verified(self):
        from gad.documentation.citations import verify_citation

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"metadata": {"titles": [{"title": "Test"}]}}

        with patch("gad.documentation.citations.requests.get", return_value=mock_resp):
            result = verify_citation({"doi": "10.1234/test"})
        assert result["verified"] is True
        assert result["method"] == "DOI"

    def test_valid_arxiv_returns_verified(self):
        from gad.documentation.citations import verify_citation

        mock_resp_ok = MagicMock()
        mock_resp_ok.status_code = 200
        mock_resp_ok.json.return_value = {"metadata": {"titles": [{"title": "arXiv paper"}]}}

        with patch("gad.documentation.citations.requests.get", return_value=mock_resp_ok):
            result = verify_citation({"eprint": "2301.12345"})
        assert result["verified"] is True
        assert result["method"] == "arXiv"

    def test_no_identifiers_returns_unverified(self):
        from gad.documentation.citations import verify_citation

        result = verify_citation({"title": "Some title"})
        assert result["verified"] is False
        assert result["method"] == "none"

    def test_network_timeout_returns_unverified(self):
        import requests
        from gad.documentation.citations import verify_citation

        with patch("gad.documentation.citations.requests.get", side_effect=requests.Timeout("timeout")):
            result = verify_citation({"doi": "10.1234/test"})
        assert result["verified"] is False
        assert "timeout" in result["details"].lower() or "error" in result["details"].lower()


class TestVerifyBibliography:
    """Tests for verify_bibliography."""

    def test_summary_counts(self):
        from gad.documentation.citations import verify_bibliography

        entries = [
            {"doi": "10.1234/a"},
            {"title": "no id"},
        ]

        def fake_verify(entry):
            if "doi" in entry:
                return {"verified": True, "method": "DOI", "details": "ok"}
            return {"verified": False, "method": "none", "details": "no id"}

        with patch("gad.documentation.citations.verify_citation", side_effect=fake_verify):
            result = verify_bibliography(entries)
        assert result["total"] == 2
        assert result["verified_count"] == 1
        assert result["failed_count"] == 1

    def test_empty_bibliography(self):
        from gad.documentation.citations import verify_bibliography

        result = verify_bibliography([])
        assert result["total"] == 0
        assert result["verified_count"] == 0


class TestCollectCitationsFromBib:
    """Tests for collect_citations_from_bib BibTeX parser."""

    def test_parses_bibtex_entries(self, tmp_path):
        from gad.documentation.citations import collect_citations_from_bib

        bib = tmp_path / "refs.bib"
        bib.write_text(textwrap.dedent("""\
            @article{Smith2023,
              author = {Smith, J.},
              title = {Test Paper},
              doi = {10.1234/test},
              eprint = {2301.12345},
            }

            @inproceedings{Jones2024,
              author = {Jones, A.},
              title = {Another Paper},
              url = {https://example.com},
            }
        """))
        result = collect_citations_from_bib(str(bib))
        assert len(result) == 2
        assert result[0]["cite_key"] == "Smith2023"
        assert result[0]["doi"] == "10.1234/test"
        assert result[0]["eprint"] == "2301.12345"
        assert result[1]["cite_key"] == "Jones2024"
        assert result[1]["url"] == "https://example.com"

    def test_handles_nested_braces(self, tmp_path):
        from gad.documentation.citations import collect_citations_from_bib

        bib = tmp_path / "refs.bib"
        bib.write_text('@article{Key1,\n  title = {{Nested Title}},\n}\n')
        result = collect_citations_from_bib(str(bib))
        assert len(result) == 1
        assert "title" in result[0]

    def test_nonexistent_file_returns_empty(self):
        from gad.documentation.citations import collect_citations_from_bib

        result = collect_citations_from_bib("/nonexistent/path.bib")
        assert result == []


class TestCollectCitationsFromYaml:
    """Tests for collect_citations_from_yaml."""

    def test_reads_yaml_file(self, tmp_path):
        from gad.documentation.citations import collect_citations_from_yaml

        yaml_content = textwrap.dedent("""\
        references:
          - title: "Test paper"
            doi: "10.1234/test"
          - title: "arXiv paper"
            eprint: "2301.12345"
        """)
        yaml_file = tmp_path / "references.yaml"
        yaml_file.write_text(yaml_content)

        result = collect_citations_from_yaml(str(yaml_file))
        assert len(result) == 2
        assert result[0]["doi"] == "10.1234/test"

    def test_bib_file_autodetect(self, tmp_path):
        from gad.documentation.citations import collect_citations_from_yaml

        bib = tmp_path / "refs.bib"
        bib.write_text('@article{Key1,\n  title = {Test},\n  doi = {10.1/x},\n}\n')
        result = collect_citations_from_yaml(str(bib))
        assert len(result) == 1
        assert result[0]["cite_key"] == "Key1"


# ---------------------------------------------------------------------------
# Plot utility tests
# ---------------------------------------------------------------------------

class TestSetupExperimentStyle:
    """Tests for setup_experiment_style."""

    def test_atlas_style_applies(self):
        from gad.documentation.plots import setup_experiment_style

        # Should not raise
        setup_experiment_style("ATLAS")

    def test_unknown_style_falls_back(self):
        from gad.documentation.plots import setup_experiment_style

        # Should not raise even with nonexistent style
        setup_experiment_style("ALEPH")

    def test_mplhep_import_failure_falls_back(self):
        import importlib
        import sys
        from gad.documentation import plots as plots_mod

        with patch.dict(sys.modules, {"mplhep": None, "mplhep.style": None}):
            # Re-import to trigger fallback path
            # Just call directly -- it should handle ImportError
            plots_mod.setup_experiment_style("ATLAS")


class TestRegenerateAllPlots:
    """Tests for regenerate_all_plots."""

    def test_generates_plots(self, tmp_path):
        from gad.documentation.plots import regenerate_all_plots

        out1 = str(tmp_path / "plot1.pdf")
        out2 = str(tmp_path / "plot2.pdf")

        def gen1(**kwargs):
            fig_mock = MagicMock()
            return fig_mock

        def gen2(**kwargs):
            fig_mock = MagicMock()
            return fig_mock

        config = {
            "plot1": {"generator": gen1, "output_path": out1, "kwargs": {}},
            "plot2": {"generator": gen2, "output_path": out2, "kwargs": {}},
        }

        result = regenerate_all_plots(config)
        assert result["total"] == 2
        assert result["generated"] == 2
        assert result["failed"] == []

    def test_failed_plot_reported(self, tmp_path):
        from gad.documentation.plots import regenerate_all_plots

        def gen_fail(**kwargs):
            raise ValueError("broken")

        config = {
            "bad_plot": {"generator": gen_fail, "output_path": str(tmp_path / "x.pdf"), "kwargs": {}},
        }

        result = regenerate_all_plots(config)
        assert result["generated"] == 0
        assert len(result["failed"]) == 1


# ---------------------------------------------------------------------------
# Compiler tests
# ---------------------------------------------------------------------------

class TestCompileNote:
    """Tests for compile_note."""

    def test_success(self, tmp_path):
        from gad.documentation.compiler import compile_note

        # Create a fake main.tex and pdf
        (tmp_path / "main.tex").write_text("\\documentclass{article}")
        (tmp_path / "main.pdf").touch()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"Output written on main.pdf"
        mock_result.stderr = b""

        with patch("gad.documentation.compiler.subprocess.run", return_value=mock_result):
            result = compile_note(str(tmp_path))
        assert result["success"] is True
        assert result["pdf_path"] is not None

    def test_failure(self, tmp_path):
        from gad.documentation.compiler import compile_note

        (tmp_path / "main.tex").write_text("bad latex")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b"! Undefined control sequence"
        mock_result.stderr = b""

        with patch("gad.documentation.compiler.subprocess.run", return_value=mock_result):
            result = compile_note(str(tmp_path))
        assert result["success"] is False
        assert len(result["errors"]) > 0


class TestCheckUndefinedReferences:
    """Tests for check_undefined_references."""

    def test_finds_undefined_refs(self, tmp_path):
        from gad.documentation.compiler import check_undefined_references

        log_content = textwrap.dedent("""\
        LaTeX Warning: Reference `fig:missing' on page 1 undefined
        LaTeX Warning: Citation `ghost2023' on page 2 undefined
        Some normal output
        """)
        (tmp_path / "main.log").write_text(log_content)

        result = check_undefined_references(str(tmp_path))
        assert "fig:missing" in result
        assert "ghost2023" in result

    def test_missing_log_file(self, tmp_path):
        from gad.documentation.compiler import check_undefined_references

        result = check_undefined_references(str(tmp_path))
        assert result == []


# ---------------------------------------------------------------------------
# Self-containedness verification tests
# ---------------------------------------------------------------------------

def _make_note_dir(tmp_path, **overrides):
    """Helper to create a minimal mock analysis note directory."""
    note_dir = tmp_path / "note"
    note_dir.mkdir()
    figures_dir = note_dir / "figures"
    figures_dir.mkdir()

    # Default: valid note
    defaults = {
        "main_tex": r"\documentclass{article}\begin{document}\input{section_04}\end{document}",
        "section_04": r"\section{Selection}\begin{tabular}{cc}cut & eff\end{tabular}",
        "section_06": r"\section{Systematics}\begin{tabular}{cc}syst & val\end{tabular}",
        "section_09": "\\section{Conclusion}\nThis analysis measured X.\nThe result is Y.\nWe observe Z.",
        "bib_content": "@article{ref1, author={A}, title={T}, year={2024}}",
        "has_figure": True,
        "figure_ref": "figures/plot1",
        "has_agent_directive": False,
        "has_git_hash": True,
    }
    defaults.update(overrides)

    (note_dir / "main.tex").write_text(defaults["main_tex"])
    (note_dir / "section_04.tex").write_text(defaults["section_04"])
    (note_dir / "section_06.tex").write_text(defaults["section_06"])
    (note_dir / "section_09.tex").write_text(defaults["section_09"])

    if defaults["bib_content"]:
        (note_dir / "references.bib").write_text(defaults["bib_content"])

    if defaults["has_figure"]:
        (figures_dir / "plot1.pdf").touch()
        tex = (note_dir / "main.tex").read_text()
        tex += f"\n\\includegraphics{{{defaults['figure_ref']}}}"
        (note_dir / "main.tex").write_text(tex)

    if defaults["has_agent_directive"]:
        content = (note_dir / "section_04.tex").read_text()
        content += "\n% AGENT: Fill in the cut values"
        (note_dir / "section_04.tex").write_text(content)

    if defaults["has_git_hash"]:
        content = (note_dir / "main.tex").read_text()
        content += "\n\\texttt{abc1234def5}"
        (note_dir / "main.tex").write_text(content)

    return note_dir


class TestVerifySelfContained:
    """Tests for verify_self_contained."""

    def test_all_checks_pass_on_valid_note(self, tmp_path):
        from gad.documentation.verification import verify_self_contained

        note_dir = _make_note_dir(tmp_path)
        checks = verify_self_contained(str(note_dir))
        assert len(checks) == 8
        for c in checks:
            assert c["passes"] is True, f"Check {c['check']} failed: {c['detail']}"

    def test_missing_figures_detected(self, tmp_path):
        from gad.documentation.verification import verify_self_contained

        note_dir = _make_note_dir(tmp_path, has_figure=False)
        # Add a reference to a missing figure
        tex = (note_dir / "main.tex").read_text()
        tex += "\n\\includegraphics{figures/missing_plot}"
        (note_dir / "main.tex").write_text(tex)

        checks = verify_self_contained(str(note_dir))
        fig_check = next(c for c in checks if c["check"] == "figures_exist")
        assert fig_check["passes"] is False

    def test_unfilled_agent_directives_detected(self, tmp_path):
        from gad.documentation.verification import verify_self_contained

        note_dir = _make_note_dir(tmp_path, has_agent_directive=True)
        checks = verify_self_contained(str(note_dir))
        agent_check = next(c for c in checks if c["check"] == "no_agent_directives")
        assert agent_check["passes"] is False

    def test_empty_section_9_detected(self, tmp_path):
        from gad.documentation.verification import verify_self_contained

        note_dir = _make_note_dir(tmp_path, section_09="% Section 9\n% TODO")
        checks = verify_self_contained(str(note_dir))
        s9_check = next(c for c in checks if c["check"] == "section_9_exists")
        assert s9_check["passes"] is False

    def test_missing_bibliography_detected(self, tmp_path):
        from gad.documentation.verification import verify_self_contained

        note_dir = _make_note_dir(tmp_path, bib_content=None)
        checks = verify_self_contained(str(note_dir))
        bib_check = next(c for c in checks if c["check"] == "bibliography_exists")
        assert bib_check["passes"] is False


class TestGenerateVerificationReport:
    """Tests for generate_verification_report."""

    def test_report_format(self):
        from gad.documentation.verification import generate_verification_report

        checks = [
            {"check": "test_a", "passes": True, "detail": "ok"},
            {"check": "test_b", "passes": False, "detail": "missing"},
        ]
        report = generate_verification_report(checks)
        assert "1/2 checks passed" in report
        assert "PASS" in report
        assert "FAIL" in report
