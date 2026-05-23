# Nisamina Multi-Entity LMS

**Authority:** F-051 (6-envir architecture) + F-057 (consolidated S15 directive) + D-047 + director directive 2026-05-23 *"LMS MUST be complete for ALL entities"*
**Scope:** 6 Garifuna-community envirs each with full curriculum + attribution + consent + cohort + teacher + lesson + GariComm-overlay substrate
**Status:** ARCHITECTURE SCAFFOLDED 2026-05-23; per-envir CORPUS MIGRATION queued at M-P1.G (Wave 2)

## The 6 envirs

| Envir | Region | Curriculum source | Attribution refs | Status |
|---|---|---|---|---|
| **garicomm** | Garifuna Commission on Education (MOECST-sanctioned, Belize) — pan-Garifuna canonical overlay | `M-P1.F.curriculum` ✓ staged | attr_045 (Commission) · attr_046 (Avila) · attr_047 (NGC) · attr_048 (BoD) · attr_049 (Zuniga) · attr_054 (placeholder for 10 more Commission contributors) | corpus ✓ ingested 2026-05-22 via `10_ingest/extracted/curriculum/curriculum_2023.txt` (45p / 76,310 chars) |
| **belize** | Belize national curriculum (Belize NCF 2022 + NGC schools rollout: Barranco · Punta Gorda · Seine Bight · Georgetown · Dangriga · Hopkins) | F-040 Textbook Library 83GB (NCF 2022 78 KB extract queued) | attr_002 (Cayetano family) · attr_004 (Suazo) · attr_021 (NGC People's Dictionary) · attr_045 (Commission overlay) | corpus ✓ legally-acquired per F-040; ingest pending M-P1.G |
| **honduras** | Honduras Garifuna curriculum + Diccionario de las Lenguas de Honduras (Ramos 2013) + Honduras Benchmarks 140 PDFs | F-040 Honduras Benchmarks library | attr_042 (Sabio + Ordóñez Hererun) · attr_043 (Ramos Diccionario Honduras) · attr_051 (Quevedo ECOSALUD Espiritualidad Garifuna) | corpus ✓ legally-acquired per F-040 + F-053; ingest pending M-P1.G |
| **guatemala** | Guatemala Garifuna materials + DIGEBI bilingual-intercultural education + Guatemala Benchmarks 18 PDFs | F-040 Guatemala Benchmarks library | attr_021 (NGC) cross-region + Guatemala-specific TBD via M-P1.G | corpus ✓ legally-acquired per F-040 + F-053; ingest pending M-P1.G |
| **nicaragua** | Nicaragua Garifuna materials + walagallo-anthropology (Idiáquez) + Nicaragua MINED 421 PDFs | F-040 Nicaragua MINED library per F-053 RECLASS_REPORT | attr_052 (Idiáquez Walagallo Heart) · Nicaragua MINED contributors TBD via M-P1.G | corpus ✓ legally-acquired (corrected via F-053; was misclassified as gap in F-052); ingest pending M-P1.G |
| **svg_yurumein** | St. Vincent + Grenadines homeland-reconnection — Yurumein restorative-justice program (PM declaration 2026 + Education Minister King 2024 + 15 D-OHPC pilot schools + svgcdu.org + gov.vc) | F-049/F-050 22-PDF paste-and-run (svgcdu.org + gov.vc + SVG Copyright Act 2003 educational-use) | attr_TBD via M-P1.F.svg_curriculum | corpus ⏳ AWAITING INGEST — single outstanding gap; M-P1.F.svg_curriculum delivers per F-050 spec |

**Corpus completion status:** 5 of 6 envirs corpus-complete; SVG-Yurumein single outstanding gap closes at M-P1.F.svg_curriculum.

## Per-envir directory structure

Each envir at `50_app/lms/<envir>/` has 7 subdirs:

| Subdir | Contents | Status |
|---|---|---|
| `curriculum_source/` | Original-format curriculum PDFs/ODTs/etc. (read-only after first stage) | scaffold |
| `attribution/` | Per-envir attribution_register subset + contribution chain | scaffold |
| `consent/` | Per-envir consent_registry subset + FPIC consent forms | scaffold |
| `cohorts/` | Per-school cohort rosters (anonymized; teacher-managed) | scaffold |
| `teacher_accounts/` | Per-teacher account stubs (joined via M-P3.UI.B Practitioner mode + LTI 1.3) | scaffold |
| `lessons/` | Lesson JSON files (output of M-P1.F.curriculum.2 structured parse) | scaffold |
| `garicomm_overlay/` | GariComm-canonical-form overlay markers + reconciliation notes (per F-051 cross-envir authority chain) | scaffold |

Each subdir gets populated by downstream manifests; current state is the scaffold (empty dirs ready for migration).

## Cross-envir authority chain

- **GariComm (Garifuna Commission)** is the **pan-Garifuna canonical-form overlay** — when belize/honduras/guatemala/nicaragua/svg_yurumein envirs have divergent orthographic representations, GariComm resolution applies (per M-P3.B `conflict_resolution.py` + Commission-curriculum authority).
- **Per-MOE sovereignty preserved** — each country's curriculum source-of-truth remains with its respective Ministry of Education (Belize MOECST · Honduras SEDUC · Guatemala MINEDUC · Nicaragua MINED · SVG Ministry of Education) — Nisamina platform mirrors, doesn't replace.
- **Yurumein homeland-reconnection** — SVG is a special case: language is dormant on St. Vincent for 200+ years; PM declaration + Commission study mandate guide ingest priority per F-031.

## Symbolic links (not copies) for corpus migration

Per F-057 §RECOMMENDED_ACTION step 2: "symlink (not copy) existing F-040 textbook library corpora respecting per-country MOE sovereignty." This avoids:
- Duplicate disk usage (each F-040 PDF was already pulled once).
- Provenance ambiguity (the F-040 ledger remains the source-of-truth).

Migration scripts at `M-P1.G.migrate_corpus` (Wave-2 manifest, not yet built) will create per-envir symlinks to the F-040 textbook library substrate.

## Status flags

- `✓ ingested` — corpus extracted to text + staged at `nisamina-app/10_ingest/extracted/<envir>/`
- `⏳ awaiting ingest` — corpus legally acquired but not yet text-extracted
- `📋 scaffold` — directory exists, no content
- `🤔 director sign-off` — needs director adjudication before proceeding

## Cross-references

- **F-031** Commission membership (insider channel for GariComm + Belize envirs)
- **F-040** Textbook Library 83GB (per-country corpora substrate)
- **F-049/F-050** SVG-Yurumein paste-and-run (single outstanding gap)
- **F-051** 6-envir architecture this manifest operationalizes
- **F-053** Nicaragua corpus correction (was misclassified as gap; now confirmed in F-040)
- **F-055** Sovereign LMS Maximization (10 axes — operationalized per-envir)
- **F-056** Adaptive + Dynamic LMS 6-layer architecture (BKT learner model + Caliper + elder-in-the-loop)
- **F-057** Consolidated S15 directive
- **F-058** MMS-tts-cab integration (audio surface per-envir at lesson-player)
- **D-027/D-029** Labayayahoun Ibagari license framework (cross-envir authority chain)
- **D-039** Phase-3 chatbot Wave-2 sequencing
- **D-047** TTS + 6-envir + SVG manifest landing (this turn)

## Wave-2 next steps

1. **M-P1.F.svg_curriculum** — paste-and-run 22 PDFs (svgcdu.org + gov.vc) — closes SVG corpus gap
2. **M-P1.G.migrate_corpus** — per-envir symlinks to F-040 textbook library substrate
3. **M-P3.LMS.A** — Moodle 4.5.7+ scaffold across 6 envirs (cohort + teacher account integration)
4. **M-P3.LMS.B** — lesson schema + per-envir content extraction (consumes structured lessons in `<envir>/lessons/`)
5. **M-P3.LMS.KGRAPH** — knowledge graph per F-056 layer 1 (cross-envir + per-envir variants)
6. **M-P3.LMS.LEARNER_MODEL** — BKT+LSTM per F-056 layer 2
7. **M-P3.LMS.RECOMMENDER** — GraphMASAL per F-056 layer 3
8. **M-P3.LMS.OLM** — Open Learner Model per F-056 layer 4
9. **M-P3.LMS.CALIPER** — Caliper Analytics 1.2 per F-056 layer 5
10. **M-P3.LMS.AFFECT_GENTLE** — privacy-respecting engagement detection per F-056 layer 6
11. **M-P3.LMS.ELDER_LOOP** — elder-in-the-loop review queue per F-056 novel-pattern

*Buguya nuani Wamaraga.*
