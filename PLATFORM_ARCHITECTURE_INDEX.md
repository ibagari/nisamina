# Nisamina V3 Platform Architecture Index

**Authority:** F-046 + F-047 (supervisor S14 consolidated) + D-038 + D-040 (engineer-executes-meta per director directive 2026-05-23 "apply all supervisor fixes")
**Re-baseline cadence:** Phase-transition or quarterly (F-046 §3.4.3)
**Last update:** 2026-05-23 (engineer; documentarian re-baseline at next cycle)
**Companion:** `FUTURE_WORK_MANIFESTS.md` + `DESIGN_DECISIONS_INDEX.md` + `90_supervisor/checkpoints/MASTER_TRACKER_2026-05-22.md`

## Status legend

`✅ shipped` · `🚧 in-progress` · `📋 queued` · `🤔 director-decision-pending` · `⏸ deferred-Wave-3` · `🧷 director-personal-channel`

---

## Phase 0 — Scaffold ✅
- 12-module tree on disk at `nisamina-app/{00_governance, 10_ingest, 20_normalize, 30_lexicon, 40_mcp_server, 50_app, 60_training, 70_audio, 80_validation, 90_supervisor, 95_documentarian, 99_publish}`
- Governance baseline: LICENSE (CC-BY-NC-SA 4.0) + CARE_compliance + attribution_register (53 rows) + consent_registry (10 rows)
- SOA discipline: decision_log.jsonl (39) + activity_log.jsonl (194+) + manifest_audit_register.jsonl (31)
- Audits: A-P0 phase-zero scaffold complete

## Phase 1 — Ingest
- **M-P1.A** Text extraction ✅ — 31 records EXTRACTION_MANIFEST; A-P1.A
- **M-P1.B** Vision-OCR 📋 — Karif 400pp + Magarada songs + Genon + Velasquez + Arrivillaga + Garifuna Song Book
- **M-P1.C** Audio transcription 📋 — Cambridge UP 47 WAVs + Bible mp3s + MP3-MP4-GARIFUNA 2.3GB + Religious_mp3s 76MB (F-007 GRN/FCBH gating Words-of-Life subset)
- **M-P1.D** Religious + Foundation provenance audit ⏸ — F-005 + F-011 audits gating
- **M-P1.E** foundry V0.1 ✅ (superseded by V0.2)
- **M-P1.E.fix** foundry V0.2 ✅ — 73,674 records / 33,133 public / 542 V_VAULT / 0/0/0 gate-clean; A-P1.E.fix
- **M-P1.E.fix.2** surgical correction ✅ — agüriahati/agüriahatu umlaut correction; A-P1.E.fix.2
- **M-P1.E.engine STAGE A** ✅ — Nisamina AI Engine inventory + classification; A-P1.E.engine.stageA
- **M-P1.E.engine STAGE B + C** 📋 — dedup vs foundry V0.2 + privacy gate
- **M-P1.F.curriculum** ✅ — Commission curriculum 45p staged; A-P1.F.curriculum; M-P1.F.curriculum.2 (lesson schema) + M-P1.F.curriculum.gate (strip_linter rule) queued
- **M-P1.F.religious** ✅ — 4 anthropology files staged; A-P1.F.religious; attr_050/051/052
- **M-P1.G** Textbook Library inventory + provenance 📋 — F-040 83GB
- **M-P1.H** Textbook Library curriculum-standards normalization 📋 — F-040
- **M-P1.I** Textbook Library Garifuna content ingest 📋 — F-040
- **M-P1.E.v0_3** foundry V0.3 (absorbs curriculum + religious + Engine STAGE B vocab) 📋

## Phase 2 — MCP Server ✅
- `40_mcp_server/nisamina_mcp/` with 5 tools + 4 resources + 2 prompts + recursive egress wrapper + safety guardrails (M-P3.E) + foundry V0.2 loader; 100/100 tests pass; A-P2

## Phase 3 — Chatbot + UI + Portal + LMS + Country + UNESCO + Funding

