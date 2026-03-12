"""Tests for gad.data.quality DataQualityScan class."""

import os
import numpy as np
import uproot
import pytest

from gad.data.quality import DataQualityScan


@pytest.fixture
def mock_root_file_2(tmp_path):
    """Create a second mock ROOT file with the same branches but different data."""
    path = str(tmp_path / "test_data_2.root")
    rng = np.random.RandomState(777)
    n_events = 30
    with uproot.recreate(path) as f:
        f["t"] = {
            "x": rng.normal(0, 1, n_events).astype(np.float64),
            "y": rng.exponential(2.0, n_events).astype(np.float64),
            "n": np.arange(100, 100 + n_events, dtype=np.int32),
        }
    return path


@pytest.fixture
def mock_root_file_inconsistent(tmp_path):
    """Create a ROOT file with different branch names for consistency check."""
    path = str(tmp_path / "test_inconsistent.root")
    rng = np.random.RandomState(555)
    n_events = 20
    with uproot.recreate(path) as f:
        f["t"] = {
            "x": rng.normal(0, 1, n_events).astype(np.float64),
            "z": rng.normal(0, 1, n_events).astype(np.float64),  # 'z' instead of 'y'
            "n": np.arange(n_events, dtype=np.int32),
        }
    return path


@pytest.fixture
def mock_root_file_with_nan(tmp_path):
    """Create a ROOT file with NaN and inf values."""
    path = str(tmp_path / "test_nan.root")
    n_events = 50
    x = np.arange(n_events, dtype=np.float64)
    x[10] = np.nan
    x[20] = np.inf
    x[30] = -np.inf
    with uproot.recreate(path) as f:
        f["t"] = {
            "x": x,
            "y": np.ones(n_events, dtype=np.float64),
            "n": np.arange(n_events, dtype=np.int32),
        }
    return path


@pytest.fixture
def mock_root_file_with_duplicates(tmp_path):
    """Create a ROOT file with duplicate event IDs."""
    path = str(tmp_path / "test_dupes.root")
    n_events = 50
    # Create duplicate event IDs: first 10 events are duplicated
    event_ids = np.arange(n_events, dtype=np.int32)
    event_ids[40:50] = event_ids[0:10]  # Duplicate first 10 IDs
    with uproot.recreate(path) as f:
        f["t"] = {
            "x": np.random.RandomState(42).normal(0, 1, n_events).astype(np.float64),
            "y": np.random.RandomState(42).exponential(2.0, n_events).astype(np.float64),
            "n": event_ids,
        }
    return path


class TestDataQualityScan:
    """DataQualityScan checks file integrity, events, branches, NaN/inf, duplicates."""

    def test_run_returns_structured_report(self, mock_root_file, mock_root_file_2):
        scan = DataQualityScan()
        report = scan.run([mock_root_file, mock_root_file_2])
        assert "file_integrity" in report
        assert "event_counts" in report
        assert "branch_consistency" in report
        assert "nan_inf" in report
        assert "duplicates" in report
        assert "warnings" in report
        assert "blockers" in report

    def test_detects_missing_files(self, mock_root_file):
        scan = DataQualityScan()
        report = scan.run([mock_root_file, "/nonexistent/file.root"])
        # Missing files should appear in file_integrity
        integrity = report["file_integrity"]
        missing = [f for f in integrity if not f["ok"]]
        assert len(missing) == 1
        assert "blockers" in report
        assert any("missing" in b.lower() or "not found" in b.lower()
                    for b in report["blockers"])

    def test_detects_branch_inconsistency(self, mock_root_file, mock_root_file_inconsistent):
        scan = DataQualityScan()
        report = scan.run([mock_root_file, mock_root_file_inconsistent])
        consistency = report["branch_consistency"]
        assert not consistency["consistent"]

    def test_reports_nan_inf(self, mock_root_file_with_nan):
        scan = DataQualityScan()
        report = scan.run([mock_root_file_with_nan])
        nan_inf = report["nan_inf"]
        # Should detect NaN and inf in branch 'x'
        assert any(entry["nan_count"] > 0 or entry["inf_count"] > 0
                    for entry in nan_inf)

    def test_detects_duplicate_events(self, mock_root_file_with_duplicates):
        scan = DataQualityScan()
        report = scan.run([mock_root_file_with_duplicates], event_id_branch="n")
        dupes = report["duplicates"]
        assert dupes["count"] > 0
        assert dupes["fraction"] > 0.0
        assert dupes["method"] == "event_id"

    def test_to_yaml_returns_dict(self, mock_root_file):
        scan = DataQualityScan()
        report = scan.run([mock_root_file])
        yaml_dict = scan.to_yaml()
        assert isinstance(yaml_dict, dict)

    def test_to_markdown_returns_string(self, mock_root_file):
        scan = DataQualityScan()
        report = scan.run([mock_root_file])
        md = scan.to_markdown()
        assert isinstance(md, str)
        assert "File Integrity" in md or "file_integrity" in md.lower()
