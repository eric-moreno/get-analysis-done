"""Tests for experiment context loading and AnalysisConfig extension.

Tests cover:
- ExperimentContext loading from multi-file YAML directory
- Missing directory and missing required file errors
- Optional files defaulting to empty dict
- Object definition retrieval with and without overrides
- Generic (non-ALEPH) experiment loading without code changes
- AnalysisConfig extension with experiment, samples, object_overrides, sqrt_s
"""

import pytest

from gad.config.experiment import ExperimentContext


# ============================================================
# ExperimentContext loading tests
# ============================================================

class TestExperimentContextLoading:
    """Tests for ExperimentContext file loading behaviour."""

    def test_loads_all_five_yaml_files(self, mock_aleph_experiment):
        """ExperimentContext loads all 5 YAML files from experiments/aleph/."""
        ctx = ExperimentContext("aleph", experiments_dir=mock_aleph_experiment)

        assert ctx.detector["experiment"] == "aleph"
        assert ctx.detector["collider"] == "LEP"
        assert "good_track" in ctx.objects
        assert "good_neutral" in ctx.objects
        assert "generators" in ctx.mc_generators
        assert "tracking" in ctx.performance
        assert "key_papers" in ctx.references

    def test_raises_file_not_found_if_dir_missing(self, tmp_path):
        """ExperimentContext raises FileNotFoundError for nonexistent directory."""
        with pytest.raises(FileNotFoundError, match="not found"):
            ExperimentContext("nonexistent", experiments_dir=str(tmp_path / "experiments"))

    def test_raises_file_not_found_if_detector_yaml_missing(self, mock_experiment_dir):
        """ExperimentContext raises FileNotFoundError if detector.yaml is missing."""
        experiments_dir = mock_experiment_dir("missing_det", skip_files=["detector.yaml"])
        with pytest.raises(FileNotFoundError, match="detector.yaml"):
            ExperimentContext("missing_det", experiments_dir=experiments_dir)

    def test_raises_file_not_found_if_objects_yaml_missing(self, mock_experiment_dir):
        """ExperimentContext raises FileNotFoundError if objects.yaml is missing."""
        experiments_dir = mock_experiment_dir("missing_obj", skip_files=["objects.yaml"])
        with pytest.raises(FileNotFoundError, match="objects.yaml"):
            ExperimentContext("missing_obj", experiments_dir=experiments_dir)

    def test_optional_mc_generators_defaults_to_empty(self, mock_experiment_dir):
        """mc_generators defaults to empty dict when file is missing."""
        experiments_dir = mock_experiment_dir(
            "no_mc", skip_files=["mc_generators.yaml"]
        )
        ctx = ExperimentContext("no_mc", experiments_dir=experiments_dir)
        assert ctx.mc_generators == {}

    def test_optional_performance_defaults_to_empty(self, mock_experiment_dir):
        """performance defaults to empty dict when file is missing."""
        experiments_dir = mock_experiment_dir(
            "no_perf", skip_files=["performance.yaml"]
        )
        ctx = ExperimentContext("no_perf", experiments_dir=experiments_dir)
        assert ctx.performance == {}

    def test_optional_references_defaults_to_empty(self, mock_experiment_dir):
        """references defaults to empty dict when file is missing."""
        experiments_dir = mock_experiment_dir(
            "no_refs", skip_files=["references.yaml"]
        )
        ctx = ExperimentContext("no_refs", experiments_dir=experiments_dir)
        assert ctx.references == {}


# ============================================================
# ExperimentContext object definition tests
# ============================================================

class TestExperimentContextObjects:
    """Tests for get_object_definition with and without overrides."""

    def test_get_object_definition_returns_dict(self, mock_experiment_dir):
        """get_object_definition returns the object definition dict."""
        experiments_dir = mock_experiment_dir()
        ctx = ExperimentContext("test_exp", experiments_dir=experiments_dir)

        defn = ctx.get_object_definition("good_track")
        assert defn["description"] == "Test good track"
        assert len(defn["cuts"]) == 2
        assert defn["metadata"]["expected_efficiency"] == 0.95

    def test_get_object_definition_unknown_returns_empty(self, mock_experiment_dir):
        """get_object_definition returns empty dict for unknown object."""
        experiments_dir = mock_experiment_dir()
        ctx = ExperimentContext("test_exp", experiments_dir=experiments_dir)

        defn = ctx.get_object_definition("nonexistent_object")
        assert defn == {}

    def test_get_object_definition_with_overrides_merges(self, mock_experiment_dir):
        """Overrides merge into the base object definition."""
        experiments_dir = mock_experiment_dir()
        ctx = ExperimentContext("test_exp", experiments_dir=experiments_dir)

        overrides = {
            "good_track": {
                "cuts": [
                    {"variable": "pt", "operator": ">", "threshold": 1.0, "unit": "GeV"},
                ],
            },
        }
        defn = ctx.get_object_definition("good_track", overrides=overrides)

        # Override replaces cuts
        assert len(defn["cuts"]) == 1
        assert defn["cuts"][0]["threshold"] == 1.0
        # Original description preserved
        assert defn["description"] == "Test good track"

    def test_get_object_definition_overrides_for_different_object_ignored(
        self, mock_experiment_dir
    ):
        """Overrides for a different object do not affect the requested one."""
        experiments_dir = mock_experiment_dir()
        ctx = ExperimentContext("test_exp", experiments_dir=experiments_dir)

        overrides = {
            "good_jet": {
                "cuts": [
                    {"variable": "pt", "operator": ">", "threshold": 50.0, "unit": "GeV"},
                ],
            },
        }
        defn = ctx.get_object_definition("good_track", overrides=overrides)

        # good_track unchanged
        assert len(defn["cuts"]) == 2
        assert defn["cuts"][0]["threshold"] == 0.5


