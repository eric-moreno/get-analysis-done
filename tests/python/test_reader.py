"""Tests for gad.data.reader DataReader class."""

import pytest
import numpy as np
import awkward as ak

from gad.data.reader import DataReader, create_reader
from gad.blinding.errors import BlindingViolationError


class TestDataReaderRawPath:
    """DataReader.load_path reads ROOT files directly."""

    def test_load_path_returns_awkward_array(self, mock_root_file):
        reader = DataReader()
        result = reader.load_path(mock_root_file, tree_name="t", branches=["x"])
        assert isinstance(result, ak.Array)
        assert len(result) == 50
        # Should have field 'x'
        assert "x" in result.fields

    def test_load_path_library_pd(self, mock_root_file):
        reader = DataReader()
        result = reader.load_path(mock_root_file, tree_name="t", branches=["x", "y"], library="pd")
        import pandas as pd
        assert isinstance(result, pd.DataFrame)
        assert "x" in result.columns
        assert "y" in result.columns
        assert len(result) == 50

    def test_load_path_default_tree_name(self, mock_root_file):
        """Default tree name is 't' (ALEPH convention)."""
        reader = DataReader()
        result = reader.load_path(mock_root_file, branches=["x"])
        assert len(result) == 50

    def test_load_path_entry_stop(self, mock_root_file):
        reader = DataReader()
        result = reader.load_path(mock_root_file, branches=["x"], entry_stop=10)
        assert len(result) == 10


class TestDataReaderConfig:
    """DataReader.load_sample resolves samples from config."""

    def test_load_sample_returns_data(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="unblinded")
        reader = DataReader(config_path=config_path, state_path=state_path)
        result = reader.load_sample("qqbar", branches=["x", "y"])
        assert isinstance(result, ak.Array)
        assert len(result) == 50

    def test_load_sample_unknown_raises_key_error(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="unblinded")
        reader = DataReader(config_path=config_path, state_path=state_path)
        with pytest.raises(KeyError, match="nonexistent"):
            reader.load_sample("nonexistent")


class TestDataReaderBlinding:
    """DataReader enforces blinding for signal region samples."""

    def test_signal_region_blocked_when_blinded(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="blinded")
        reader = DataReader(config_path=config_path, state_path=state_path)
        with pytest.raises(BlindingViolationError):
            reader.load_sample("signal", branches=["x"])

    def test_control_region_passes_when_blinded(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="blinded")
        reader = DataReader(config_path=config_path, state_path=state_path)
        result = reader.load_sample("qqbar", branches=["x"])
        assert len(result) == 50

    def test_signal_region_accessible_when_unblinded(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="unblinded")
        reader = DataReader(config_path=config_path, state_path=state_path)
        result = reader.load_sample("signal", branches=["x"])
        assert len(result) == 50


class TestDataReaderFactory:
    """create_reader auto-detects YAML config vs raw ROOT path."""

    def test_from_path_classmethod(self, mock_root_file, mock_state_md):
        state_path = mock_state_md(blinding_status="blinded")
        reader = DataReader.from_path(mock_root_file, state_path=state_path)
        assert reader._raw_path == mock_root_file

    def test_create_reader_detects_yaml(self, mock_samples_yaml, mock_state_md):
        samples_path, config_path = mock_samples_yaml
        state_path = mock_state_md(blinding_status="blinded")
        reader = create_reader(config_path, state_path=state_path)
        assert reader._config is not None

    def test_create_reader_detects_root(self, mock_root_file):
        reader = create_reader(mock_root_file)
        assert reader._raw_path == mock_root_file


class TestDataReaderBranches:
    """DataReader.scan_branches returns branch metadata."""

    def test_scan_branches_returns_metadata(self, mock_root_file):
        reader = DataReader()
        branches = reader.scan_branches(mock_root_file)
        assert isinstance(branches, list)
        assert len(branches) == 3  # x, y, n
        names = {b["name"] for b in branches}
        assert names == {"x", "y", "n"}
        for b in branches:
            assert "typename" in b
            assert "num_entries" in b
            assert "is_jagged" in b
            assert b["num_entries"] == 50
