"""Explicit optional HTTP probe. No automatic execution on fact exports."""

from typing import Any
import urllib.request
import urllib.error
from cil_domain.jobs.freshness import FreshnessPolicy


def verify_url_live(url: str, timeout: float = 3.0) -> dict[str, Any]:
    """Perform live network probing via HTTP HEAD request (Local-first / optional)."""
    if not FreshnessPolicy.validate_url_syntax(url):
        return {"status": "INVALID_SYNTAX", "reachable": False, "http_code": None}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CompanyIntel/0.1 LiveProvenanceVerifier",
        "Accept": "*/*",
    }
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "status": "REACHABLE",
                "reachable": True,
                "http_code": response.status,
            }
    except urllib.error.HTTPError as e:
        if e.code == 405:
            try:
                get_req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(get_req, timeout=timeout) as get_resp:
                    return {
                        "status": "REACHABLE",
                        "reachable": True,
                        "http_code": get_resp.status,
                    }
            except Exception as inner_e:
                return {
                    "status": f"HTTP_{getattr(inner_e, 'code', 'ERROR')}",
                    "reachable": False,
                    "http_code": getattr(inner_e, "code", None),
                    "error": str(inner_e),
                }
        return {"status": f"HTTP_{e.code}", "reachable": False, "http_code": e.code}
    except Exception as e:
        return {
            "status": "NETWORK_UNREACHABLE",
            "reachable": False,
            "http_code": None,
            "error": str(e),
        }
