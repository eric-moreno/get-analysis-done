"""Tests for gad.blinding.integrity -- BlindingIntegrityChecker."""

import os
import subprocess

import pytest

from gad.blinding.integrity import BlindingIntegrityChecker


class TestSrPlotsEmpty:
    """Tests for check_sr_plots_empty."""

    def test_sr_plots_empty_passes_when_dir_empty(self, tmp_path):
        plots_dir = tmp_path / "plots" / "signal_region"
        plots_dir.mkdir(parents=True)
        checker = BlindingIntegrityChecker(str(tmp_path), sr_plots_dir=str(plots_dir))
        result = checker.check_sr_plots_empty()
        assert result["passes"] is True

    def test_sr_plots_empty_passes_when_dir_missing(self, tmp_path):
        checker = BlindingIntegrityChecker(
            str(tmp_path), sr_plots_dir=str(tmp_path / "nonexistent")
        )
        result = checker.check_sr_plots_empty()
        assert result["passes"] is True

    def test_sr_plots_empty_fails_when_files_exist(self, tmp_path):
        plots_dir = tmp_path / "plots" / "signal_region"
        plots_dir.mkdir(parents=True)
        (plots_dir / "sr_plot.pdf").write_text("fake")
        checker = BlindingIntegrityChecker(str(tmp_path), sr_plots_dir=str(plots_dir))
        result = checker.check_sr_plots_empty()
        assert result["passes"] is False


class TestNoSrYields:
    """Tests for check_no_sr_yields_in_outputs."""

    def test_no_sr_yields_passes_with_clean_files(self, tmp_path):
        wave_dir = tmp_path / "wave_output"
        wave_dir.mkdir()
        (wave_dir / "summary.md").write_text("background yields: 100.5")
        checker = BlindingIntegrityChecker(str(tmp_path))
        result = checker.check_no_sr_yields_in_outputs(wave_dirs=[str(wave_dir)])
        assert result["passes"] is True

    def test_no_sr_yields_fails_with_sr_data(self, tmp_path):
        wave_dir = tmp_path / "wave_output"
        wave_dir.mkdir()
        (wave_dir / "summary.md").write_text(
            "observed signal region yield: 123.45 events"
        )
        checker = BlindingIntegrityChecker(str(tmp_path))
        result = checker.check_no_sr_yields_in_outputs(wave_dirs=[str(wave_dir)])
        assert result["passes"] is False


class TestGitHistory:
    """Tests for check_git_history."""

    def test_git_no_sr_data_passes_clean_repo(self, tmp_path):
        # Create a minimal git repo with no SR data
        subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(tmp_path), capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(tmp_path), capture_output=True,
        )
        (tmp_path / "readme.txt").write_text("clean repo")
        subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=str(tmp_path), capture_output=True,
        )
        checker = BlindingIntegrityChecker(str(tmp_path))
        result = checker.check_git_history()
        assert result["passes"] is True


class TestRunAll:
    """Tests for run_all aggregation."""

    def test_run_all_aggregates_results(self, tmp_path):
        # Empty plots dir + clean wave dir + clean git repo
        plots_dir = tmp_path / "plots" / "signal_region"
        plots_dir.mkdir(parents=True)
        wave_dir = tmp_path / "wave_output"
        wave_dir.mkdir()
        (wave_dir / "summary.md").write_text("background only")

        subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(tmp_path), capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(tmp_path), capture_output=True,
        )
        (tmp_path / "readme.txt").write_text("clean")
        subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=str(tmp_path), capture_output=True,
        )

        checker = BlindingIntegrityChecker(
            str(tmp_path), sr_plots_dir=str(plots_dir)
        )
        result = checker.run_all(wave_dirs=[str(wave_dir)])
        assert result["all_pass"] is True
        assert len(result["checks"]) == 3

    def test_run_all_fails_if_any_check_fails(self, tmp_path):
        # Plots dir with files -> first check fails
        plots_dir = tmp_path / "plots" / "signal_region"
        plots_dir.mkdir(parents=True)
        (plots_dir / "leak.pdf").write_text("leaked SR plot")

        subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(tmp_path), capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(tmp_path), capture_output=True,
        )
        (tmp_path / "readme.txt").write_text("has leak")
        subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=str(tmp_path), capture_output=True,
        )

        checker = BlindingIntegrityChecker(
            str(tmp_path), sr_plots_dir=str(plots_dir)
        )
        result = checker.run_all()
        assert result["all_pass"] is False
