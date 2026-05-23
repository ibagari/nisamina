# nisamina-mcp

MCP server exposing the **Nisamina Garifuna corpus** (foundry_v6 V0.2 — 33,133 public-eligible headwords, Cayetano-1992-normalized) to any MCP-compatible LLM client.

Every response passes through the `99_publish/strip_linter` egress gate — gated source IDs (JW / Magarada-PRELIMINARY / Catatu), internal-only fields, and Tier-C/X entries cannot leak.

## The 5 tools

| Tool | Purpose |
|---|---|
| `lookup_headword` | Exact / prefix / fuzzy search over foundry_v6 by `headword_normalized`. |
| `cayetano_normalize` | Apply Cayetano-1992 orthographic normalization + conformance + stress check. |
| `parse_morphology` | Extract morphology decomposition + noun-class from senses. |
| `translate_sentence` | Cayetano-normalize, tokenize, per-token lookup with source IDs. |
| `cite_sources` | Resolve a headword's source IDs to full contributor attribution chain. |

## The 4 resources

- `foundry_v6` — public-release slice of the lexicon (33,133 records).
- `V_VAULT_355` — V_VAULT vault-attested subset (Tier 5).
- `attestation_matrix` — cross-attestation matrix (public-safe slice).
- `canonical_source_map` — attribution_register (public-eligible contributors).

## Install

### From source (this repo)

```bash
cd nisamina-app/40_mcp_server
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Then either:

```bash
nisamina-mcp                                            # console script (after pip install)
# or
python3 server.py                                       # direct script
```

### Add to Claude Code

```bash
claude mcp add nisamina ./nisamina-app/40_mcp_server/server.py
```

## Distribution channels (per D-008)

1. **`pip install nisamina-mcp`** — sovereignty-maximal local install. Users run the server on their own machine; MCP clients (Claude Code, ChatGPT desktop, open-weight LLM via local MCP, future Phase 3 web chatbot) connect over stdio.
2. **HuggingFace Space HTTP/SSE mirror** — secondary, for casual remote users (deferred to a follow-up manifest).

## Egress contract (non-negotiable)

Every tool response is wrapped through `nisamina_mcp.egress.enforce_egress(...)`, which calls `99_publish/strip_linter.block_if_violations()` on the records before they leave the server. If any record carries:

- a truthy `jw_*`, `catatu_*`, `magarada_unverified` field;
- a Tier-C or Tier-X classification;
- a source ID matching the JW / Magarada / Catatu pattern modules;
- `public_release: false`;
- non-Cayetano-conformant `headword_normalized`;
- missing required attribution fields;

the response is blocked with `StripLinterError` before any data reaches the MCP client.

## Authority

- plan v1 §3 + Phase 2 (line 166-173)
- plan v1.1 §2.1 (distribution channels) + §2.3 (strip-linter egress)
- D-008 (distribution decision)
- D-016 (chatbot grounding layer)
- M-P2 manifest at `nisamina-app/90_supervisor/manifests/M-P2_mcp_server.md`

## License

CC-BY-NC-SA 4.0 (matches Nisamina platform and Ibagari Foundation framework).

*Buguya nuani Wamaraga.*
