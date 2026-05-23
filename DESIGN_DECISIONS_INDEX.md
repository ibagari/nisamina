# Design Decisions Index — D-001 through D-039

**Authority:** F-046 §3.3.3 + D-040 (engineer-executes-meta per director directive 2026-05-23 "apply all supervisor fixes")
**Source:** `90_supervisor/decision_log.jsonl` (39 records, append-only)
**Maintenance:** updated per Wave-completion + quarterly re-baseline

Each entry: summary + date + citation chain + supervisor review status + downstream-decisions-affected.

---

## D-001 — Free-tier hosting (Cloudflare Pages + HF Space + R2)
- **Date:** 2026-05-21
- **Citation:** plan v1.1 §1.1 + director directive 2026-05-21 *"let's do the (free) route for now"*
- **Supervisor review:** S5 concur
- **Downstream:** D-008 (pip+HF Space distribution); D-016 (sovereignty-max); F-045 (funding portal architecture)

## D-002 — JW re-mining: internal-only with strict output stripping
- **Date:** 2026-05-21
- **Citation:** director directive 2026-05-21 *"yes mine legally"* + jw_remining_policy.md + consent_005
- **Supervisor review:** S5 concur
- **Downstream:** D-012 (foundry V0.2 gate enforcement)

## D-003 — Meta MMS-tts-cab + Cambridge UP fine-tune
- **Date:** 2026-05-21
- **Citation:** director directive *"meta+cambridge if with integrity and legal"* + CC-BY-NC 4.0 (MMS) + CC-BY 4.0 (Cambridge UP)
- **Supervisor review:** S5 concur

## D-004 — Webonary co-publication yes-with-mirror
- **Date:** 2026-05-21
- **Citation:** director directive + SIL Webonary FLEx XHTML export

## D-005 — Magarada Stories triangulate-and-verify only
- **Date:** 2026-05-21
- **Citation:** director directive 2026-05-21 *"use only what we can triangulate and verify"* + project_magarada_preliminary_status

## D-006 — Catatu Midwife archival-only
- **Date:** 2026-05-21
- **Citation:** director directive *"we can do that at a later date"* + UNDRIP FPIC + consent_004

## D-007 — Supervisor channel: another Claude instance, bidirectional log
- **Date:** 2026-05-21
- **Citation:** director directive + plan v1 §7
- **Downstream:** F-024 (channel isolation); F-035 (documentarian queue)

## D-008 — MCP distribution: pip primary + HF Space mirror
- **Date:** 2026-05-21
- **Citation:** D-001 free-tier + sovereignty principle + Anthropic MCP spec

## D-009 — Memory mirror at `_memory_mirror/`
- **Date:** 2026-05-22
- **Citation:** director directive + supervisor 2026-05-21 dependency note

## D-010 — foundry_v6 V0.1 architecture (Cayetano-normalized merge + tier 5/A/B/C/X)
- **Date:** 2026-05-22
- **Citation:** Cayetano 1992 + CARE Principles Authority-to-control
- **Downstream:** D-011 (reject-rebuild); D-012 (V0.2 fix)

## D-011 — Reject-rebuild foundry V0.1 (3 defects caught self-audit)
- **Date:** 2026-05-22
- **Citation:** feedback_no_oscillation + feedback_soa_discipline

## D-012 — foundry V0.2 full multi-gate stack (Cayetano + English + per-row V_VAULT + gate library)
- **Date:** 2026-05-22
- **Citation:** director directive *"NO foundry contamination — FIX IT b4 you continue"* + F-016/F-017/F-018/F-019/F-020 supervisor findings

## D-013 — F-007/F-009/F-011 best-practice rulings
- **Date:** 2026-05-22
- **Citation:** director directives + GRN CC-BY-NC-SA + foundation_provenance_policy.md
- **Sub-decisions:** F-007 GRN; F-009 UP-Mississippi maximize-use; F-011 .bak_pre_scrub quarantine

## D-014 — UP Mississippi permission letter approved for send
- **Date:** 2026-05-22
- **Citation:** director *"mississippi approved"*

## D-015 — F-025 + F-026 + F-024 item 2 housekeeping
- **Date:** 2026-05-22
- **Citation:** director *"3"* + supervisor S7 findings

## D-016 — Open-weight LLM only; chatbot UI Phase 3 (sovereignty-max)
- **Date:** 2026-05-22
- **Citation:** director directive *"ADD a chatbot to the platform"* + AskUserQuestion answers
- **Downstream:** F-033-OVERRIDE (Gemma 4 E4B final); D-030 (Phase-3 interim Gemma 3 4B); D-039 (verification)

## D-017 — M-P2 MCP server complete
- **Date:** 2026-05-22
- **Citation:** plan v1 §3 Phase 2 + plan v1.1 §2.1 + D-008 + D-016

## D-018 — F-021 attribution audit Phase-A (24 mechanical mappings)
- **Date:** 2026-05-22
- **Citation:** plan v1 §9 + plan v1.1 §1.6 + F-021

## D-019 — F-021 Phase-B (100% foundry source-ID coverage)
- **Date:** 2026-05-22
- **Citation:** director AskUserQuestion answers + Stanford SearchWorks 7145709 + WebSearch
- **Downstream:** attr_042 Sabio+Ordóñez · attr_043 Ramos · attr_044 Diccionario_Garifuna unknown

## D-020 — 2026-05-22 scope consolidation (MASTER_TRACKER + 3 memory files)
- **Date:** 2026-05-22
- **Citation:** F-029 + F-030 + F-031 + F-032 + F-033

