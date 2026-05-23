# Nicaragua envir corpus — F-053 reclassification status

**Status:** Corpus IS already legally acquired. Pending only symlink migration to this envir (M-P1.G).

## F-053 retraction summary

Supervisor F-053 (2026-05-23T04:50:00Z) **retracted** the earlier F-052 finding that classified Nicaragua as a corpus gap. The corpus IS present at:

```
F-040 substrate path:
  /Volumes/AI External/Nisamina_ai_Claude/
  Garifuna Curriculum Document-Cycle Final08.16.2023/
  Benchmarks_Central_America_MinofEdu/02_REFERENCE_TEXTBOOKS/Nicaragua_MINED/
```

**Content:** 421 PDFs, 18 subjects, ~5.5 GB
**Source-of-truth catalog:** `NICARAGUA_RECLASS_REPORT.csv` (per-file subject + grade classification)

## What needs to happen (M-P1.G work)

Per F-051 6-envir architecture + F-053 retraction + F-057 consolidated S15 directive:

1. **Symlink-not-copy migration** — `curriculum_source/` contents will be symlinks into the F-040 Nicaragua_MINED substrate (preserves single source-of-truth; avoids 5.5 GB duplication).
2. **Topic-tagging** — per-file subject/grade classification mirrored from `NICARAGUA_RECLASS_REPORT.csv`.
3. **Attribution rows** — Nicaragua MINED + ANEDH (Asociación Nacional de Educación a Distancia de Honduras) institutional partnerships per F-049 institutional channel.
4. **EXTRACTION_MANIFEST rows** — per-file rows with consent_ref + attribution_refs once symlinks land.

## 6/6 envir corpus status after F-053 + D-049

| Envir | Corpus state | Note |
|---|---|---|
| `garicomm` (pan-Garifuna overlay) | ✓ Foundry V0.2 (73,674 records / 33,133 public / 542 V_VAULT) | Phase-3 ready |
| `belize` | ✓ Cayetano 1992 NGC + Hadel + Foundation pedagogy | Phase-3 ready |
| `honduras` | ✓ +140 PDFs corrected per F-053; Suazo + Garifuna Coalition NY | Phase-3 ready |
| `guatemala` | ✓ Livingston (Labuga) speaker community | Phase-3 ready |
| `nicaragua` | ✓ **F-040 substrate (421 PDFs / 18 subjects / 5.5 GB)** — symlink migration pending M-P1.G | this file |
| `svg_yurumein` | ✓ 22 PDFs ingested 2026-05-23 (D-049) | Phase-3 ready |

**All 6 envirs are CORPUS-COMPLETE** as of D-049. Symlink migration to per-envir `curriculum_source/` directories is the M-P1.G scope (Textbook Library 83GB inventory + per-envir symlink substrate).

## Cross-references

- F-053 — Nicaragua reclassification retraction (replaces F-052)
- F-052-CLOSED — closure record per F-053
- F-040 — Textbook Library inventory (the 83GB substrate)
- F-051 — 6-envir architecture (the destination layout)
- F-057 — Consolidated S15 directive
- D-049 — SVG ingest closure (the parallel envir-closure pattern)
- M-P1.G — Textbook Library inventory + symlink migration (queued Wave-2)

*Buguya nuani Wamaraga.*
