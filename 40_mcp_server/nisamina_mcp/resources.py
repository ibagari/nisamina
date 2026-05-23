"""MCP resources — read-only browseable corpus slices.

Four resources, all public-safe (public_release filter + egress wrapper on
content fetch):

  - foundry_v6              The full public-release lexicon (33,133 records)
  - V_VAULT_355             The vault_attested Tier-5 subset (542 records)
  - attestation_matrix      Cross-attestation matrix (public-safe slice)
  - canonical_source_map    Attribution register (public-eligible contributors)

MCP resources are exposed via URIs the client can fetch by reference; the
content is loaded lazily on first access.
"""
from __future__ import annotations
import json
from pathlib import Path

from .egress import enforce_egress
from .foundry_loader import FoundryIndex, load as load_foundry

_NISAMINA_APP = Path(__file__).resolve().parent.parent.parent
ATTESTATION_PATH = _NISAMINA_APP / "30_lexicon" / "CROSS_ATTESTATION_MATRIX.jsonl"
ATTRIBUTION_PATH = _NISAMINA_APP / "00_governance" / "attribution_register.jsonl"

# MCP resource URI scheme — these strings are exposed to clients as identifiers.
URI_FOUNDRY = "nisamina://foundry_v6"
URI_VAULT = "nisamina://V_VAULT_355"
URI_ATTESTATION = "nisamina://attestation_matrix"
URI_SOURCE_MAP = "nisamina://canonical_source_map"


def resource_foundry_v6(index: FoundryIndex | None = None) -> list[dict]:
    """Full public-release foundry as a list of records. Egress-checked."""
    idx = index or load_foundry()
    return enforce_egress(list(idx.records), context="resource:foundry_v6")


def resource_vault(index: FoundryIndex | None = None) -> list[dict]:
    """V_VAULT vault_attested subset (542 records). Egress-checked."""
    idx = index or load_foundry()
    return enforce_egress(idx.vault_attested(), context="resource:V_VAULT_355")


def resource_attestation_matrix() -> list[dict]:
    """Cross-attestation matrix records. Egress-checked.

    The full file is 7.7 MB; this loader streams it into a list. If memory
    pressure becomes an issue at scale, switch to a generator-based MCP
    resource handler.
    """
    if not ATTESTATION_PATH.exists():
        return []
    out: list[dict] = []
    with ATTESTATION_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out.append(r)
    # The matrix entries are not foundry records per se (different schema), so
    # the egress wrapper will scan them but not trigger record-level rules
    # unless they happen to look like foundry records. Defense in depth either way.
    return enforce_egress(out, context="resource:attestation_matrix")


def resource_canonical_source_map() -> list[dict]:
    """Attribution register rows (contributors / sources / consent / status).

    Includes any row whose `status` starts with `public` (case-insensitive)
    — that covers `public` (36 rows) and `public_with_magarada_preliminary_gate`
    (attr_001 Wamaraga, who is fully publishable for the V_VAULT/Songs
    contributions even though the Magarada Stories component is gated).
    Excludes `license_pending` (publisher hasn't granted yet — can't claim
    attribution publicly), `quarantine`, `archival_only`, and any other
    non-public status.

    Distinct statuses in attribution_register as of 2026-05-22:
      36 public · 2 license_pending · 1 public_with_magarada_preliminary_gate
      · 1 quarantine · 1 archival_only.
    """
    if not ATTRIBUTION_PATH.exists():
        return []
    out: list[dict] = []
    with ATTRIBUTION_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            status = (row.get("status") or "").lower()
            if status.startswith("public"):
                out.append(row)
    return enforce_egress(out, context="resource:canonical_source_map")


RESOURCE_REGISTRY: dict[str, tuple[str, str]] = {
    # uri -> (display_name, mime_type)
    URI_FOUNDRY: ("foundry_v6 public lexicon (33,133 records)", "application/x-jsonlines"),
    URI_VAULT: ("V_VAULT vault-attested Tier-5 subset (542 records)", "application/x-jsonlines"),
    URI_ATTESTATION: ("Cross-attestation matrix", "application/x-jsonlines"),
    URI_SOURCE_MAP: ("Canonical source map (attribution register, public-eligible)", "application/x-jsonlines"),
}
