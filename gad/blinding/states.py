"""Blinding state definitions for staged unblinding protocol.

The blinding protocol enforces a strict sequence:
  BLINDED -> SIDEBANDS -> PARTIAL_10PCT -> UNBLINDED

Skipping stages is not allowed. Re-blinding (UNBLINDED -> BLINDED) is
permitted once for Category B problems.
"""

from enum import Enum


class BlindingState(Enum):
    """Blinding states for the staged unblinding protocol.

    Values match the strings stored in STATE.md frontmatter
    under the ``blinding_status`` field.
    """

    BLINDED = "blinded"
    SIDEBANDS = "sidebands"
    PARTIAL_10PCT = "partial_10pct"
    UNBLINDED = "unblinded"
