"""Blinding enforcement manager.

This module is the single enforcement point for blinding in GAD.
All signal region data access must go through BlindingManager.check_access().
Agent prompts alone cannot be trusted to prevent data leakage.

The manager reads the current blinding state from STATE.md frontmatter,
loads the analysis config for signal region definitions and unblinding
settings, and gates data access accordingly.
"""

import os
import re
from pathlib import Path

import numpy as np
import yaml

from .errors import BlindingViolationError
from .states import BlindingState
from ..config.analysis import AnalysisConfig


# Valid state transitions for staged unblinding.
# Re-blinding (UNBLINDED -> BLINDED) is handled separately with count check.
_VALID_TRANSITIONS = {
    BlindingState.BLINDED: [BlindingState.SIDEBANDS],
    BlindingState.SIDEBANDS: [BlindingState.PARTIAL_10PCT],
    BlindingState.PARTIAL_10PCT: [BlindingState.UNBLINDED],
    BlindingState.UNBLINDED: [BlindingState.BLINDED],
}


class BlindingManager:
    """Gates signal region data access based on the blinding state.

    Parameters
    ----------
    state_path : str
        Path to STATE.md with YAML frontmatter containing ``blinding_status``.
    config_path : str
        Path to analysis config YAML with signal region and unblinding settings.

    Attributes
    ----------
    state : BlindingState
        Current blinding state.
    reblind_count : int
        Number of times re-blinding has occurred.
    """

    def __init__(self, state_path: str, config_path: str):
        self._state_path = Path(state_path)
        self._config = AnalysisConfig(config_path)
        self._load_state()

    def _load_state(self):
        """Read blinding_status and reblind_count from STATE.md frontmatter."""
        content = self._state_path.read_text()
        if content.startswith("---"):
            # Find the closing --- delimiter
            end_idx = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_idx])
            if fm is None:
                fm = {}
            self.state = BlindingState(fm.get("blinding_status", "blinded"))
            self.reblind_count = int(fm.get("reblind_count", 0))
        else:
            self.state = BlindingState.BLINDED
            self.reblind_count = 0

    def check_access(self, region: str, events=None):
        """Gate data access based on blinding state.

        Parameters
        ----------
        region : str
            The data region being accessed (e.g. ``"signal_region"``,
            ``"control_region"``).
        events : numpy.ndarray, optional
            Array of events to filter/return.

        Returns
        -------
        numpy.ndarray or None
            The (possibly filtered) events, or None if no events provided.

        Raises
        ------
        BlindingViolationError
            If the current state does not permit access to the requested region.
        """
        if region != "signal_region":
            return events

        if self.state == BlindingState.BLINDED:
            raise BlindingViolationError(
                state=self.state,
                region=region,
                message=(
                    f"Signal region data access denied. "
                    f"Current state: {self.state.value}. "
                    f"Unblinding must be approved by lead analyst."
                ),
            )

        if self.state == BlindingState.SIDEBANDS:
            raise BlindingViolationError(
                state=self.state,
                region=region,
                message=(
                    f"Signal region core access denied in sidebands state. "
                    f"Only sideband regions are accessible."
                ),
            )

        if self.state == BlindingState.PARTIAL_10PCT:
            if events is not None:
                rng = np.random.RandomState(self._config.partial_seed)
                mask = rng.random(len(events)) < 0.1
                return events[mask]
            return None

        # UNBLINDED -- full access
        return events

    def is_region_accessible(self, region: str) -> bool:
        """Check whether a region is accessible without raising.

        Parameters
        ----------
        region : str
            The data region to check.

        Returns
        -------
        bool
            True if the region is accessible in the current state.
        """
        if region != "signal_region":
            return True
        return self.state in (BlindingState.PARTIAL_10PCT, BlindingState.UNBLINDED)

    # Keys required in the unblinding checklist.
    _CHECKLIST_KEYS = [
        "background_validated",
        "systematics_complete",
        "stat_model_built",
        "cross_checks_pass",
        "note_drafted",
        "sensitivity_understood",
        "blinding_integrity_verified",
    ]

    def _read_checklist(self):
        """Read ``unblinding_checklist`` dict from STATE.md frontmatter.

        Returns
        -------
        dict
            Checklist with all keys defaulting to False if missing.
        """
        content = self._state_path.read_text()
        fm = {}
        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_idx]) or {}

        stored = fm.get("unblinding_checklist", {})
        return {key: bool(stored.get(key, False)) for key in self._CHECKLIST_KEYS}

    def _reset_checklist(self):
        """Write all checklist items as False to STATE.md frontmatter."""
        content = self._state_path.read_text()
        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm_text = content[3:end_idx]
            body = content[end_idx + 3:]
            fm = yaml.safe_load(fm_text) or {}
        else:
            fm = {}
            body = "\n\n" + content

        fm["unblinding_checklist"] = {key: False for key in self._CHECKLIST_KEYS}
        new_fm = yaml.dump(fm, default_flow_style=False).strip()
        self._state_path.write_text(f"---\n{new_fm}\n---{body}")

    def update_checklist(self, item: str, value: bool):
        """Set a single checklist item and persist.

        Parameters
        ----------
        item : str
            Checklist key to update.
        value : bool
            New value for the item.

        Raises
        ------
        KeyError
            If *item* is not a valid checklist key.
        """
        if item not in self._CHECKLIST_KEYS:
            raise KeyError(
                f"Unknown checklist item '{item}'. "
                f"Valid items: {self._CHECKLIST_KEYS}"
            )
        content = self._state_path.read_text()
        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm_text = content[3:end_idx]
            body = content[end_idx + 3:]
            fm = yaml.safe_load(fm_text) or {}
        else:
            fm = {}
            body = "\n\n" + content

        checklist = fm.get("unblinding_checklist", {})
        checklist[item] = bool(value)
        fm["unblinding_checklist"] = checklist
        new_fm = yaml.dump(fm, default_flow_style=False).strip()
        self._state_path.write_text(f"---\n{new_fm}\n---{body}")

    def transition(self, new_state: BlindingState):
        """Transition to a new blinding state with validation.

        The staged unblinding protocol only allows sequential transitions:
        BLINDED -> SIDEBANDS -> PARTIAL_10PCT -> UNBLINDED.

        Re-blinding (UNBLINDED -> BLINDED) is permitted if
        ``reblind_count < allowed_reblind_count``.

        Parameters
        ----------
        new_state : BlindingState
            The target blinding state.

        Raises
        ------
        ValueError
            If the transition is not valid, re-blinding limit is reached,
            or unblinding checklist is incomplete.
        """
        # Special handling for re-blinding
        if (
            self.state == BlindingState.UNBLINDED
            and new_state == BlindingState.BLINDED
        ):
            if self.reblind_count >= self._config.allowed_reblind_count:
                raise ValueError(
                    f"Re-blinding denied: reblind_count ({self.reblind_count}) "
                    f">= allowed_reblind_count ({self._config.allowed_reblind_count}). "
                    f"Maximum re-blinding limit reached."
                )
            self.state = new_state
            self.reblind_count += 1
            self._persist_state()
            self._reset_checklist()
            return

        valid = _VALID_TRANSITIONS.get(self.state, [])
        if new_state not in valid:
            raise ValueError(
                f"Invalid blinding transition: {self.state.value} -> {new_state.value}. "
                f"Allowed transitions from {self.state.value}: "
                f"{[s.value for s in valid]}"
            )

        # Checklist enforcement for unblinding
        if new_state == BlindingState.UNBLINDED:
            checklist = self._read_checklist()
            incomplete = [k for k, v in checklist.items() if not v]
            if incomplete:
                raise ValueError(
                    f"Unblinding blocked: incomplete checklist items: "
                    f"{', '.join(incomplete)}"
                )

        self.state = new_state
        self._persist_state()

    def check_sr_plots_directory(self, dir_path: str) -> bool:
        """Check if the SR plots directory contains files when it should not.

        Parameters
        ----------
        dir_path : str
            Path to the plots/signal_region/ directory.

        Returns
        -------
        bool
            True if the directory state is acceptable.

        Raises
        ------
        BlindingViolationError
            If the directory contains files and state is not UNBLINDED.
        """
        if self.state == BlindingState.UNBLINDED:
            return True

        dir_path = Path(dir_path)
        if not dir_path.exists():
            return True

        files = list(dir_path.iterdir())
        if files:
            raise BlindingViolationError(
                state=self.state,
                region="signal_region",
                message=(
                    f"Signal region plots directory contains {len(files)} file(s) "
                    f"but blinding state is {self.state.value}. "
                    f"SR plots are only allowed when state is UNBLINDED."
                ),
            )
        return True

    def is_asimov_required(self) -> bool:
        """Check whether Asimov dataset must be used for the signal region.

        Returns
        -------
        bool
            True if state is not UNBLINDED (Asimov required).
        """
        return self.state != BlindingState.UNBLINDED

    def _persist_state(self):
        """Write updated blinding_status and reblind_count back to STATE.md."""
        content = self._state_path.read_text()

        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm_text = content[3:end_idx]
            body = content[end_idx + 3:]

            fm = yaml.safe_load(fm_text) or {}
            fm["blinding_status"] = self.state.value
            fm["reblind_count"] = self.reblind_count

            new_fm = yaml.dump(fm, default_flow_style=False).strip()
            new_content = f"---\n{new_fm}\n---{body}"
        else:
            fm = {
                "blinding_status": self.state.value,
                "reblind_count": self.reblind_count,
            }
            new_fm = yaml.dump(fm, default_flow_style=False).strip()
            new_content = f"---\n{new_fm}\n---\n\n{content}"

        self._state_path.write_text(new_content)