### Chatbot core (F-033 + F-033-DIRECTIVE)
- **M-P3.A** brain deploy 📋 — Gemma 3 4B-Instruct interim Phase-3 (D-030 + D-039) → Phase-5 Gemma-4-E4B-Nisamina; HF Space free tier; system_prompt_v1 + guardrails wired
- **M-P3.B** RAG layer 📋 — MEGA-RAG multi-evidence
- **M-P3.C** three-mode interface 📋 — curriculum content needs M-P1.F.curriculum.2
- **M-P3.D** speaking practice 📋 — MMS-tts-cab + Whisper-cab + Common Voice cab
- **M-P3.E** safety guardrails ✅ — 8-file library at `40_mcp_server/nisamina_mcp/guardrails/`; A-P3.E
- **M-P3.F** Avila briefing letter (Labayayahoun Ibagari) ✅ — draft sent per D-039; M-P3.F.2 formal-legal-license document queued post-Commission feedback
- **M-P3.G** GarifunaBench scaffold ✅ — 13-file package at `80_validation/garifuna_bench/`; A-P3.G

### UI (F-034)
- **M-P3.UI.A** Next.js 15 + React 19 + Tailwind v4 + shadcn/ui + Radix + next-intl + Workbox 7 scaffold 📋
- **M-P3.UI.B** three-mode interface + IndexedDB preferences 📋
- **M-P3.UI.C** curriculum mode UI 📋 — depends on M-P1.F.curriculum.2
- **M-P3.UI.D** chatbot streaming UI + Web Speech API + Whisper-cab fallback 📋
- **M-P3.UI.E** WCAG 2.2 AA + axe-core CI + Lighthouse gates 📋 — federal April 24 2026 deadline (already passed; gates production deploy)
- **M-P3.UI.F** Claim Attribution + Removal Request 📋 (scope) — code blocked on M-P3.UI.A + M-P3.A; A-P3.UI.F scope-audit

### Contributor Portal (F-038 + F-038-EXPANSION)
- **M-P3.PORTAL.A** Pre-populated forms ⏸ — auth flow, e-sign baseline
- **M-P3.PORTAL.B** Author/academic stewardship gateway ⏸ — OpenSign integration
- **M-P3.PORTAL.C** FPIC-compliant consent flow ⏸ — CARE Authority-to-control workflow
- **M-P3.PORTAL.D** Pre-population engine ⏸ — extracts from foundry + attribution_register
- **M-P3.PORTAL.E** Public counter-sign chain ⏸ — provenance anchor
- **M-P3.PORTAL.F** Mukurtu interop ⏸ — TK Labels native handoff

### LMS (F-039 + F-043)
- **M-P3.LMS.DEMO** Avila-meeting demo stage 📋 (Wave-2 next; uses F-043 real course outlines)
- **M-P3.LMS.A** Moodle 4.5.7+ scaffold ⏸ — 10 pilot schools Belize
- **M-P3.LMS.B** Real Belize NCF 2022 + Avila Commission course outlines ⏸ — content from F-043
- **M-P3.LMS.C** LTI 1.3 wiring (chatbot + foundry + portal + pronunciation) ⏸
- **M-P3.LMS.D** Per-school cohort management ⏸
- **M-P3.LMS.E** 11-outcome measurement integration ⏸ — F-044 MANDATORY at pilot launch

### Country organization (F-041)
- **M-P3.COUNTRY** First-class country dimension 📋 — UI + foundry V0.3 country_origin + attribution/consent metadata + chatbot Heritage variants + LMS per-country cohorts + St. Vincent homeland-reconnection per F-031

### UNESCO alignment (F-042) — 17 additions across 4 tiers
- **Tier-1 (foundational; documentation-level fast wins for Avila meeting)** 📋:
  - UNESCO 2003 ICH Convention alignment (Garifuna ICH-RL since 2008)
  - UNESCO 2021 AI Ethics Recommendation
  - UNESCO 2019 OER Recommendation
  - UNESCO 2025 Languages Matter
- **Tier-2 (IDIL theme expansions)** ⏸: M-P3.IDIL.4 Health · M-P3.IDIL.5 Public services · M-P3.IDIL.7 Biodiversity (TEK) · M-P3.IDIL.8 Economic · M-P3.IDIL.9 Gender (Abeimahani) · M-P3.IDIL.10 Partnerships
- **Tier-3 (research-infrastructure standards)** ⏸: M-P3.PID DOI/ORCID/ROR · M-P3.DEPOSITS ELAR+DELAMAN · M-P3.FORMATS TEI+ELAN+FLEx LIFT
- **Tier-4 (governance + accessibility + offline)** ⏸: M-P3.GOVERNANCE Community Advisory Board · M-P3.A11Y.DEEP sign-language+audio-native+cognitive · M-P3.OFFLINE.DEEP SMS+USB+Tŝilhqot'in pack

