"""nisamina-mcp server — Anthropic MCP Python SDK entrypoint.

Registers the 5 Nisamina tools, 4 resources, and 2 lesson prompts on a
FastMCP server. Default transport is stdio (for `claude mcp add` + local pip
install). HTTP/SSE is available via `--transport sse` for the HF Space mirror
(deferred deployment per M-P2 manifest §4).

The `mcp` package is a runtime dependency declared in pyproject.toml. It is
imported lazily inside `main()` so the rest of the package (tools, egress,
loader, resources, prompts) can be imported and tested without it.
"""
from __future__ import annotations
import argparse
import json
import sys

from . import __version__
from .foundry_loader import load as load_foundry
from .tools.lookup_headword import lookup_headword as _lookup_headword
from .tools.cayetano_normalize import cayetano_normalize as _cayetano_normalize
from .tools.parse_morphology import parse_morphology as _parse_morphology
from .tools.translate_sentence import translate_sentence as _translate_sentence
from .tools.cite_sources import cite_sources as _cite_sources
from .resources import (
    resource_foundry_v6, resource_vault, resource_attestation_matrix,
    resource_canonical_source_map,
    URI_FOUNDRY, URI_VAULT, URI_ATTESTATION, URI_SOURCE_MAP,
)
from .prompts.lesson_templates import vocab_drill_prompt, sentence_breakdown_prompt


def _require_mcp():
    """Import the mcp SDK or raise a clear error."""
    try:
        from mcp.server.fastmcp import FastMCP
        return FastMCP
    except ImportError as e:
        raise SystemExit(
            "The `mcp` Python SDK is required to run the nisamina-mcp server.\n"
            "Install it with: pip install 'mcp>=1.0.0'  (or `pip install -e .` from this directory).\n"
            f"Original error: {e}"
        )


