"""Citation verification via INSPIRE-HEP REST API."""

import logging
import re
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

INSPIRE_API = "https://inspirehep.net/api"
REQUEST_TIMEOUT = 10


def verify_citation(entry: dict) -> dict:
    """Verify a single citation entry against INSPIRE-HEP.

    Tries DOI first, then arXiv eprint, then INSPIRE record URL.

    Parameters
    ----------
    entry : dict
        Citation dict with optional keys: doi, eprint, url, title.

    Returns
    -------
    dict
        {"verified": bool, "method": str, "details": str}
    """
    doi = entry.get("doi")
    eprint = entry.get("eprint")
    url = entry.get("url", "")

    # Try DOI lookup
    if doi:
        try:
            resp = requests.get(
                f"{INSPIRE_API}/doi/{doi}", timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                return {"verified": True, "method": "DOI", "details": f"DOI {doi} found"}
        except requests.RequestException as exc:
            return {"verified": False, "method": "DOI", "details": f"Error: {exc}"}

    # Try arXiv lookup
    if eprint:
        try:
            resp = requests.get(
                f"{INSPIRE_API}/arxiv/{eprint}", timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                return {"verified": True, "method": "arXiv", "details": f"arXiv {eprint} found"}
        except requests.RequestException as exc:
            return {"verified": False, "method": "arXiv", "details": f"Error: {exc}"}

    # Try INSPIRE record number from URL
    if "inspirehep.net" in url:
        try:
            # Extract record id from URL like https://inspirehep.net/literature/12345
            parts = url.rstrip("/").split("/")
            record_id = parts[-1]
            resp = requests.get(
                f"{INSPIRE_API}/literature/{record_id}", timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                return {"verified": True, "method": "INSPIRE", "details": f"Record {record_id} found"}
        except requests.RequestException as exc:
            return {"verified": False, "method": "INSPIRE", "details": f"Error: {exc}"}

    return {"verified": False, "method": "none", "details": "No verifiable identifiers"}


def verify_bibliography(bib_entries: list) -> dict:
    """Verify all entries in a bibliography.

    Parameters
    ----------
    bib_entries : list[dict]
        List of citation dicts.

    Returns
    -------
    dict
        {"total": int, "verified_count": int, "failed_count": int,
         "verified": list, "failed": list}
    """
    verified = []
    failed = []
    for entry in bib_entries:
        result = verify_citation(entry)
        entry_result = {**entry, **result}
        if result["verified"]:
            verified.append(entry_result)
        else:
            failed.append(entry_result)

    return {
        "total": len(bib_entries),
        "verified_count": len(verified),
        "failed_count": len(failed),
        "verified": verified,
        "failed": failed,
    }


def collect_citations_from_bib(bib_path: str) -> list:
    """Parse BibTeX file and extract citation entries for verification.

    Parameters
    ----------
    bib_path : str
        Path to .bib file.

    Returns
    -------
    list[dict]
        List of citation dicts with cite_key and optional doi, eprint, title, url fields.
    """
    path = Path(bib_path)
    if not path.exists():
        logger.warning("BibTeX file not found: %s", bib_path)
        return []

    content = path.read_text()
    entries = []
    for match in re.finditer(r'@\w+\{([^,]+),\s*(.*?)\n\}', content, re.DOTALL):
        key = match.group(1).strip()
        body = match.group(2)
        entry = {"cite_key": key}
        for field_match in re.finditer(
            r'(\w+)\s*=\s*\{(?:\{([^}]*)\}|([^}]*))\}', body
        ):
            field_name = field_match.group(1).lower()
            field_value = (field_match.group(2) or field_match.group(3) or "").strip()
            if field_name in ("doi", "eprint", "title", "url"):
                entry[field_name] = field_value
        entries.append(entry)
    return entries


def collect_citations_from_yaml(yaml_path: str) -> list:
    """Read citation entries from a references YAML or BibTeX file.

    If the file has a .bib extension, delegates to collect_citations_from_bib().

    Parameters
    ----------
    yaml_path : str
        Path to references YAML or BibTeX file.

    Returns
    -------
    list[dict]
        List of citation dicts with doi, eprint, title fields.
    """
    path = Path(yaml_path)
    if not path.exists():
        logger.warning("References file not found: %s", yaml_path)
        return []

    if path.suffix == ".bib":
        return collect_citations_from_bib(str(path))

    with open(path) as fh:
        data = yaml.safe_load(fh)

    if data is None:
        return []

    # Support both flat list and nested under 'references' key
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "references" in data:
        return data["references"]

    return []