### Measurement (F-044)
- **M-P3.MEASURE** 11-outcome quarterly program 📋 — Lyu 2025 g≥0.608 + Li 2025 WTC + CAUSLT ≥4.0 + technostress NET REDUCTION + EGIDS 6b→6a + ASR≥90% per Te Hiku 92% + hallucination<5% per MEGA-RAG + cultural-relevance ≥4.0 + foundry coverage transparency + Tier-A consent traceability + hours-to-pilot

### Funding portal (F-045) — 16 sub-manifests
- **M-P3.FUND.A-H** Internal Ibagari grant pursuit (private; auth-gated) 📋 — pipeline tracker / application workspace / requirement checklist / budget / impact reporting (auto-from F-044) / funder CRM / 501(c)(3) compliance / director dashboard
- **M-P3.FUNDCOM.A-H** Public community funding directory ⏸ — searchable funder directory / funder profile pages / success stories / pathway guides / template library / tip sheets / Ibagari micro-re-granting (optional) / peer mentorship

### Governance + license
- **M-P3.F.2** Formal `Labayayahoun Ibagari` legal license document 📋 — post-Commission feedback on F-031/M-P3.F draft
- **Plan v1.2 amendment** 📋 — consolidates F-030..F-045 into the canonical plan

## Phase 4 — Audio 📋
- MMS-tts-cab wrap · Whisper-cab fine-tune · Common Voice cab corpus initiation · Cambridge UP 47 WAVs + community recordings · Catatu archival-only (consent_004 closed)

## Phase 5 — CPT + SFT fine-tune 📋
- **M-P5.A** Fine-tune corpus consolidation — uses textbook library `nisamina_gemma_4_fine_tune_master_corpus 2.4GB` per F-040
- **M-P5.B** CPT on Gemma 4 E4B per Rodríguez 2025 methodology
- **M-P5.C** SFT on V_VAULT + foundry-attested
- **M-P5.D** Gemma-4-E4B-Nisamina checkpoint
- **M-P5.E** GarifunaBench evaluation (M-P3.G harness)

## Phase 6 — Community release + academic record 📋
- Webonary + Living Dictionaries + Mukurtu + AILLA + Wikipedia/Wp-cab/Wikidata deposits
- UNESCO Memory of the World deposit
- Peer-reviewed paper (ACL Findings; Olko 2022 realist-synthesis-call answered)
- 24-month + 60-month longitudinal pilot follow-up (F-044)
- Reproducibility packet
- St. Vincent Yurumein homeland reconnection deliverable (F-031 + F-041)

## Cross-cutting infrastructure

### Three-channel exchange (F-024 isolation)
- **Engineer** writes `nisamina-app/` + ledgers; lives in `nisamina-app/`
- **Supervisor** writes `nisamina-supervisor/findings/` + `escalations/`; lives in `nisamina-supervisor/`
- **Documentarian** writes `nisamina-app/95_documentarian/` + `thesis/` + `90_supervisor/checkpoints/DOCUMENTARIAN_FILING_*.md`; lives in `nisamina-app/95_documentarian/`

### Memory + memory mirror
- Canonical: `/Users/shakamagarada/.claude/projects/-Volumes-AI-External-Nisamina-ai-Claude*/memory/` (currently three-way split — drive-root + -nisamina-app + -nisamina-supervisor)
- Mirror: `_memory_mirror/` (workspace union view); re-snap per `_memory_mirror/SNAPSHOT_NOTE.md`

### SOA-discipline trail
- `90_supervisor/decision_log.jsonl` · `90_supervisor/activity_log.jsonl` · `90_supervisor/manifest_audit_register.jsonl` · `90_supervisor/manifests/M-*.md` · `90_supervisor/audits/A-*.md` · `90_supervisor/checkpoints/*.md`

