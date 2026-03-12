"""Post-unblinding problem classifier.

Categorises anomalies found after unblinding into Category A (serious,
requires re-blinding), Category B (moderate, may require re-blinding),
or Category C (minor, document and proceed).  Problems are persisted
to ``post_unblinding_problems`` in STATE.md frontmatter.
"""

from datetime import datetime
from pathlib import Path

import yaml


class PostUnblindingClassifier:
    """Classify and persist post-unblinding problems.

    Parameters
    ----------
    state_path : str or Path
        Path to STATE.md with YAML frontmatter.
    """

    CATEGORIES = {
        "A": "Serious problem requiring re-blinding and re-analysis",
        "B": "Moderate problem that may require re-blinding",
        "C": "Minor issue -- document and proceed",
    }

    def __init__(self, state_path):
        self._state_path = Path(state_path)

    def classify(self, description: str, category: str, resolution=None):
        """Classify a post-unblinding problem.

        Parameters
        ----------
        description : str
            Human-readable description of the problem.
        category : str
            One of ``"A"``, ``"B"``, ``"C"``.
        resolution : str, optional
            Proposed or applied resolution.

        Returns
        -------
        dict
            Problem record with category, description, resolution, timestamp.

        Raises
        ------
        ValueError
            If *category* is not in ``("A", "B", "C")``.
        """
        if category not in self.CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Must be one of: "
                f"{', '.join(sorted(self.CATEGORIES))}"
            )

        problem = {
            "category": category,
            "description": description,
            "resolution": resolution,
            "timestamp": datetime.now().isoformat(),
        }
        self._persist_problem(problem)
        return problem

    def get_problems(self):
        """Read all post-unblinding problems from STATE.md frontmatter.

        Returns
        -------
        list[dict]
            List of problem records (empty if none recorded).
        """
        content = self._state_path.read_text()
        fm = {}
        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_idx]) or {}
        return fm.get("post_unblinding_problems", [])

    def _persist_problem(self, problem):
        """Append a problem to ``post_unblinding_problems`` in STATE.md."""
        content = self._state_path.read_text()
        if content.startswith("---"):
            end_idx = content.index("---", 3)
            fm_text = content[3:end_idx]
            body = content[end_idx + 3:]
            fm = yaml.safe_load(fm_text) or {}
        else:
            fm = {}
            body = "\n\n" + content

        problems = fm.get("post_unblinding_problems", [])
        problems.append(problem)
        fm["post_unblinding_problems"] = problems

        new_fm = yaml.dump(fm, default_flow_style=False).strip()
        self._state_path.write_text(f"---\n{new_fm}\n---{body}")
