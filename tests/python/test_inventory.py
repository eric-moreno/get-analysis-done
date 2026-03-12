"""Tests for gad.data.inventory variable inventory scanner."""

import numpy as np
import pytest

from gad.data.inventory import VariableInventory, scan_variable_inventory


class TestVariableInventory:
    """scan_variable_inventory produces a catalog of branch metadata and statistics."""

    def test_scan_returns_list_of_dicts(self, mock_root_file):
        result = scan_variable_inventory(mock_root_file)
        assert isinstance(result, list)
        assert len(result) == 3  # x, y, n branches

    def test_scan_has_required_keys(self, mock_root_file):
        result = scan_variable_inventory(mock_root_file)
        required_keys = {"name", "typename", "num_entries", "is_jagged",
                         "min", "max", "mean", "fill_fraction"}
        for entry in result:
            assert required_keys.issubset(entry.keys()), (
                f"Missing keys: {required_keys - set(entry.keys())}"
            )

    def test_scan_statistics_reasonable(self, mock_root_file):
        result = scan_variable_inventory(mock_root_file)
        # Find the 'x' branch (normal distribution around 0)
        x_info = next(r for r in result if r["name"] == "x")
        assert x_info["num_entries"] == 50
        assert x_info["min"] < x_info["max"]
        assert isinstance(x_info["mean"], float)
        assert 0.0 <= x_info["fill_fraction"] <= 1.0

    def test_scan_flat_branches_not_jagged(self, mock_root_file):
        result = scan_variable_inventory(mock_root_file)
        for entry in result:
            assert entry["is_jagged"] is False  # All branches in mock are flat

    def test_scan_respects_max_events(self, mock_root_file):
        """max_events limits the number of events read for statistics."""
        result = scan_variable_inventory(mock_root_file, max_events=10)
        # Should still report statistics, but based on fewer events
        assert isinstance(result, list)
        assert len(result) == 3

    def test_variable_inventory_class_to_json(self, mock_root_file):
        inv = VariableInventory(mock_root_file)
        data = inv.to_json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_variable_inventory_class_to_markdown(self, mock_root_file):
        inv = VariableInventory(mock_root_file)
        md = inv.to_markdown()
        assert isinstance(md, str)
        assert "| Name" in md  # Should have a table header
        assert "x" in md
        assert "y" in md
        assert "n" in md