## D-021 — F-022 closure via append (D-001..D-011 supervisor concur)
- **Date:** 2026-05-22
- **Citation:** F-022 + feedback_no_hindsight_whitewashing rule 3

## D-022 — F-035 documentarian next cycle = Plan v1 + v1.1 + A-052 full read
- **Date:** 2026-05-22
- **Citation:** director AskUserQuestion + F-035

## D-023 — M-CLEANUP narrow scope (STAGE A + STAGE C trilingual derivatives)
- **Date:** 2026-05-22
- **Citation:** F-010-DIRECTIVE + MASTER_TRACKER §4 + plan v1 §6 rule 6

## D-024 — M-P3.E safety guardrails as library at 40_mcp_server
- **Date:** 2026-05-22
- **Citation:** F-033-DIRECTIVE + S12 brief §2.7 + UNESCO 2025 + GUARD Act + CA 2025

## D-025 — M-P3.G GarifunaBench scaffold with NotAuthoritativeError gate
- **Date:** 2026-05-22
- **Citation:** F-033-DIRECTIVE + F-030 #13 + FormosanBench 2025 + MEGA-RAG 2025 + plan v1 §6 rule 2

## D-026 — 5 director adjudications captured
- **Date:** 2026-05-22
- **Sub-decisions:**
  - #1 Curriculum path verified
  - #2 Kaitiakitanga = abayayaha-root family
  - #3 SHA256-dup = one canonical retained per cluster + engineer judgment
  - #4 Outreach letters shelved for M-P3.UI.F
  - #5 Dr. Gwen Nuñez Gonzalez = director-personal-channel

## D-027 — License name `Labayayahoun Ibagari` LOCKED
- **Date:** 2026-05-22
- **Citation:** director *"Labayayahoun Ibagari"* + foundry V0.2 abayayahouni Tier-5 V_VAULT

## D-028 — Umlaut triangulation: aguriahati→agüriahati confirmed; Labayayahoun corpus-clean
- **Date:** 2026-05-22
- **Citation:** foundry V0.2 multi-dictionary triangulation + director *"may need umlaut"*
- **Downstream:** D-033 (M-P1.E.fix.2 surgical correction)

## D-029 — Labayayahoun final lock + principle text approved
- **Date:** 2026-05-22
- **Citation:** director *"approved"* + D-028

## D-030 — Phase-3 interim Gemma 3 4B-Instruct; Phase-5 final Gemma-4-E4B-Nisamina
- **Date:** 2026-05-22
- **Citation:** director correction *"we agreed to use a temp brain before we train Nisamina on gemma 4 e4b"* + D-016 + project-moest-chatbot-directive memory
- **Downstream:** D-039 (verification: NOT e4b)

## D-031 — M-P3.F Avila briefing letter director-edit-and-sign workflow
- **Date:** 2026-05-22
- **Citation:** director directive M-P3.F + D-027 + D-029 + D-030

## D-032 — M-P1.F.curriculum staged ingest (consent_010 NGC+BoD IP)
- **Date:** 2026-05-22
- **Citation:** F-031 + D-026 #1 + curriculum PDF page-1 IP notice

## D-033 — M-P1.E.fix.2 foundry surgical correction (2 records; SHA new c2934dd7...)
- **Date:** 2026-05-22
- **Citation:** D-028 + plan v1.1 §1.6 + feedback_no_hindsight_whitewashing rule 2

## D-034 — M-P3.UI.F scope-manifest (code blocked on UI.A + M-P3.A)
- **Date:** 2026-05-22
- **Citation:** D-026 + F-030 #9 + Te Hiku Media community-authority pattern

## D-035 — F-004 + F-006 + F-010 director rulings (Engine + Religious + SHA256-dedup)
- **Date:** 2026-05-22
- **Citation:** director 2026-05-22 *"F-004 Yes safely and scientifically. f-006 yes please, scientifically. f-010... we do not destroy corpus we keep it clean and remove dups"*

## D-036 — M-P1.F.religious 4-file anthropology ingest
- **Date:** 2026-05-22
- **Citation:** F-006-DIRECTIVE + D-035 + attr_050/051/052

## D-037 — M-P1.E.engine STAGE A inventory; STAGE B + C deferred
- **Date:** 2026-05-22
- **Citation:** F-004-DIRECTIVE + F-004-ADVISORY 3 caveats + D-035 + Master Directive 2025-06-22 ODT

## D-038 — Supervisor S14 consolidated scope (F-037..F-047) absorbed; MASTER_TRACKER §10
- **Date:** 2026-05-22
- **Citation:** F-047 supervisor consolidated directive + director pacing frame *"we do not need to have all NOW per say"*

## D-039 — Three director locks 2026-05-23
- **Date:** 2026-05-23
- **Sub-decisions:**
  - (1) Avila briefing letter SENT (*"done"*)
  - (2) Temp brain verified Gemma 3 4B-Instruct NOT e4b (*"verify temp brain, not e4b"*)
  - (3) Wave-2 sequence locked: LMS demo → chatbot end-to-end → Textbook Library (*"best prac 4"*)

## D-040 — Apply-all-supervisor-fixes engineer execution
- **Date:** 2026-05-23
- **Citation:** director *"apply all supervisor fixes as well"* + F-046 §3.3 templates + F-047 RECOMMENDED_ACTION
- **Artifacts produced:** PLATFORM_ARCHITECTURE_INDEX.md + FUTURE_WORK_MANIFESTS.md + DESIGN_DECISIONS_INDEX.md (this file) + 10 Commission attribution rows (attr_054..attr_063) + funder seed directory + protocol updates with 3 standing practices + M-P3.META consolidated scope manifest

*Buguya nuani Wamaraga.*
