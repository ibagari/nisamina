# STEM-alternative envir — STATUS

**Status:** Scaffolded 2026-05-23 per F-067 PART 1. Corpus access via symlinks live. Framework + overlay protocol scaffolds queued.

## Current state

✅ **Done this turn:**
- 7th envir directory scaffold (`50_app/lms/stem_alternative/` + 8 subdirs)
- 7 grade-band subdirs under `curriculum_source/` each with Math/Science/Computing symlinks
- All 1,315 files accessible via symlinks (verified `find -L | wc -l` = 1315; matches F-067 inventory)
- README.md, STATUS.md (this file)

⏳ **Pending (multi-session per F-067 §4 + F-065-AMENDMENT):**

| Item | Sub-manifest | Per | Status |
|---|---|---|---|
| `CURRICULUM_FRAMEWORK.md` 5-pillar (Math + Science + Computing + Cross-cutting + Cultural) | M-P3.LMS.STEM_FRAMEWORK | F-065-AMENDMENT | scaffold queued |
| `GARIFUNA_OVERLAY_PROTOCOL.md` trilingual (Garifuna + English + Spanish) overlay rules | M-P3.LMS.STEM_OVERLAY | F-066 | scaffold queued |
| Publisher-by-publisher `attribution/*` rows (~30 publishers) | M-P3.LMS.STEM_ATTRIBUTION | F-065 §5 | queued |
| `consent_012` fair-use educational pedagogy + transformative-use overlay | governance ledger append | F-065 §5 | queued |
| Trilingual lesson JSON generator (per grade × subject × concept) | M-P3.LMS.STEM_LESSON_GEN | F-066 + F-065-AMENDMENT | depends on framework |
| Per-band scope-and-sequence (`grade_bands/*`) | M-P3.LMS.STEM_BANDS | F-065-AMENDMENT | queued |
| GariComm overlay cross-references (`garicomm_overlay/`) | M-P3.LMS.STEM_GARICOMM | F-051 | queued |
| Trilingual i18n integration into M-P3.UI.A scaffold | M-P3.UI.STEM_TRILINGUAL | F-066 | queued |
| Caliper events instrumented for STEM-track cohort enrollment | M-P3.LMS.STEM_CALIPER | D-MAX-11 | queued (engine ready in WAVE-2.A) |
| Gate #24 trilingual default rendered verified across all 5 country envirs + GariComm + diaspora | quality-gate test | F-066 + F-054 | queued |
| Teacher CPD pathway for STEM-track instructors | M-P3.LMS.STEM_CPD | D-MAX-8 + F-067 | queued |
| Achievement-gap analytics dashboard | M-P3.LMS.STEM_DASHBOARD | F-067 + D-MAX-11 | queued |

## Legal basis

- **F-065 §5:** fair-use educational pedagogy doctrine + transformative-use Garifuna-overlay
- **Per US Copyright Act §107 4-factor test:** (1) purpose = educational + transformative; (2) nature = published curriculum; (3) amount = use of concepts + scope-and-sequence, not verbatim large portions; (4) market = no substitute for original publishers (different language overlay)
- **Per F-049 institutional pathway:** Commission-channel outreach to publishers for explicit consent on per-publisher basis; F-065-AMENDMENT engineer-followup
- **Verbatim public republication path:** per-publisher consent + license review (NOT enabled at internal-pedagogy + LMS-stem_alternative-envir + chatbot-Heritage-mode scope of consent_012)

## Cross-envir composition

Per F-067 §3: this envir is an **alternative track**, not a replacement. The 5 country envirs (BLZ/HND/GUA/NIC/SVG) preserve per-MOE sovereignty and remain the primary cohort target. STEM-alternative is **opt-in supplementary** for cohorts whose MOEs cannot resource first-world STEM material directly.

GariComm envir provides pan-Garifuna canonical-form overlay (Cayetano 1992 NGC-Belize); STEM-track Garifuna-overlay defers technical-register coining to GariComm + Commission elder-mentor review.

## Reproducibility pointer

```bash
# Verify file counts match F-067 inventory
find -L "/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/lms/stem_alternative/curriculum_source" -type f | wc -l
# Expected: 1315

# Per-band breakdown
for band in 01_PreK_Ages_3_to_5 02_Kindergarten_Age_5_to_6 03_Early_Elementary_Grades_1_to_2 04_Upper_Elementary_Grades_3_to_5 05_Lower_Secondary_Grades_6_to_9 06_Upper_Secondary_Grades_10_to_12 07_University_Prep_and_Adult; do
  echo "$band: $(find -L "/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/lms/stem_alternative/curriculum_source/$band" -type f 2>/dev/null | wc -l | xargs) files"
done
```

*Buguya nuani Wamaraga.*
