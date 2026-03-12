"""Comprehensive tests for the blinding enforcement module.

Tests cover:
- BlindingState enum values and transitions
- BlindingViolationError exception attributes
- AnalysisConfig loading
- BlindingManager.check_access for all states and regions
- BlindingManager.transition validation (staged unblinding)
- SR plots directory enforcement
- Asimov requirement flag
- 10% partial unblinding reproducibility
- Re-blinding limits
"""

import os
import numpy as np
import pytest

from gad.blinding.states import BlindingState
from gad.blinding.errors import BlindingViolationError
from gad.blinding.module import BlindingManager
from gad.config.analysis import AnalysisConfig


# ============================================================
# BlindingState enum tests
# ============================================================

class TestBlindingState:
    """Tests for the BlindingState enum."""

    def test_blinded_state_exists(self):
        assert BlindingState.BLINDED.value == "blinded"

    def test_sidebands_state_exists(self):
        assert BlindingState.SIDEBANDS.value == "sidebands"

    def test_partial_10pct_state_exists(self):
        assert BlindingState.PARTIAL_10PCT.value == "partial_10pct"

    def test_unblinded_state_exists(self):
        assert BlindingState.UNBLINDED.value == "unblinded"

    def test_construct_from_string(self):
        assert BlindingState("blinded") == BlindingState.BLINDED
        assert BlindingState("sidebands") == BlindingState.SIDEBANDS
        assert BlindingState("partial_10pct") == BlindingState.PARTIAL_10PCT
        assert BlindingState("unblinded") == BlindingState.UNBLINDED

    def test_invalid_state_raises(self):
        with pytest.raises(ValueError):
            BlindingState("invalid_state")


# ============================================================
# BlindingViolationError tests
# ============================================================

class TestBlindingViolationError:
    """Tests for the BlindingViolationError exception."""

    def test_is_exception(self):
        err = BlindingViolationError(
            state=BlindingState.BLINDED,
            region="signal_region",
            message="Access denied"
        )
        assert isinstance(err, Exception)

    def test_stores_state(self):
        err = BlindingViolationError(
            state=BlindingState.BLINDED,
            region="signal_region",
            message="Access denied"
        )
        assert err.state == BlindingState.BLINDED

    def test_stores_region(self):
        err = BlindingViolationError(
            state=BlindingState.SIDEBANDS,
            region="signal_region",
            message="SR blocked"
        )
        assert err.region == "signal_region"

    def test_stores_message(self):
        err = BlindingViolationError(
            state=BlindingState.BLINDED,
            region="signal_region",
            message="Custom message"
        )
        assert str(err) == "Custom message"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(BlindingViolationError) as exc_info:
            raise BlindingViolationError(
                state=BlindingState.BLINDED,
                region="signal_region",
                message="Blocked"
            )
        assert exc_info.value.state == BlindingState.BLINDED


# ============================================================
# AnalysisConfig tests
# ============================================================

class TestAnalysisConfig:
    """Tests for the AnalysisConfig loader."""

    def test_loads_signal_region(self, mock_config_yaml):
        config_path = mock_config_yaml()
        config = AnalysisConfig(config_path)
        assert config.signal_region["name"] == "SR"

    def test_loads_signal_region_cuts(self, mock_config_yaml):
        config_path = mock_config_yaml()
        config = AnalysisConfig(config_path)
        assert len(config.signal_region["cuts"]) == 2

    def test_loads_partial_seed(self, mock_config_yaml):
        config_path = mock_config_yaml(partial_seed=99)
        config = AnalysisConfig(config_path)
        assert config.partial_seed == 99

    def test_loads_allowed_reblind_count(self, mock_config_yaml):
        config_path = mock_config_yaml(allowed_reblind_count=2)
        config = AnalysisConfig(config_path)
        assert config.allowed_reblind_count == 2

    def test_default_partial_seed(self, tmp_path):
        config_file = tmp_path / "minimal.yaml"
        config_file.write_text("signal_region:\n  name: SR\n")
        config = AnalysisConfig(str(config_file))
        assert config.partial_seed == 42

    def test_default_allowed_reblind_count(self, tmp_path):
        config_file = tmp_path / "minimal.yaml"
        config_file.write_text("signal_region:\n  name: SR\n")
        config = AnalysisConfig(str(config_file))
        assert config.allowed_reblind_count == 1


