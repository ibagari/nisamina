# STEM-alternative — Trilingual Garifuna overlay protocol

**Status:** Scaffold (per F-066 trilingual amendment + Cummins 1979 CALP/BICS). M-P3.LMS.STEM_OVERLAY sub-manifest fills in concrete rendering rules.

## Per F-066: trilingual default (Garifuna + English + Spanish)

Per director directive 2026-05-23: STEM track is **trilingual**, not bilingual. Updates Gate #24 to "TRILINGUAL default rendered (Garifuna + English + Spanish)".

### Three languages, distinct roles

| Language | Role |
|---|---|
| **Garifuna** (cab) | heritage-language anchoring + identity-relevant content surfacing; technical-register coining via GariComm overlay |
| **English** (en) | source-publication language for most of the corpus (Spectrum, Cambridge, AOPS) |
| **Spanish** (es) | primary instructional language for Honduras + Guatemala + Nicaragua public schools |

### Per-envir default

Per F-066: default-rendered language is per-envir-default. Per-learner toggle on every surface.

| Envir | Default language stack |
|---|---|
| `belize` cohort | English (primary) + Garifuna (heritage anchor) + Spanish (regional) |
| `honduras` cohort | Spanish (primary) + Garifuna (heritage anchor) + English (technical) |
| `guatemala` cohort | Spanish (primary) + Garifuna (heritage anchor) + English (technical) |
| `nicaragua` cohort | Spanish (primary) + Garifuna (heritage anchor) + English (technical) |
| `svg_yurumein` cohort | English (primary) + Garifuna (heritage reconstruction) + Spanish (regional) |
| `garicomm` cohort | Garifuna (canonical) + English (cross-reference) + Spanish (cross-reference) |
| `diaspora` cohort | English (primary) + Garifuna (heritage reconstruction) + Spanish (regional) |

## Per Cummins 1979 CALP/BICS — overlay intensity by band

Per F-065 §3: cognitive academic language proficiency (CALP) requires 5-7 years of intensive instruction vs basic interpersonal communication (BICS) 1-2 years. **Implication:** Garifuna-overlay intensity should be progressive across grade bands.

| Band | Garifuna overlay intensity | English/Spanish role |
|---|---|---|
| 01_PreK + 02_K | **Heaviest** Garifuna scaffolding | English/Spanish present as exposure |
| 03_G1-G2 + 04_G3-G5 | **Mature bilingual default** Garifuna + L2 | balanced |
| 05_G6-G9 | Garifuna technical-register sustainment | L2 dominant |
| 06_G10-G12 + 07_UnivPrep | **English/Spanish-dominant** with Garifuna technical-register sustainment | L2 primary; Garifuna anchor |

This progression respects F-059 D-MAX-5 heritage pathway pacing (HL learners progress receptive → productive over years).

## Source-to-derivative work rule

Per F-065 §5 + F-067 §3 sovereign presentation:

1. **Source corpus** is unchanged: publishers' material lives at the textbook library symlink target. Engineer does NOT modify source PDFs.
2. **Lesson JSON** at `lessons/` is the derivative work — Garifuna/English/Spanish trilingual rendering of source concepts.
3. **Lesson JSON schema** (per M-P3.LMS.STEM_LESSON_GEN sub-manifest):
   ```json
   {
     "lesson_id": "stem.math.04.bar_modeling.fractions_intro",
     "subject": "Math",
     "grade_band": "04_Upper_Elementary_Grades_3_to_5",
     "concept": "Bar modeling for fraction comparison",
     "source_refs": [
       {"corpus": "Singapore_Math_4A", "page": "47-52", "publisher": "Singapore Math Inc."}
     ],
     "consent_ref": "consent_012",
     "attribution_refs": ["attr_XYZ"],
     "trilingual": {
       "cab": {"title": "...", "instruction_steps": [...], "examples": [...]},
       "en":  {"title": "...", "instruction_steps": [...], "examples": [...]},
       "es":  {"title": "...", "instruction_steps": [...], "examples": [...]}
     },
     "cultural_anchors": ["hudutu-recipe-ratio", "canoe-distance-time"],
     "pathway_variants": {
       "heritage": {"identity_anchor": "..."},
       "novice": {"example_emphasis": "..."},
       "l1_maintainer": {"academic_register": "..."}
     }
   }
   ```

## Technical-register coining

Per F-067 §3 + F-031 Commission institutional channel + F-055 axis #1:

- Garifuna technical-register terms (e.g., "fraction", "variable", "algorithm") are **NOT engineer-invented**.
- Routing: lesson_gen flags need-for-new-term → GariComm overlay review → Commission elder-mentor review → canonical term added to `30_lexicon/foundry_v6/` → re-renders lesson with canonical term.
- Until canonical term exists, English/Spanish term surfaces with `[needs Garifuna term]` flag visible in learner UI; community-translation pipeline picks up.

## Quality gate

Per F-066 Gate #24: **trilingual default rendered verified across all 5 country envirs + GariComm + diaspora.**

Acceptance criteria (queued for M-P3.LMS.STEM_LESSON_GEN sub-manifest):
- Every lesson JSON has all 3 language tracks populated (or explicitly `[needs translation]` placeholder)
- Per-envir default-language renders correctly in the UI
- Per-learner toggle changes rendering across whole session
- No accidental cross-language leak (Spanish text appearing in Garifuna track, etc.)

## Cross-references

- **F-066** trilingual amendment (updates Gate #24)
- **F-065 §3** Cummins 1979 CALP/BICS + translanguaging research base
- **F-067 §3** sovereign presentation principle
- **F-031** Garifuna Commission institutional channel (Curtis King + Godwin Friday + Avila + elder mentors)
- **F-055 axis #1** sovereign presentation (matter vs presentation)
- **F-059 D-MAX-5** pathway differentiation (HL/Novice/L1-maintainer)
- **D-027 + D-029** Labayayahoun Ibagari (license + cultural protocol)
- **D-049** SVG ingest (parallel envir closure pattern)

*Buguya nuani Wamaraga.*