### Quarantine + governance gates
- JW NWT raw text quarantine (`30_lexicon/jw_quarantine_filter.py` + `30_lexicon/jw_remining_policy.md` + consent_005)
- Foundation pre-scrub quarantine (`30_lexicon/foundation_provenance_policy.md` + consent_009)
- Magarada PRELIMINARY (`30_lexicon/magarada_preliminary_gate.py` + consent_002)
- Catatu archival-only (`30_lexicon/catatu_archival_gate.py` + consent_004)
- English-language gate (`30_lexicon/english_language_gate.py`)
- NGC + BoD curriculum IP gate (consent_010 + forthcoming `M-P1.F.curriculum.gate` strip_linter rule)
- Egress: `99_publish/strip_linter.py` + MCP `40_mcp_server/nisamina_mcp/egress.py` recursive wrapper

## 7th LMS envir — STEM-alternative (per F-067)

Added 2026-05-23 per director directive *"add an alternative 'STEM' curricullum ... mimic a first world curricullum"* + F-065 + F-065-AMENDMENT + F-066 trilingual amendment + F-067 consolidated.

| Aspect | Value |
|---|---|
| Envir path | `50_app/lms/stem_alternative/` |
| Corpus | 1,315 files / 26.4 GB symlinked from `/Volumes/AI External/Nisamina_AI_Garifuna_Textbook_Library/{Math,Science,Computing}/` |
| Grade bands | 7 (01_PreK → 07_UnivPrep matching director's pre-existing structure) |
| Languages | Trilingual (Garifuna + English + Spanish) per F-066 (corrects earlier bilingual framing) |
| Status | Scaffolded; framework + overlay protocol drafted; per-band/per-subject content + trilingual lesson JSON generation queued multi-session |
| Legal basis | US Copyright Act §107 educational fair-use + transformative Garifuna-overlay (consent_012); per-publisher consent outreach queued via F-049 institutional pathway |
| Cross-envir | Alternative track (opt-in supplementary); 6 country-and-language envirs preserve per-MOE sovereignty as primary cohort target |
| Sovereign-presentation | F-055 axis #1 — matter (publisher source) vs presentation (Garifuna-overlay derivative work) |

## F-068 S16-FINAL fix queue (active blockers + WAVE-2.B unblocking conditions)

Per F-068 consolidated S16-FINAL directive — paste-ready for tracking. **Priority-0 blockers as of 2026-05-23T11:00Z:**

| ID | Item | Status |
|---|---|---|
| [B1] | F-063-REINSTATED garifuna_bench package-completeness on HF deploy | ✓ closed via deploy script `cp -R` + tts_garifuna.py + egress fix |
| [B2] | F-069 SECURITY HF_TOKEN scrub | ✓ closed via deploy script LFS-section auto-scrub regex; director retained current token per directive |
| [B3] | F-064 Phase-A keep-warm + 3-tier deployment posture | open — keep-warm cron queued; pilot-tier upgrade director-decision per F-064 staircase |
| [B4] | F-067 STEM 7th envir scaffold | ✓ closed this turn (scaffolded + symlinks live + framework + overlay drafted) |
| [B5] | F-066 trilingual Gate #24 verification | open — depends on M-P3.LMS.STEM_LESSON_GEN producing trilingual lesson JSON |
| [B6] | F-070 2-repo GitHub creation | director-action — org name confirmation pending (G11 approved) |
| [B7] | D-055 GGUF brain loader for free-tier compatibility | ✓ closed this turn (Q4_K_M GGUF via llama-cpp-python; requirements pushed) |
| [B8] | A-P3.A.FINAL chatbot live verification | pending HF Space `RUNNING` stage (build in progress) |

### Standing continuity-discipline practices (per F-046 §3.4)
1. **Every supervisor finding cites a peer-reviewed source OR supervisor brief OR director directive** (never supervisor opinion — F-044 enforcement)
2. **Every engineer manifest includes the FUTURE_WORK_MANIFESTS pickup spec** (scope + dependencies + sign-offs + DoD + citation chain)
3. **Quarterly meta-architecture re-baseline** (or Phase-transition; whichever sooner) — documentarian or engineer updates this file + `FUTURE_WORK_MANIFESTS.md` + `DESIGN_DECISIONS_INDEX.md`

*Buguya nuani Wamaraga.*