def build_server():
    """Construct + register a FastMCP instance. Raises if `mcp` SDK is absent."""
    FastMCP = _require_mcp()
    server = FastMCP(
        name="nisamina-mcp",
        instructions=(
            "Nisamina MCP — Garifuna corpus access. All 5 tools "
            "(`lookup_headword`, `cayetano_normalize`, `parse_morphology`, "
            "`translate_sentence`, `cite_sources`) operate over the foundry_v6 V0.2 "
            "lexicon (33,133 public-eligible headwords, Cayetano-1992-normalized). "
            "Every response is passed through the strip-linter egress gate; gated "
            "source IDs (JW / Magarada-PRELIMINARY / Catatu) cannot leak. "
            "Do NOT generate Garifuna words from training data — use these tools "
            "for grounded, attributed answers, and cite the returned `sources[]` "
            "fields in your reply."
        ),
    )

    # Load the foundry once at startup so every tool call uses the same index.
    foundry = load_foundry()

    # ---- 5 tools ----

    @server.tool(description=(
        "Search the Nisamina foundry_v6 lexicon by headword. `query` is the "
        "string to search. `mode` is one of 'exact' | 'prefix' | 'fuzzy'. "
        "`limit` caps the result count (default 10). Returns a list of foundry "
        "records (each with headword, senses, examples, sources, tier, ...)."
    ))
    def lookup_headword(query: str, mode: str = "exact", limit: int = 10) -> list[dict]:
        return _lookup_headword(foundry, query, mode=mode, limit=limit)  # type: ignore[arg-type]

    @server.tool(description=(
        "Apply Cayetano-1992 Garifuna orthographic normalization to `text`. "
        "Returns the normalized form, the change log, a conformance report, "
        "and a stress-pattern analysis. Use this BEFORE looking up a headword "
        "if the input may be in non-standard orthography."
    ))
    def cayetano_normalize(text: str) -> dict:
        return _cayetano_normalize(text)

    @server.tool(description=(
        "Look up `headword` and return its morphological decomposition "
        "(senses[].morphology + senses[].noun_class) from the foundry. "
        "Returns {found: bool, senses: [...]}. Does NOT generate morphology "
        "if the foundry has none — returns empty senses instead."
    ))
    def parse_morphology(headword: str) -> dict:
        return _parse_morphology(foundry, headword)

    @server.tool(description=(
        "Per-token gloss of a Garifuna `sentence` using foundry-attested "
        "entries only. Cayetano-normalizes each token, looks it up, returns "
        "matched_records + fuzzy candidates. Tokens with no match are flagged "
        "`unmatched: true` — do NOT invent a gloss for those."
    ))
    def translate_sentence(sentence: str, fuzzy_fallback: bool = True) -> dict:
        return _translate_sentence(foundry, sentence, fuzzy_fallback=fuzzy_fallback)

    @server.tool(description=(
        "Return the full attribution chain for `headword` — for each source ID "
        "in the foundry record, look up the contributors in attribution_register "
        "and return their names, roles, and consent status. Use this when "
        "citing the foundry in any user-facing answer."
    ))
    def cite_sources(headword: str) -> dict:
        return _cite_sources(foundry, headword)

    # ---- 4 resources ----

    @server.resource(URI_FOUNDRY, description="Full public-release foundry_v6 V0.2 lexicon (33,133 records).")
    def res_foundry() -> str:
        # Return as JSON-lines string so clients can stream-parse.
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in resource_foundry_v6(foundry))

    @server.resource(URI_VAULT, description="V_VAULT Tier-5 vault-attested subset (542 records).")
    def res_vault() -> str:
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in resource_vault(foundry))

    @server.resource(URI_ATTESTATION, description="Cross-attestation matrix (per-headword source-presence map).")
    def res_attestation() -> str:
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in resource_attestation_matrix())

    @server.resource(URI_SOURCE_MAP, description="Canonical contributor / source map (public-eligible rows of attribution_register).")
    def res_sources() -> str:
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in resource_canonical_source_map())

    # ---- 2 prompts ----

    @server.prompt(description=(
        "Walk a learner through a single Garifuna headword using the foundry's "
        "recorded senses + examples only. Refuses to invent additional content."
    ))
    def vocab_drill(headword: str) -> str:
        out = vocab_drill_prompt(foundry, headword)
        if out is None:
            return (
                f"Headword '{headword}' is not in the Nisamina public foundry. "
                f"Use the `lookup_headword` tool with mode='fuzzy' to find similar "
                f"recorded headwords; do NOT invent a definition."
            )
        return out

    @server.prompt(description=(
        "Per-token parse of a Garifuna sentence using foundry-attested glosses. "
        "Refuses to invent glosses for unmatched tokens."
    ))
    def sentence_breakdown(sentence: str) -> str:
        return sentence_breakdown_prompt(foundry, sentence)

    return server


def main() -> None:
    """Entrypoint. Parses transport flag, builds server, runs."""
    parser = argparse.ArgumentParser(
        prog="nisamina-mcp",
        description=f"nisamina-mcp v{__version__} — Garifuna corpus MCP server.",
    )
    parser.add_argument(
        "--transport", choices=["stdio", "sse"], default="stdio",
        help="MCP transport (stdio for local Claude Code / pip; sse for HF Space HTTP mirror).",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Bind host for sse transport (default 127.0.0.1).",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Bind port for sse transport (default 8000).",
    )
    parser.add_argument(
        "--version", action="version", version=f"nisamina-mcp {__version__}",
    )
    args = parser.parse_args()
    server = build_server()
    if args.transport == "stdio":
        # FastMCP.run() defaults to stdio.
        server.run()
    elif args.transport == "sse":
        # FastMCP supports sse via run(transport="sse"); host/port args are
        # passed through SDK-dependent options. If the installed mcp version
        # has a different signature, this branch will raise — surface and
        # document as the HF Space deferral acknowledged in M-P2 §4.
        try:
            server.run(transport="sse", host=args.host, port=args.port)
        except TypeError:
            print(
                "The installed mcp SDK does not accept transport='sse' / host / port "
                "via this signature. SSE deployment is deferred per M-P2 manifest §4 "
                "(HF Space mirror). Falling back to stdio.",
                file=sys.stderr,
            )
            server.run()


if __name__ == "__main__":
    main()