# ============================================================
# BlindingManager core enforcement tests
# ============================================================

class TestBlindingManagerAccess:
    """Tests for BlindingManager.check_access."""

    def test_blinded_sr_raises(self, mock_state_md, mock_config_yaml, mock_events):
        """SR access when blinded raises BlindingViolationError."""
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        with pytest.raises(BlindingViolationError):
            mgr.check_access("signal_region", events=mock_events)

    def test_blinded_cr_allowed(self, mock_state_md, mock_config_yaml, mock_events):
        """Control region access always allowed regardless of state."""
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        result = mgr.check_access("control_region", events=mock_events)
        assert np.array_equal(result, mock_events)

    def test_sidebands_sr_raises(self, mock_state_md, mock_config_yaml, mock_events):
        """SR core still blocked in sidebands state."""
        mgr = BlindingManager(mock_state_md("sidebands"), mock_config_yaml())
        with pytest.raises(BlindingViolationError):
            mgr.check_access("signal_region", events=mock_events)

    def test_partial_10pct_returns_subset(self, mock_state_md, mock_config_yaml, mock_events):
        """PARTIAL_10PCT returns ~10% of events."""
        mgr = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml())
        result = mgr.check_access("signal_region", events=mock_events)
        # Should return approximately 10 events from 100 (allow some variance)
        assert 1 <= len(result) <= 30
        assert len(result) < len(mock_events)

    def test_unblinded_returns_all(self, mock_state_md, mock_config_yaml, mock_events):
        """UNBLINDED returns all events."""
        mgr = BlindingManager(mock_state_md("unblinded"), mock_config_yaml())
        result = mgr.check_access("signal_region", events=mock_events)
        assert np.array_equal(result, mock_events)

    def test_check_access_no_events_blinded_raises(self, mock_state_md, mock_config_yaml):
        """SR access without events still raises when blinded."""
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        with pytest.raises(BlindingViolationError):
            mgr.check_access("signal_region")

    def test_check_access_no_events_unblinded_ok(self, mock_state_md, mock_config_yaml):
        """SR access without events returns None when unblinded."""
        mgr = BlindingManager(mock_state_md("unblinded"), mock_config_yaml())
        result = mgr.check_access("signal_region")
        assert result is None


# ============================================================
# Reproducibility tests
# ============================================================

class TestBlindingReproducibility:
    """Tests for 10% partial unblinding reproducibility."""

    def test_same_seed_same_subset(self, mock_state_md, mock_config_yaml, mock_events):
        """Two calls with same events and same seed produce identical subsets."""
        mgr = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml(partial_seed=42))
        result1 = mgr.check_access("signal_region", events=mock_events)
        result2 = mgr.check_access("signal_region", events=mock_events)
        assert np.array_equal(result1, result2)

    def test_different_seed_different_subset(self, mock_state_md, mock_config_yaml, mock_events):
        """Different config seeds produce different subsets."""
        mgr1 = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml(partial_seed=42))
        mgr2 = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml(partial_seed=99))
        result1 = mgr1.check_access("signal_region", events=mock_events)
        result2 = mgr2.check_access("signal_region", events=mock_events)
        # With different seeds, subsets should differ (probabilistically certain for 100 events)
        assert not np.array_equal(result1, result2)


# ============================================================
# State transition tests
# ============================================================

