# GarifunaBench Fixtures — curator guide

## Format

One JSON object per line. Required fields:

```json
{
  "id": "BENCH-V0-001",
  "task": "vocab_recall | mt_en_to_cab | mt_cab_to_en | conversation_quality | pronunciation_grading",
  "input": "<English gloss / Garifuna sentence / English sentence / etc.>",
  "expected": "<expected response>",
  "source_ids": ["<foundry source ID>", ...],
  "headword": "<Cayetano-normalized form, if applicable>",
  "tier": 5,
  "graded_by": "engineer-scaffold-only-NOT-AUTHORITATIVE | director:Wamaraga:YYYY-MM-DD | commission:Garifuna_Commission_on_Education:YYYY-MM-DD | community:<partner_name>:YYYY-MM-DD",
  "notes": "<free-text — provenance, caveats, dialect notes>"
}
```

## Plan v1 §6 rule 2 — never self-graded

Items with `graded_by: engineer-scaffold-only-NOT-AUTHORITATIVE` are
**SCAFFOLD ONLY**. The harness refuses to emit a bench score against
them (raises `NotAuthoritativeError`); only sanity checks are allowed.

To promote a starter item:

1. Director, Commission representative, or community partner verifies
   the (input, expected) pair is correct, complete, and culturally
   appropriate.
2. Set `graded_by` to:
   - `director:Wamaraga:YYYY-MM-DD`
   - `commission:Garifuna_Commission_on_Education:YYYY-MM-DD`
   - `community:<community_or_partner_name>:YYYY-MM-DD`
3. Add a `notes` line documenting what was verified.

## Gates for fixture items

Items MUST NOT include:
- Magarada-PRELIMINARY content (per consent_002 + [[project-magarada-preliminary-status]]).
- JW raw text or JW-only attestations (per [[quarantine-policy]]).
- Catatu midwife corpus content (consent_004 closed).
- Tier-C (single-source) content unless triangulated.

Items SHOULD prefer Tier-5 (V_VAULT director-attested) or Tier-A
(4+ public sources, gated, Cayetano-conformant, non-English).

## Files in this directory

| File | Items | Status |
|---|---:|---|
| `held_out_starter_v0.jsonl` | 10 | engineer-scaffold-only; awaiting director/commission/community grading |

*Buguya nuani Wamaraga.*
