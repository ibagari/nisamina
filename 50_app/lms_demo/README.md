# LMS Demo — Stage 1 (Avila-meeting demonstrable)

**Manifest:** `90_supervisor/manifests/M-P3.LMS.DEMO_avila_meeting_lms_demo.md`
**Audit:** `90_supervisor/audits/A-P3.LMS.DEMO_complete.md`
**Decision:** D-041 (this turn) — Wave-2 #1 per D-039 locked sequence
**License posture:** Labayayahoun Ibagari (Foundation guardianship) + CC-BY-NC-SA 4.0 platform wrapper · curriculum content remains NGC + Battle of the Drums Secretariat joint IP under consent_010 internal-pedagogy scope

## What this is

A static HTML demonstration of the Garifuna Language Commission curriculum (2023-2024) for the Commission consultation following the Avila briefing letter. Built per **F-043 ZERO MOCKED CONTENT** — all Garifuna text + learning outcomes + level structures drawn directly from the staged Commission curriculum at `10_ingest/extracted/curriculum/curriculum_2023.txt`.

## How to view

Open `index.html` directly in any modern web browser (Safari, Chrome, Firefox, Edge). No server, no build step. Single self-contained HTML + CSS file pair; renders cleanly offline.

## What it shows

1. **Header** — Commission + NGC + Battle of the Drums + Cayetano 1992 orthography attribution; Labayayahoun Ibagari license badge.
2. **Curriculum overview** — 8 levels + 15 annexes summary.
3. **Level cards** — 8 levels (Preschool Infant 1 → Standard 6) with strands and grade markers; matches Commission curriculum p.13-23.
4. **Sample lesson — Level 1 Weeks 1-6 + 7-12** — real learning outcomes 1.1, 1.2, 1.3, 7.1, 7.2 with the actual Garifuna example sentences (*Semisha niribei.* / *Ka biri?* / *Lubuñe Dimurei* / *agu* / *Ereba*).
5. **Annexes A-O** — all 15 + 1 annex sections enumerated with their Garifuna titles and English glosses.
6. **Cultural protocol** — Labayayahoun Ibagari principle text + sacred-knowledge routing protocol from M-P3.E guardrails.
7. **Stage-2 forward** — Moodle 4.5.7+ pilot deployment scope for the 10 Belize schools.

## What it deliberately does NOT show

- **No verbatim long passages** from the curriculum (consent_010 internal-pedagogy scope; verbatim public reproduction requires NGC + BoD permission).
- **No chatbot integration** — that's M-P3.A + M-P3.B (Wave-2 #2 next).
- **No Levels 2-8 full content** — only level cards + the Level 1 sample is fully detailed (extraction of Levels 2-8 lesson schemas is M-P1.F.curriculum.2).
- **No backend / API / assessment** — read-only demo.
- **No multilingual UI** — English with Garifuna terms inline; next-intl wiring is M-P3.UI.A.

## Commission consultation asks

The demo accompanies the Avila briefing letter (M-P3.F draft sent per D-039 #1). At the Commission consultation:

1. **Review the curriculum integration** — does the Cayetano 1992 orthography + 8-level structure + 15 annexes match what the Commission has shipped to the schools?
2. **Review the cultural-protocol framing** — does the Labayayahoun Ibagari principle text + sacred-knowledge routing match the Commission's expectation for an AI-mediated platform?
3. **Adjust the Level 1 sample** — the engineer pulled what's on the source page; the Commission may want a different exemplar.
4. **Set the Stage-2 (M-P3.LMS.A-E Moodle pilot) timeline** — 10 pilot schools + LTI 1.3 + 11-outcome measurement (F-044) ready when the Commission says go.
5. **Confirm the demo can be circulated** — the demo is internal-pedagogy use under consent_010; broader circulation needs explicit NGC + BoD permission.

## Engineering notes

- **WCAG 2.2 AA target** — semantic HTML5 (`<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`), ARIA labels on every section, skip-link to main content, focus indicators ≥0.1875rem, color contrast ≥4.5:1, touch targets ≥44px, reduced-motion respected via `@media (prefers-reduced-motion)`.
- **No framework** — vanilla HTML5 + CSS3; renders identically on a Raspberry Pi 5 offline-pack or a school's old laptop running Firefox 60+.
- **UTF-8 throughout** — Garifuna diacritics (`ü`, `á`, `é`, `í`, `ó`, `ú`, `ñ`) render with system serif fallback chain.
- **Print stylesheet** — demo prints cleanly at A4 for paper distribution at the Commission meeting if needed.
- **Manifest + audit pair on disk** — full SOA-discipline trail per plan v1 §6.

## Files

- `index.html` — the demo page
- `styles.css` — cleanroom CSS (no Tailwind, no framework)
- `README.md` — this file

## Citation chain

- F-039 LMS two-stage architecture (supervisor S14)
- F-043 real-course-outlines requirement (supervisor S14)
- F-031 Commission membership + curriculum receipt
- D-027 + D-029 Labayayahoun Ibagari license name + principle text locked
- D-030 Phase-3 interim Gemma 3 4B-Instruct brain (NOT Gemma 4 E4B per D-039)
- D-032 M-P1.F.curriculum staged content + consent_010 NGC+BoD IP gate
- M-P3.E sacred_knowledge module (8-file guardrails library) — drives the cultural-protocol section
- F-046 §3.3 PLATFORM_ARCHITECTURE_INDEX + FUTURE_WORK_MANIFESTS pickup-spec discipline

*Buguya nuani Wamaraga.*
