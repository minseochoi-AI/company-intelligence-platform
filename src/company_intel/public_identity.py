"""Evidence-preserving public-sector entity linkage.

Names are useful for candidates but are never an automatic entity join.  Korean
MPM names and Czech MPSV employer records deliberately follow separate rules.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class IdentityLink:
    provider_entity_id: str | None
    canonical_entity_id: str | None
    status: str
    method: str
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _name(value: object) -> str:
    return re.sub(r"[^\w가-힣]+", "", str(value or "").casefold())


def classify_link_status(link: IdentityLink | Mapping[str, Any]) -> str:
    status = link.status if isinstance(link, IdentityLink) else str(link.get("status") or "unresolved")
    return status if status in {"linked", "candidate", "unresolved", "conflict"} else "unresolved"


def link_mpsv_ares(mpsv_employer: Mapping[str, Any], ares_record: Mapping[str, Any] | None) -> IdentityLink:
    """Join a Czech vacancy employer to ARES only on an exact IČO match."""

    ico = str(mpsv_employer.get("ico") or "").strip()
    ares_ico = str((ares_record or {}).get("ico") or "").strip()
    if ico and ares_ico and ico == ares_ico:
        return IdentityLink(f"ICO:{ico}", f"ICO:{ares_ico}", "linked", "ico_exact", {"ico": ico})
    if ico and ares_ico:
        return IdentityLink(f"ICO:{ico}", None, "conflict", "ico_mismatch", {"mpsv_ico": ico, "ares_ico": ares_ico})
    return IdentityLink(f"ICO:{ico}" if ico else None, None, "unresolved", "ico_missing", {"ico": ico or None})


def link_mpm_alio(
    mpm_record: Mapping[str, Any], alio_record: Mapping[str, Any] | None, *, verified_aliases: Mapping[str, str] | None = None
) -> IdentityLink:
    """Return an exact/verified link or a non-selectable name candidate."""

    name = str(mpm_record.get("institution_name") or mpm_record.get("insttname") or "").strip()
    alio = alio_record or {}
    mpm_id = str(mpm_record.get("institution_id") or mpm_record.get("instt_id") or "").strip()
    alio_id = str(alio.get("apbaId") or alio.get("apba_id") or "").strip()
    if mpm_id and alio_id and mpm_id == alio_id:
        return IdentityLink(f"MPM:{mpm_id}", f"ALIO:{alio_id}", "linked", "official_id_exact", {"institution_id": mpm_id})
    aliases = {_name(key): value for key, value in (verified_aliases or {}).items()}
    if name and _name(name) in aliases:
        canonical = aliases[_name(name)]
        return IdentityLink(None, canonical, "linked", "verified_alias", {"institution_name": name})
    alio_name = str(alio.get("apbaNa") or alio.get("title") or "").strip()
    if name and alio_name and _name(name) == _name(alio_name):
        return IdentityLink(None, None, "candidate", "name_candidate", {"mpm_name": name, "alio_name": alio_name})
    return IdentityLink(None, None, "unresolved", "no_verified_identifier", {"institution_name": name or None})