# ============================================================
# Generic (non-ALEPH) experiment context test
# ============================================================

class TestGenericContext:
    """Test that a minimal non-ALEPH experiment works without code changes."""

    def test_cms_like_experiment_loads(self, mock_experiment_dir):
        """A CMS-like experiment context loads correctly."""
        cms_detector = {
            "experiment": "cms",
            "collider": "LHC",
            "full_name": "Compact Muon Solenoid",
            "sqrt_s_range": [7000.0, 13600.0],
            "subsystems": {
                "tracker": {"name": "Tracker", "type": "silicon_pixel_strip"},
                "ecal": {"name": "ECAL", "type": "PbWO4_crystals"},
                "hcal": {"name": "HCAL", "type": "brass_scintillator"},
                "muon": {"name": "Muon System", "type": "DT_CSC_RPC"},
            },
        }

        cms_objects = {
            "tight_muon": {
                "description": "CMS tight muon ID",
                "cuts": [
                    {"variable": "pt", "operator": ">", "threshold": 26.0, "unit": "GeV"},
                    {"variable": "eta", "operator": "<", "threshold": 2.4, "absolute": True},
                    {"variable": "is_global_muon", "operator": "==", "threshold": 1},
                ],
                "metadata": {"expected_efficiency": 0.96},
            },
        }

        experiments_dir = mock_experiment_dir(
            "cms",
            files={"detector.yaml": cms_detector, "objects.yaml": cms_objects},
        )

        ctx = ExperimentContext("cms", experiments_dir=experiments_dir)
        assert ctx.detector["experiment"] == "cms"
        assert ctx.detector["collider"] == "LHC"
        assert "tight_muon" in ctx.objects

        defn = ctx.get_object_definition("tight_muon")
        assert defn["cuts"][0]["threshold"] == 26.0


# ============================================================
# AnalysisConfig extension tests
# ============================================================

class TestAnalysisConfigExtension:
    """Tests for AnalysisConfig experiment-related field extensions."""

    def test_experiment_key_loaded(self, tmp_path):
        """AnalysisConfig loads experiment key as attribute."""
        from gad.config.analysis import AnalysisConfig

        config_file = tmp_path / "analysis.yaml"
        config_file.write_text(
            "experiment: aleph\n"
            "signal_region:\n"
            "  name: SR\n"
        )
        cfg = AnalysisConfig(str(config_file))
        assert cfg.experiment == "aleph"

    def test_samples_config_loaded(self, tmp_path):
        """AnalysisConfig loads samples config dict."""
        from gad.config.analysis import AnalysisConfig

        config_file = tmp_path / "analysis.yaml"
        config_file.write_text(
            "samples:\n"
            "  config: samples.yaml\n"
            "signal_region:\n"
            "  name: SR\n"
        )
        cfg = AnalysisConfig(str(config_file))
        assert cfg.samples_config == {"config": "samples.yaml"}

    def test_samples_config_raw_path_mode(self, tmp_path):
        """AnalysisConfig loads raw path samples config."""
        from gad.config.analysis import AnalysisConfig

        config_file = tmp_path / "analysis.yaml"
        config_file.write_text(
            "samples:\n"
            "  path: /eos/data/\n"
            "  tree_name: t\n"
            "signal_region:\n"
            "  name: SR\n"
        )
        cfg = AnalysisConfig(str(config_file))
        assert cfg.samples_config["path"] == "/eos/data/"
        assert cfg.samples_config["tree_name"] == "t"

    def test_object_overrides_loaded(self, tmp_path):
        """AnalysisConfig loads object_overrides dict."""
        from gad.config.analysis import AnalysisConfig

        config_file = tmp_path / "analysis.yaml"
        config_file.write_text(
            "object_overrides:\n"
            "  good_track:\n"
            "    cuts:\n"
            "      - variable: ntpc\n"
            '        operator: ">="\n'
            "        threshold: 6\n"
            "signal_region:\n"
            "  name: SR\n"
        )
        cfg = AnalysisConfig(str(config_file))
        assert "good_track" in cfg.object_overrides
        assert cfg.object_overrides["good_track"]["cuts"][0]["threshold"] == 6

    def test_sqrt_s_loaded(self, tmp_path):
        """AnalysisConfig loads sqrt_s as float."""
        from gad.config.analysis import AnalysisConfig

        config_file = tmp_path / "analysis.yaml"
        config_file.write_text(
            "sqrt_s: 91.2\n"
            "signal_region:\n"
            "  name: SR\n"
        )
        cfg = AnalysisConfig(str(config_file))
        assert cfg.sqrt_s == 91.2

    def test_backward_compatibility_no_new_fields(self, mock_config_yaml):
        """Existing config without new fields still works with defaults."""
        from gad.config.analysis import AnalysisConfig

        config_path = mock_config_yaml()
        cfg = AnalysisConfig(config_path)

        # Original fields still work
        assert cfg.signal_region["name"] == "SR"
        assert cfg.partial_seed == 42
        assert cfg.allowed_reblind_count == 1

        # New fields default gracefully
        assert cfg.experiment is None
        assert cfg.samples_config is None
        assert cfg.object_overrides == {}
        assert cfg.sqrt_s is None
