"""Tests for resources + prompts."""
from __future__ import annotations

from nisamina_mcp.resources import (
    resource_foundry_v6, resource_vault, resource_attestation_matrix,
    resource_canonical_source_map, RESOURCE_REGISTRY,
    URI_FOUNDRY, URI_VAULT, URI_ATTESTATION, URI_SOURCE_MAP,
)
from nisamina_mcp.prompts.lesson_templates import (
    vocab_drill_prompt, sentence_breakdown_prompt, PROMPT_REGISTRY,
)


def test_resource_foundry_count(foundry_index):
    assert len(resource_foundry_v6(foundry_index)) == 33133


def test_resource_vault_count(foundry_index):
    assert len(resource_vault(foundry_index)) == 542


def test_resource_attestation_loads():
    assert len(resource_attestation_matrix()) > 0


def test_resource_source_map_filters_non_public():
    """Must exclude `license_pending`, `quarantine`, `archival_only` rows."""
    rows = resource_canonical_source_map()
    for r in rows:
        assert (r.get("status") or "").lower().startswith("public")


def test_resource_source_map_includes_wamaraga():
    """attr_001 Wamaraga (status `public_with_magarada_preliminary_gate`)
    must be included — the director is publishable for the V_VAULT/Songs
    contributions even though Magarada Stories is gated."""
    rows = resource_canonical_source_map()
    assert any(r.get("id") == "attr_001" for r in rows)


def test_resource_registry_uris():
    assert set(RESOURCE_REGISTRY) == {URI_FOUNDRY, URI_VAULT, URI_ATTESTATION, URI_SOURCE_MAP}


def test_vocab_drill_known_headword(foundry_index):
    p = vocab_drill_prompt(foundry_index, "ababagüda")
    assert p is not None
    assert "ababagüda" in p
    assert "foundry" in p.lower()


def test_vocab_drill_unknown_headword(foundry_index):
    p = vocab_drill_prompt(foundry_index, "zzzqqqxxx")
    assert p is None


def test_sentence_breakdown_renders(foundry_index):
    p = sentence_breakdown_prompt(foundry_index, "Ababagüdati kalíki gamísa tó.")
    assert "Ababagüdati" in p
    assert "foundry" in p.lower()
    # Tokens with no foundry match must be marked NOT IN FOUNDRY in the prompt
    p_bad = sentence_breakdown_prompt(foundry_index, "zzzqqq")
    assert "NOT IN FOUNDRY" in p_bad


def test_prompt_registry_has_both():
    assert set(PROMPT_REGISTRY) == {"vocab_drill", "sentence_breakdown"}
