# Future Work Manifests — Forward-Pickup Specs

**Authority:** F-046 §3.3.2 + D-040 (engineer-executes-meta per director directive 2026-05-23 "apply all supervisor fixes")
**Companion:** `PLATFORM_ARCHITECTURE_INDEX.md` + `90_supervisor/manifests/M-*.md` (full text for shipped manifests)
**Maintenance:** quarterly re-baseline + after each Wave-completion (F-046 §3.4.3)

Per the F-046 §3.3.2 template, each queued M-* below carries: status / supervisor-brief-ref / director-directive / dependencies / director sign-off needed / DoD gate items / citation chain. **Engineers pick up from this file without re-deriving scope.**

---

## Wave-2 — engineer can begin next session (no blockers + locked sequence per D-039)

### M-P3.LMS.DEMO — Avila-meeting LMS demonstration stage

- **Status:** 📋 queued (next-session start per D-039 Wave-2 sequencing #1)
- **Supervisor brief:** `nisamina-supervisor/notes/2026-05-23_S14_lms_architecture_brief.md` (F-039) + `2026-05-23_S14_real_course_outlines.md` (F-043)
- **Director directive:** 2026-05-23 *"MOEST dire NEED for Garifuna chatBot + create standardized LMS specifically aligned to the needs of Garifuna + 10 pilot schools in Belize... almost immediate testing stress test/usage, in a scientifically aligned way"*
- **Dependencies:** F-043 real course outlines staged (Belize NCF 2022 + Avila Commission curriculum already extracted ✓); chatbot Gemma 3 4B-Instruct interim brain locked (D-030); attribution_register Commission rows present (attr_045/046/047/048/049)
- **Director sign-off needed:** demo presentation format (live web vs slide-walkthrough vs video) + Avila meeting date
- **DoD gate items:**
  - [ ] Demo stage scaffolded at `50_app/lms_demo/` (Next.js 15 page or static-export)
  - [ ] Real Belize NCF 2022 + Avila Commission curriculum data wired (no mock content)
  - [ ] 1 sample lesson per of the 8 levels (Preschool Infant 1 → Standard 6) playable
  - [ ] Chatbot integration smoke-tested (Gemma 3 4B + system_prompt_v1 + MCP grounding)
  - [ ] Commission attribution chain visible on every cited fact
  - [ ] M-P3.LMS.DEMO manifest + A-P3.LMS.DEMO audit committed
- **Citation chain:** F-039 + F-043 + F-031 Commission membership + D-039 Wave-2 sequence

### M-P3.A — Gemma 3 4B-Instruct interim brain on HF Space

- **Status:** 📋 queued (next-session start per D-039 Wave-2 sequencing #2)
- **Supervisor brief:** `nisamina-supervisor/notes/2026-05-22_S12_chatbot_architecture_brief.md` (F-033 + F-033-OVERRIDE corrected per D-030)
- **Director directive:** 2026-05-22 *"we are using gemma 4 e4b"* (F-033-OVERRIDE → reframed as Phase-5 target per D-030) + 2026-05-23 *"verify temp brain, not e4b"* (D-039 lock)
- **Dependencies:** M-P2 MCP server ✓ + M-P3.E safety guardrails ✓ + system_prompt_v1 ✓ + foundry V0.2 gate-clean ✓
- **Director sign-off needed:** HF Space hosting account + (optional) Hetzner backup-Hetzner upgrade trigger
- **DoD gate items:**
  - [ ] Gemma 3 4B-Instruct downloaded + 4-bit quantized on HF Space free tier
  - [ ] System_prompt_v1.md loaded as system prompt
  - [ ] All 7 guardrails wired (sacred_knowledge + crisis_fallback + session_breaks + no_impersonation + disclosure + off_topic + age_appropriate)
  - [ ] MCP server `40_mcp_server/` callable from chatbot for `lookup_headword` + `cite_sources` + `cayetano_normalize` + `parse_morphology` + `translate_sentence`
  - [ ] GarifunaBench scaffold callable wrapping the brain (M-P3.G integration)
  - [ ] First 10 queries smoke-tested end-to-end (input → MCP grounded → guardrails-screened → cited response)
  - [ ] M-P3.A manifest + A-P3.A audit committed
- **Citation chain:** D-016 sovereignty-max + F-033 chatbot brief + D-030 + D-039 + project-moest-chatbot-directive memory + plan v1.1 §1.1 free-tier hosting

### M-P3.B — RAG layer (MEGA-RAG multi-evidence)

- **Status:** 📋 queued (parallel with M-P3.A; same Wave-2 cluster)
- **Supervisor brief:** `2026-05-22_S12_chatbot_architecture_brief.md` §2.4
- **Director directive:** F-033-DIRECTIVE
- **Dependencies:** M-P3.A brain running + foundry V0.2 ✓
- **Director sign-off needed:** none — engineer defaults to MEGA-RAG pattern
- **DoD gate items:**
  - [ ] Retrieval index built (foundry V0.2 + curriculum + religious-anthropology + verified-sentences)
  - [ ] Multi-evidence requirement enforced (≥2 sources for Tier-A; flagged single-source for Tier-C)
  - [ ] Hallucination detector M-P3.G wired live
  - [ ] Context-conflict resolution rule (curriculum > foundry > religious-anthropology)
  - [ ] M-P3.B manifest + A-P3.B audit
- **Citation chain:** MEGA-RAG PMC 2025 + Hallucination Mitigation MDPI 2025 + Rodríguez 2025 + plan v1 §6 rule 2

### M-P3.UI.A — Next.js 15 + React 19 + Tailwind v4 + shadcn/ui + Radix + next-intl + Workbox 7 scaffold

- **Status:** 📋 queued (parallel with M-P3.A; can land same Wave)
- **Supervisor brief:** `nisamina-supervisor/notes/2026-05-22_S13_ui_architecture_brief_may2026.md` (F-034)
- **Director directive:** 2026-05-22 *"this platform MUST have the latest and greates UI based on todays standards May 2026"*
- **Dependencies:** none — can start TODAY
- **Director sign-off needed:** brand colors + logo if any
- **DoD gate items:**
  - [ ] Next.js 15 + React 19 project at `nisamina-app/50_app/`
  - [ ] Tailwind v4 + shadcn/ui (copy-not-install model) installed
  - [ ] Radix UI primitives wired
  - [ ] next-intl scaffolded (English / Garifuna / Spanish / Kriol stubs)
  - [ ] Workbox 7 PWA service worker registered
  - [ ] WCAG 2.2 AA design tokens (≥4.5:1 contrast / focus indicators / ≥44×44px touch)
  - [ ] axe-core + Lighthouse CI gates
  - [ ] Cloudflare Pages deploy configured
  - [ ] M-P3.UI.A manifest + A-P3.UI.A audit
- **Citation chain:** F-034 + WCAG 2.2 W3C + Next.js 15 + plan v1.1 §1.1

### M-P3.UI.D — Chatbot streaming UI + Web Speech API + Whisper-cab fallback

- **Status:** 📋 queued (parallel with M-P3.A once UI.A scaffold lands)
- **Supervisor brief:** S13 UI brief §5
- **Dependencies:** M-P3.UI.A scaffold + M-P3.A brain running
- **DoD gate items:**
  - [ ] Vercel-AI-SDK-equivalent streaming hook
  - [ ] Markdown buffering + deferred code blocks
  - [ ] ARIA live regions for screen readers
  - [ ] Stop button + citation chain inline `[source]` superscripts
  - [ ] Web Speech API + Whisper-cab fallback
  - [ ] M-P3.UI.D manifest + A-P3.UI.D audit
- **Citation chain:** F-034 + AI Chat UI Best Practices 2026 frontkit + Chatbot UI Design Patterns 2026 FuseLab

### M-P3.UI.B / .C / .E — three-mode interface / curriculum mode / WCAG gates

- All 📋 queued; per F-034 + D-039 Wave-2 sequencing; DoD per `2026-05-22_S13_ui_architecture_brief_may2026.md` §8

### F-030 P1 quick wins (documentation-level fast wins for Avila meeting)

- **TK + BC Labels** 📋 — `30_lexicon/tk_labels.py` + `99_publish/strip_linter.py` extension + 50_app UI surfaces
- **UNESCO 2006-2009 Garifuna Action Plan citation** 📋 — plan v1.2 §1.1 update (doc-only)
- **IDIL 10-theme explicit map** 📋 — plan v1.2 §1.5 (doc-only)

### F-030 P2 publication targets

- **Mukurtu** 📋 — `99_publish/mukurtu_export.py` (Mukurtu 4 / Drupal 11; TK Labels native)
- **Common Voice cab** 📋 — Mozilla locale initiation; community crowdsourced corpus
- **Wikidata** 📋 — `99_publish/wikidata_export.py` + Wp/cab feed
- **AILLA** 📋 — `99_publish/ailla_deposit.py`

### F-030 P3 partners + funding (elevated per F-044)

- **F-030 P3 #9** 8 partner attribution rows — superseded by M-P3.UI.F community-led pattern (D-026)
- **F-030 P3 #11** named-academic-partnerships — ELEVATED to current cycle per F-044 §5
- **F-030 P3 #12** named-grant-applications — merged into F-045 funding portal scope

### F-040 Textbook Library 83 GB

- **M-P1.G** inventory + provenance ledger reading
- **M-P1.H** curriculum-standards normalization (Belize NCF 2022 alignment)
- **M-P1.I** Garifuna content ingest (per-file license discrimination CC-BY-4.0 substrate vs CC-BY-NC-SA-4.0 benchmark-only)
- **M-P5.A** fine-tune corpus consolidation (`nisamina_gemma_4_fine_tune_master_corpus 2.4GB` Phase-5 ready)

### F-041 Country organization

- **M-P3.COUNTRY** — UI + foundry V0.3 `country_origin` field + attribution/consent metadata + chatbot Heritage variants + LMS per-country cohorts + St. Vincent homeland reconnection

### F-042 17 UNESCO additions — Tier-1 (Avila-meeting fast wins)

- UNESCO 2003 ICH Convention alignment (Garifuna ICH-RL since 2008)
- UNESCO 2021 AI Ethics Recommendation
- UNESCO 2019 OER Recommendation
- UNESCO 2025 Languages Matter

### F-043 Real course outlines + 10 Commission attribution rows

- Belize NCF 2022 (78KB) ✓ extracted (engineer-pending; queued for STAGE B of F-043 manifest)
- Avila Commission curriculum (1MB) ✓ already extracted in M-P1.F.curriculum
- 8 Avila courses × 36 unit titles × ~288 unit-records + 15 annexes
- 10 new Commission attribution rows added this turn (attr_054 — attr_063; per F-043 below)

### F-044 11-outcome measurement program

- **M-P3.MEASURE** quarterly cadence — Lyu g≥0.608 + Li WTC + CAUSLT ≥4.0 + technostress NET REDUCTION + EGIDS 6b→6a + ASR≥90% + hallucination<5% + cultural-relevance ≥4.0 + foundry coverage + Tier-A consent traceability + hours-to-pilot

### F-045 Funding Portal — Internal (M-P3.FUND.A-H)

Per F-046 brief §2.2:
- **M-P3.FUND.A** grant pipeline tracker · **M-P3.FUND.B** application workspace · **M-P3.FUND.C** requirement checklist · **M-P3.FUND.D** budget management · **M-P3.FUND.E** impact reporting (auto-from F-044) · **M-P3.FUND.F** funder CRM · **M-P3.FUND.G** 501(c)(3) compliance · **M-P3.FUND.H** director dashboard
- **Pre-seeded funder directory** (12+ funders) — see `99_publish/funder_seed_directory.jsonl` produced this turn

---

## Wave-3 — soft-blocked

### Contributor Portal (F-038 + F-038-EXPANSION)
- **M-P3.PORTAL.A-F** — 6 sub-manifests; depends on M-P3.UI.A scaffold + M-P3.A backend + Commission consultation on portal name (Contributor Portal / Stewardship Gateway / abayayaha Hub); spec per `2026-05-23_S14_contributor_portal_brief.md`

### LMS pilot deployment (F-039)
- **M-P3.LMS.A-E** — Moodle 4.5.7+ infrastructure; 10 pilot schools; spec per `2026-05-23_S14_lms_architecture_brief.md`

### Funding Portal Community (F-045)
- **M-P3.FUNDCOM.A-H** — public community-funding directory; spec per `2026-05-23_S14_funding_portal_and_meta_architecture.md` §2.3

### UNESCO additions Tier 2/3/4 (F-042)
- **M-P3.IDIL.4 / .5 / .7 / .8 / .9 / .10** — IDIL theme expansions
- **M-P3.PID** DOI/ORCID/ROR · **M-P3.DEPOSITS** ELAR+DELAMAN · **M-P3.FORMATS** TEI+ELAN+FLEx LIFT
- **M-P3.GOVERNANCE** Community Advisory Board · **M-P3.A11Y.DEEP** sign-language+audio · **M-P3.OFFLINE.DEEP** SMS+USB+offline

### Engine Phase-B + Phase-C (F-004)
- **M-P1.E.engine STAGE B** — dedup vs foundry V0.2 + per-source attribution; unzip Learning Corpus 3
- **M-P1.E.engine STAGE C** — privacy gate per file + magarada_engine_privacy_gate.py module

### F-010 M-CLEANUP-B SHA256 dedup
- Per D-026 policy: one canonical retained per cluster; keep all unique content; remove only verified-duplicate copies; quarantine perimeter preserved

### Other Wave-3 items
- **M-P1.F.curriculum.2** lesson-level structured parsing
- **M-P1.F.curriculum.gate** strip_linter verbatim-block rule
- **F-005 + F-011** Religious Distillation + Foundation Training provenance audits (gate M-P1.D)
- **F-009** UP Mississippi permission letter send mechanics
- **F-030 P3 #10** NYC diaspora UI mode
- **F-030 P4 #14** Ladin synthetic-data methodology
- **F-030 P4 #15** TEK / Biocultural corpus + BC Labels
- **F-030 P4 #16** Abeimahani / Arumahani women's-song corpus
- **M-P3.F.2** Formal `Labayayahoun Ibagari` legal license document (post-Commission feedback)
- **M-DOC-006-META** documentarian-pickup of these meta-architecture files (when documentarian session opens)
- **Plan v1.2 amendment** — consolidates F-030..F-045 into the canonical plan

---

## Director-personal channel (engineer does NOT outreach)
- **🧷 Dr. Gwen Nuñez Gonzalez** (Yurumein Project Initiative; Commission; director-friend)
- **🧷 Ms. Sheena Zuniga** (NGC president per curriculum frontmatter; attr_049)
- **🧷 Darius Avila** (Commission president; attr_046; receives M-P3.F briefing letter)

---

## Phase B WAVE-2.B/3/4/5 — LMS maximize catalog (per F-059)

Added 2026-05-23 with WAVE-2.A foundations landing in M-P3.LMS.WAVE-2A. Each pickup spec follows F-046 §3.3.2 template: Status / authority / dependencies / DoD / citation.

### WAVE-2.B — Learner experience (3 sessions; depends on WAVE-2.A foundations)

#### M-P3.LMS.PATHWAY — heritage/novice/L1-maintainer pathway differentiation
- **Status:** queued; depends on `lesson_player` + `olm`
- **Authority:** F-059 D-MAX-5 + Carreira & Kagan 2018 (HL pedagogical needs differ) + Polinsky & Kagan heritage continuum + Form-Focused Instruction in HL Classroom Frontiers 2020
- **Deps:** M-P3.LMS.WAVE-2A (lesson_player + olm)
- **DoD:** Three Pathway classes (HeritagePathway, NovicePathway, L1MaintainerPathway) each with scaffolding intensity + register focus + assessment differences; per-pathway lesson variants generator; tests for distinct progression
- **Citation:** Carreira & Kagan (2018) — Spanish heritage language education in US

#### M-P3.LMS.MULTIMODAL — video + oral-history + image with consent surfacing
- **Status:** queued; depends on `caliper`
- **Authority:** F-059 D-MAX-6 + UNESCO Feb 2025 + UNESCO Dec 2025 Chile vitality
- **Deps:** M-P3.LMS.WAVE-2A (caliper for analytics); 00_governance/attribution_register + consent_registry
- **DoD:** Multimodal asset types (Video, OralHistory, Image) with consent_id + attribution_id required at instantiation; cite_sources MCP tool surfaces on each play; storage scaffold; tests for required-attribution-or-raise
- **Citation:** UNESCO Technology in Indigenous Language Preservation (Feb 2025)

#### M-P3.LMS.GAMES — mobile games (vocab-match + sentence-build + dialogue-choose)
- **Status:** queued
- **Authority:** F-059 D-MAX-4 + g=0.962 large-effect meta-analysis (38 studies / N=4,102) + g=1.28 long-term mobile vocabulary meta (65 studies 2010-2024)
- **Deps:** M-P3.LMS.WAVE-2A (lesson_player) + M-P3.UI.A (web scaffold)
- **DoD:** 4 game types (vocab-match + sentence-build + dialogue-choose + cultural-context-quiz); mobile-first responsive; offline-capable via Workbox 7; per-envir dialect-aware content
- **Citation:** Mobile games for language learning meta-analysis (cited in F-059)

#### M-P3.LMS.A11Y — WCAG 2.2 AAA + low-bandwidth + print-export
- **Status:** queued; depends on M-P3.UI.A
- **Authority:** F-059 D-MAX-12 + WCAG 2.2 AAA + UNESCO Languages Matter 2025 + federal April 24 2026 deadline (AA floor)
- **Deps:** M-P3.UI.A (scaffold; AA already embedded); axe-core CI from M-P3.UI.E
- **DoD:** AAA color contrast on text + UI; audio-only + text-only fallback modes; print-export workbook generator (SVG-Yurumein remote-area pilot requirement); CI gate via axe-core + Lighthouse
- **Citation:** WCAG 2.2 W3C Recommendation (federal April 24 2026 Title II deadline)

### WAVE-3 — Adaptive + Tutoring (4 sessions; depends on WAVE-2.A foundations)

#### M-P3.LMS.KGRAPH — knowledge graph
- **Status:** queued
- **Authority:** F-056 layer-1 + F-059 D-MAX-1 (FSRS feeds graph)
- **Deps:** M-P3.LMS.WAVE-2A; Foundry V0.2 headwords; per-country curriculum LOs
- **DoD:** Graph schema (Cayetano headwords + Avila units + LO edges + dialect-variant edges); load from foundry + curriculum; traversal API; tests for graph integrity
- **Citation:** F-056 brief §1

#### M-P3.LMS.LEARNER_MODEL — full BKT-LSTM hybrid (production of OLM scaffold)
- **Status:** queued
- **Authority:** F-056 layer-2 + F-059 D-MAX-2 + Nature 2025 DKT + Zhou 2024 PSI-KT
- **Deps:** M-P3.LMS.WAVE-2A (olm scaffold); cohort observations
- **DoD:** BKT parameter fit from cohort; LSTM sequence-aware extension; hybrid BKT-LSTM gating; per-headword tuned parameters; A/B vs baseline OLM scaffold
- **Citation:** Corbett & Anderson (1995) BKT + Nature 2025 DKT

#### M-P3.LMS.RECOMMENDER — GraphMASAL multi-agent recommender
- **Status:** queued
- **Authority:** F-056 layer-3 + GraphMASAL 2025
- **Deps:** M-P3.LMS.KGRAPH + M-P3.LMS.LEARNER_MODEL
- **DoD:** Multi-agent recommender (per-pathway agent + cohort-affinity agent + dialect-preservation agent); next-headword + next-lesson recommendations; per-MOE data sovereignty preserved
- **Citation:** GraphMASAL 2025 (cited in F-056)

#### M-P3.LMS.AFFECT_GENTLE — privacy-respecting engagement
- **Status:** queued
- **Authority:** F-056 layer-5 + SDT 2024-2025 + Hamari 2014
- **Deps:** M-P3.LMS.WAVE-2A (olm)
- **DoD:** Engagement signals (session length + pause patterns + retry behaviour) without camera/mic/biometrics; gentle nudge generation; opt-in default; per-MOE data sovereignty
- **Citation:** SDT 2024-2025 + Hamari (2014) gamification meta

#### M-P3.LMS.TUTOR — Socratic AI tutor with Phase-5 Gemma-4-E4B-Nisamina
- **Status:** queued; depends on Phase-5 fine-tune
- **Authority:** F-059 D-MAX-7 + Harvard 2024 (>2× learning) + Reiser 2004 + Brookings 2025 SLM
- **Deps:** Phase-5 Gemma-4-E4B-Nisamina fine-tune (CPT/SFT on Avila + foundry V0.3); M-P3.LMS.WAVE-2A (olm for personalization)
- **DoD:** Scaffolded Q&A with hint progression; OLM-state-aware personalization; integrates with mastery-gate (D-MAX-2); cite_sources MCP attribution; on-the-fly Garifuna-language scaffolding
- **Citation:** Harvard 2024 AI-tutor study + Reiser (2004)

#### M-P3.LMS.MASTERY — mastery-gate progression
- **Status:** queued
- **Authority:** F-059 D-MAX-2 + Bloom 1968 + Bloom 1984 (2-sigma) + Guskey 2007 meta
- **Deps:** M-P3.LMS.WAVE-2A (lesson_player + olm)
- **DoD:** Replace time-based advancement with mastery-gate (≥0.85 OLM belief); per-cohort + per-pathway mastery thresholds; Caliper events emit at mastery
- **Citation:** Bloom (1968, 1984) + Guskey (2007)

#### M-P3.LMS.MICRO — 5-minute daily microlearning units
- **Status:** queued
- **Authority:** F-059 D-MAX-3 + 0.74 SD higher-ed microlearning meta + Prasittichok EFL systematic review
- **Deps:** M-P3.LMS.WAVE-2A (lesson_player); Workbox 7 (PWA push)
- **DoD:** 5-min unit generator from lesson sequence; PWA push notification scaffold; mobile-first; offline-capable; alternative pathway alongside M-P3.LMS.B full lesson player
- **Citation:** Higher-ed microlearning meta-analysis (cited in F-059)

#### M-P3.LMS.ELDER_LOOP — weekly community-elder feedback review queue per cohort
- **Status:** queued; depends on Commission elder-mentor recruitment (G4)
- **Authority:** F-055 sovereignty axis #1 + F-056 layer-6 + F-031 Commission membership
- **Deps:** M-P3.LMS.WAVE-2A (caliper for cohort surface)
- **DoD:** Weekly formative-feedback queue generator; elder-review tool surface; feedback integration back to lesson + cohort; cultural-protocol surface
- **Citation:** F-055 + Olko 2022 realist synthesis

### WAVE-4 — Community + Heritage + Research (3 sessions)

#### M-P3.LMS.CPD — Teacher CPD module with Open Badges 3.0 (1EdTech)
- **Status:** queued; depends on M-P3.LMS.MASTERY
- **Authority:** F-059 D-MAX-8 + UNESCO Languages Matter 2025 + 1EdTech Open Badges 3.0
- **Deps:** M-P3.LMS.MASTERY + Moodle LTI 1.3 (M-P3.LMS.A WAVE-5)
- **DoD:** CPD course generator from foundry + curriculum; Open Badges 3.0 verifiable credential emit at completion; LTI 1.3 wiring to per-MOE Moodle
- **Citation:** UNESCO Languages Matter 2025 + 1EdTech Open Badges 3.0 spec

#### M-P3.LMS.DIASPORA — US/UK Garifuna diaspora portal
- **Status:** queued
- **Authority:** F-059 D-MAX-9 + UNESCO Dec 2025 Chile + EGIDS dialect-level
- **Deps:** M-P3.LMS.PATHWAY (heritage-learner pathway)
- **DoD:** US Garifuna hubs (LA + NY + Bronx) + UK Garifuna + diaspora language portal; cohort-affinity routing; diaspora-elder mentorship surface
- **Citation:** UNESCO Dec 2025 Chile 8-Indigenous-Peoples vitality

#### M-P3.LMS.DIALECT — Dialect tagging × 5 envirs
- **Status:** queued
- **Authority:** F-059 D-MAX-9 + EGIDS Lewis & Simons 2010
- **Deps:** M-P3.LMS.WAVE-2A (Card + Step both have dialect_tag fields)
- **DoD:** Per-envir dialect inventory (Belize-Garifuna vs Honduras-Garifuna vs Guatemala-Garifuna vs Nicaragua-Garifuna vs SVG-Yurumein-Garifuna); lesson variant generator with dialect filter; cross-envir dialect comparison surface
- **Citation:** EGIDS Lewis & Simons (2010)

#### M-P3.LMS.ICH — Intangible Cultural Heritage modules
- **Status:** queued
- **Authority:** F-059 D-MAX-10 + UNESCO 2003 ICH Convention + Olko 2022
- **Deps:** M-P3.LMS.MULTIMODAL (video + oral-history); F-031 Commission consent
- **DoD:** 5 module families — Music (punta + paranda + hungahunga + chumba) + Dance (punta + dügü ceremony movements) + Food (hudutu + sere + machuca + ereba) + Calendar (Settlement Day Nov 19 Belize + Yurumein April 14 SVG + Chugu + Beluria) + Kinship (Garifuna matrilineal/patrilineal kin terminology)
- **Citation:** UNESCO 2003 ICH Convention + Olko (2022) realist synthesis

#### M-P3.LMS.DASHBOARD — Commission research + vitality dashboard
- **Status:** queued
- **Authority:** F-059 D-MAX-11 + F-055 axis #6 + EGIDS Lewis & Simons 2010 + Caliper 1.2 spec
- **Deps:** M-P3.LMS.WAVE-2A (caliper + olm); per-MOE data residency infrastructure
- **DoD:** EGIDS tracking per cohort + envir; Caliper aggregate analytics surface (no PII); cohort progression waves; cross-envir comparisons; per-MOE sovereignty enforced at query layer
- **Citation:** EGIDS Lewis & Simons (2010) + IMS Caliper 1.2

#### M-P3.LMS.PORTAL — Contributor portal extension
- **Status:** queued
- **Authority:** F-038 contributor portal
- **Deps:** M-P3.UI.A scaffold
- **DoD:** Claim-attribution form (M-P3.UI.F surface); community-translation pipeline; per-contributor consent tracking
- **Citation:** F-038 brief

### WAVE-5 — Integration + Quality Gates + Phase-5 + Stage-2 deploy (3 sessions)

#### M-P3.LMS.A — Moodle 4.5.7+ multi-envir + LTI 1.3
- **Status:** queued
- **Authority:** F-039 + F-054 quality-gate-suite
- **Deps:** WAVE-2.A + WAVE-2.B foundations; per-MOE Moodle hosting; LTI 1.3 tool consumer
- **DoD:** Moodle multi-tenant scaffold (per-envir); LTI 1.3 tool consumer for Nisamina engine; per-MOE admin separation; cohort enrollment + Caliper integration
- **Citation:** F-039 + IMS LTI 1.3

#### M-P3.LMS.QUALITY_GATES — 23 block-ship CI gates
- **Status:** queued
- **Authority:** F-054 14 gates + F-058 #18 + F-059 +5 (D-MAX-1/2/5/9/11) = 23 total
- **Deps:** WAVE-2.A + all WAVE-2.B/3/4 foundations
- **DoD:** CI pipeline (per F-054 §3 + F-059 §5) running 23 gates pre-merge; each gate has measurable + peer-reviewable + falsifiable spec; director adjudicates any waiver
- **Citation:** F-054 super-SOA spec + F-059 D-MAX dimensions

#### Phase-5 Gemma-4-E4B-Nisamina fine-tune
- **Status:** queued; depends on G5 director approval
- **Authority:** F-033-OVERRIDE D-039 + D-MAX-7 + Phase-5 brain plan
- **Deps:** WAVE-2.A; Avila + foundry V0.3 corpus; HF + Gemma access
- **DoD:** CPT (Continued Pre-Training) on Garifuna corpus; SFT (Supervised Fine-Tuning) on Avila instruction data; checkpoint at HF Models; integration replacing interim Gemma 3 4B-Instruct in chatbot
- **Citation:** D-030 Phase-3 interim + D-039 Phase-5 plan

#### Per-envir corpus migration completion (M-P1.G)
- **Status:** queued
- **Authority:** F-040 substrate + F-051 6-envir + F-053 Nicaragua + F-057 consolidated
- **Deps:** Textbook Library 83GB inventory
- **DoD:** Symlinks from each envir's curriculum_source/ into F-040 substrate; per-envir SHA256 ledger; EXTRACTION_MANIFEST appends across all 6 envirs
- **Citation:** F-040 + F-051 + F-057

---

## Continuity-discipline standing practices (per F-046 §3.4)
1. **Citation: peer-review OR brief OR director-directive** — never supervisor opinion (F-044)
2. **Manifest pickup spec** — every M-* uses §3.3.2 template (Status / brief / directive / deps / sign-offs / DoD / citation)
3. **Quarterly re-baseline** — this file + ARCHITECTURE_INDEX + DESIGN_DECISIONS_INDEX updated quarterly or per Phase transition

*Buguya nuani Wamaraga.*
