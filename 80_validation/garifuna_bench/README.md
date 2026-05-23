# GarifunaBench

Evaluation harness for Garifuna-language ML systems. Built per M-P3.G
manifest. Templates: FormosanBench (Jun 2025), MEGA-RAG (PMC 2025),
Rodríguez et al. 2025 Galician CPT methodology.

## Scope

GarifunaBench is the measurement substrate for the Nisamina chatbot
(M-P3.A) and the Phase-5 Gemma-4-E4B-Nisamina fine-tune. It supports
five task types:

| Task | Input | Expected | Scoring |
|---|---|---|---|
| **mt_en_to_cab** | English sentence | Cayetano-normalized Garifuna gloss | exact-match + Cayetano-normalize + per-token foundry attestation |
| **mt_cab_to_en** | Garifuna sentence | English gloss | exact-match + token-level translate_sentence overlap |
| **vocab_recall** | English gloss | Garifuna headword | exact / fuzzy / synonym (synonym = foundry headwords sharing gloss) |
| **conversation_quality** | Multi-turn dialogue + chatbot responses | numeric 0-1 | citation-density + hallucination rate (MEGA-RAG style) |
| **pronunciation_grading** | Audio + expected text | numeric 0-1 | STUB — requires M-P3.D (Whisper-cab) integration |

## Non-self-graded contract

Plan v1 §6 rule 2: held-out sets are director- + community-graded only.

Each fixture item carries a `graded_by` field. Items with
`graded_by: engineer-scaffold-only-NOT-AUTHORITATIVE` (the starter
items in this scaffold) trigger `NotAuthoritativeError` if any caller
asks the harness for a "bench score" against them. Sanity-check output
is fine; authoritative scoring requires real grading metadata.

To make an item authoritative, set its `graded_by` field to one of:
- `director:Wamaraga:<date>`
- `commission:Garifuna_Commission_on_Education:<date>`
- `community:<community_or_partner_name>:<date>`

## Usage

```python
from garifuna_bench import BenchHarness, load_fixture

# Load held-out items
items = load_fixture("garifuna_bench/fixtures/held_out_starter_v0.jsonl")

# Wrap any chatbot as a callable: (item) -> response_text
def my_chatbot(item):
    # Real chatbot wired here at M-P3.A
    return "..."

harness = BenchHarness(items, chatbot_callable=my_chatbot)

# Sanity check — works on scaffold-only items
report = harness.sanity_check("vocab_recall")
print(report)

# Authoritative score — only runs if items are graded
try:
    result = harness.run_task("vocab_recall")
except NotAuthoritativeError as e:
    print(f"Need real grading first: {e}")
```

## Hallucination detector

`HallucinationDetector` implements the MEGA-RAG multi-evidence check:

```python
from garifuna_bench import HallucinationDetector

# At M-P3.A: pass a real MCP lookup_headword callable
det = HallucinationDetector(lookup_fn=mcp_lookup_headword)

report = det.check(
    response="The Garifuna word for 'cat' is mesu.",
    claimed_sources=["Hadel_vol_I_OCR", "garifuna_living_dictionary"],
)
print(report.score, report.grounded_tokens, report.flagged_tokens)
```

## Fixture curator guide

See `fixtures/README.md`.

## Status

| Component | Status |
|---|---|
| Harness skeleton | ✓ scaffold |
| Hallucination detector skeleton | ✓ scaffold (mock retrieval) |
| 5 task stubs | ✓ scaffold (mt_*, vocab_recall) / ⚠ stub (conversation_quality) / ✗ blocked (pronunciation_grading — M-P3.D) |
| 10-item held-out starter | ✓ Tier-5-attested, `engineer-scaffold-only-NOT-AUTHORITATIVE` |
| Real held-out items | ✗ director + commission + community work |
| Live MCP retrieval wiring | ✗ M-P3.A |
| Chatbot integration | ✗ M-P3.A |

*Buguya nuani Wamaraga.*