class TestBlindingTransitions:
    """Tests for BlindingManager.transition validation."""

    def test_blinded_to_sidebands(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        mgr.transition(BlindingState.SIDEBANDS)
        assert mgr.state == BlindingState.SIDEBANDS

    def test_sidebands_to_partial(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("sidebands"), mock_config_yaml())
        mgr.transition(BlindingState.PARTIAL_10PCT)
        assert mgr.state == BlindingState.PARTIAL_10PCT

    def test_partial_to_unblinded(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(
            mock_state_md("partial_10pct", checklist_complete=True),
            mock_config_yaml(),
        )
        mgr.transition(BlindingState.UNBLINDED)
        assert mgr.state == BlindingState.UNBLINDED

    def test_skip_blinded_to_unblinded_raises(self, mock_state_md, mock_config_yaml):
        """Skipping stages not allowed."""
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        with pytest.raises(ValueError, match="Invalid blinding transition"):
            mgr.transition(BlindingState.UNBLINDED)

    def test_skip_blinded_to_partial_raises(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        with pytest.raises(ValueError, match="Invalid blinding transition"):
            mgr.transition(BlindingState.PARTIAL_10PCT)

    def test_reblind_succeeds_first_time(self, mock_state_md, mock_config_yaml):
        """Re-blinding for Category B succeeds when reblind_count < allowed."""
        mgr = BlindingManager(mock_state_md("unblinded", reblind_count=0), mock_config_yaml())
        mgr.transition(BlindingState.BLINDED)
        assert mgr.state == BlindingState.BLINDED

    def test_reblind_fails_when_limit_reached(self, mock_state_md, mock_config_yaml):
        """Re-blinding rejected when reblind_count >= allowed_reblind_count."""
        mgr = BlindingManager(
            mock_state_md("unblinded", reblind_count=1),
            mock_config_yaml(allowed_reblind_count=1)
        )
        with pytest.raises(ValueError, match="[Rr]e-blinding"):
            mgr.transition(BlindingState.BLINDED)

    def test_transition_persists_to_state_md(self, mock_state_md, mock_config_yaml):
        """Transition writes the new state back to STATE.md."""
        state_path = mock_state_md("blinded")
        mgr = BlindingManager(state_path, mock_config_yaml())
        mgr.transition(BlindingState.SIDEBANDS)
        # Re-read the file and verify
        with open(state_path) as f:
            content = f.read()
        assert "sidebands" in content


# ============================================================
# Checklist enforcement tests
# ============================================================

class TestChecklistEnforcement:
    """Tests for unblinding checklist enforcement in BlindingManager."""

    @pytest.fixture
    def state_with_checklist(self, tmp_path):
        """Create STATE.md with unblinding_checklist in frontmatter."""
        def _create(checklist=None, blinding_status="partial_10pct", reblind_count=0):
            state_file = tmp_path / "STATE.md"
            if checklist is None:
                checklist = {
                    "background_validated": False,
                    "systematics_complete": False,
                    "stat_model_built": False,
                    "cross_checks_pass": False,
                    "note_drafted": False,
                    "sensitivity_understood": False,
                    "blinding_integrity_verified": False,
                }
            import yaml
            fm = {
                "gsd_state_version": 1.0,
                "blinding_status": blinding_status,
                "reblind_count": reblind_count,
                "unblinding_checklist": checklist,
            }
            fm_text = yaml.dump(fm, default_flow_style=False).strip()
            content = f"---\n{fm_text}\n---\n\n# Project State\n"
            state_file.write_text(content)
            return str(state_file)
        return _create

    def test_transition_to_unblinded_blocked_if_checklist_incomplete(
        self, state_with_checklist, mock_config_yaml
    ):
        """transition(UNBLINDED) raises ValueError when any checklist item is False."""
        checklist = {
            "background_validated": True,
            "systematics_complete": True,
            "stat_model_built": True,
            "cross_checks_pass": False,  # incomplete
            "note_drafted": True,
            "sensitivity_understood": True,
            "blinding_integrity_verified": True,
        }
        state_path = state_with_checklist(checklist=checklist)
        mgr = BlindingManager(state_path, mock_config_yaml())
        with pytest.raises(ValueError, match="cross_checks_pass"):
            mgr.transition(BlindingState.UNBLINDED)

    def test_transition_to_unblinded_allowed_if_checklist_complete(
        self, state_with_checklist, mock_config_yaml
    ):
        """transition(UNBLINDED) succeeds when all checklist items are True."""
        checklist = {
            "background_validated": True,
            "systematics_complete": True,
            "stat_model_built": True,
            "cross_checks_pass": True,
            "note_drafted": True,
            "sensitivity_understood": True,
            "blinding_integrity_verified": True,
        }
        state_path = state_with_checklist(checklist=checklist)
        mgr = BlindingManager(state_path, mock_config_yaml())
        mgr.transition(BlindingState.UNBLINDED)
        assert mgr.state == BlindingState.UNBLINDED

    def test_checklist_resets_on_reblinding(
        self, state_with_checklist, mock_config_yaml
    ):
        """After re-blinding, all checklist items reset to False."""
        checklist = {
            "background_validated": True,
            "systematics_complete": True,
            "stat_model_built": True,
            "cross_checks_pass": True,
            "note_drafted": True,
            "sensitivity_understood": True,
            "blinding_integrity_verified": True,
        }
        state_path = state_with_checklist(
            checklist=checklist, blinding_status="unblinded", reblind_count=0
        )
        mgr = BlindingManager(state_path, mock_config_yaml())
        mgr.transition(BlindingState.BLINDED)

        # Read back and verify checklist is all False
        import yaml
        content = open(state_path).read()
        end_idx = content.index("---", 3)
        fm = yaml.safe_load(content[3:end_idx])
        cl = fm["unblinding_checklist"]
        assert all(v is False for v in cl.values()), f"Checklist not reset: {cl}"

    def test_checklist_not_required_for_non_unblinded_transitions(
        self, state_with_checklist, mock_config_yaml
    ):
        """Transition to SIDEBANDS/PARTIAL_10PCT works without checklist."""
        # Use blinded state with no checklist at all
        state_path = state_with_checklist(
            checklist={}, blinding_status="blinded"
        )
        mgr = BlindingManager(state_path, mock_config_yaml())
        mgr.transition(BlindingState.SIDEBANDS)
        assert mgr.state == BlindingState.SIDEBANDS


# ============================================================
# is_region_accessible tests
# ============================================================

class TestIsRegionAccessible:
    """Tests for BlindingManager.is_region_accessible."""

    def test_cr_always_accessible(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        assert mgr.is_region_accessible("control_region") is True

    def test_sr_not_accessible_blinded(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        assert mgr.is_region_accessible("signal_region") is False

    def test_sr_not_accessible_sidebands(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("sidebands"), mock_config_yaml())
        assert mgr.is_region_accessible("signal_region") is False

    def test_sr_accessible_partial(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml())
        assert mgr.is_region_accessible("signal_region") is True

    def test_sr_accessible_unblinded(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("unblinded"), mock_config_yaml())
        assert mgr.is_region_accessible("signal_region") is True


# ============================================================
# SR plots directory enforcement tests
# ============================================================

class TestSRPlotsEnforcement:
    """Tests for check_sr_plots_directory."""

    def test_empty_dir_ok_when_blinded(self, mock_state_md, mock_config_yaml, mock_sr_plots_dir):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        result = mgr.check_sr_plots_directory(mock_sr_plots_dir)
        assert result is True

    def test_files_in_dir_raises_when_blinded(self, mock_state_md, mock_config_yaml, mock_sr_plots_dir):
        # Create a file in the SR plots directory
        with open(os.path.join(mock_sr_plots_dir, "plot.png"), "w") as f:
            f.write("fake plot")
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        with pytest.raises(BlindingViolationError):
            mgr.check_sr_plots_directory(mock_sr_plots_dir)

    def test_files_in_dir_raises_when_sidebands(self, mock_state_md, mock_config_yaml, mock_sr_plots_dir):
        with open(os.path.join(mock_sr_plots_dir, "plot.png"), "w") as f:
            f.write("fake plot")
        mgr = BlindingManager(mock_state_md("sidebands"), mock_config_yaml())
        with pytest.raises(BlindingViolationError):
            mgr.check_sr_plots_directory(mock_sr_plots_dir)

    def test_files_in_dir_ok_when_unblinded(self, mock_state_md, mock_config_yaml, mock_sr_plots_dir):
        with open(os.path.join(mock_sr_plots_dir, "plot.png"), "w") as f:
            f.write("fake plot")
        mgr = BlindingManager(mock_state_md("unblinded"), mock_config_yaml())
        result = mgr.check_sr_plots_directory(mock_sr_plots_dir)
        assert result is True


# ============================================================
# Asimov enforcement tests
# ============================================================

class TestAsimovEnforcement:
    """Tests for is_asimov_required."""

    def test_asimov_required_when_blinded(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("blinded"), mock_config_yaml())
        assert mgr.is_asimov_required() is True

    def test_asimov_required_when_sidebands(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("sidebands"), mock_config_yaml())
        assert mgr.is_asimov_required() is True

    def test_asimov_required_when_partial(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("partial_10pct"), mock_config_yaml())
        assert mgr.is_asimov_required() is True

    def test_asimov_not_required_when_unblinded(self, mock_state_md, mock_config_yaml):
        mgr = BlindingManager(mock_state_md("unblinded"), mock_config_yaml())
        assert mgr.is_asimov_required() is False
