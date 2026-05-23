# Nisamina — Garifuna Learning App

`garifunalearningacademy.com` · Ibagari Foundation (Delaware 501(c)(3)) · CC-BY-NC-SA 4.0 · low-resource · non-commercial · community-driven

This is the working tree for the Nisamina Garifuna app. Source of truth for design and decisions:

- **Plan v1:** `../Nisamina_Garifuna_Linguist/_SOA/RESEARCH_GROUNDED_APP_PLAN_v1_2026-05-21.md`
- **Plan v1.1 amendment (locked decisions):** `../Nisamina_Garifuna_Linguist/_SOA/RESEARCH_GROUNDED_APP_PLAN_v1_1_AMENDMENT_2026-05-21.md`
- **Corpus coverage truth:** `../Nisamina_Garifuna_Linguist/_SOA/audits/A-052_corpus_coverage_truth.md`

## Module map

| Folder | Purpose |
|---|---|
| `00_governance/` | CARE + FPIC + IDIL alignment; attribution + consent registries; license |
| `10_ingest/` | PDF/OCR/audio/ODS loaders; CANONICAL_SOURCE_MAP_v2 + FILE_LEDGER seed |
| `20_normalize/` | Cayetano 1992 NGC-Belize standardizer (`cayetano_1992.py` ported from V2) |
| `30_lexicon/` | Foundry v6 builder; cross-attestation matrix; JW re-mining policy; Magarada preliminary gate |
| `40_mcp_server/` | MCP Stdio + HTTP/SSE; tools/resources/prompts (distributed as `pip install nisamina-mcp` + HF Space mirror) |
| `50_app/` | Web app — Next.js frontend (Cloudflare Pages) + Django backend (HF Space) |
| `60_training/` | CPT + SFT pipelines (Rodríguez et al. ACL 2025 methodology) |
| `70_audio/` | MMS-cab wrapper + Whisper-cab fine-tune; `elder_voice_preservation/` archival-only |
| `80_validation/` | Director- and community-graded; held-out test sets; NEVER self-graded |
| `90_supervisor/` | Live-stream activity + manifest+audit register + decision log + supervisor findings |
| `99_publish/` | Webonary + Living Dictionaries + HuggingFace exports; strip linter |

## License

CC-BY-NC-SA 4.0 — see `00_governance/LICENSE`.

## Attribution

Every contributor is named in `00_governance/attribution_register.jsonl`. The register grows as Phase 1 ingestion reveals per-file authorship. Corrections from director and community are commits.

## Mission

Build a community-owned Garifuna dictionary + translator + reader + audio platform that uses every legally-cleared source in the drive, attributes everyone, never self-grades, and never re-runs the failure pattern of the prior 51-cycle in-session loop.

*Buguya nuani Wamaraga.*
