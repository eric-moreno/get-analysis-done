"""Blinding violation error definitions.

BlindingViolationError is raised whenever an agent attempts to access
signal region data in a state that does not permit it. This is a hard
error -- the agent must stop immediately.
"""

from .states import BlindingState


class BlindingViolationError(Exception):
    """Raised when blinding policy denies data access.

    Attributes:
        state:   The current BlindingState when the violation occurred.
        region:  The data region that was requested.
        message: Human-readable description of the violation.
    """

    def __init__(self, *, state: BlindingState, region: str, message: str):
        super().__init__(message)
        self.state = state
        self.region = region
