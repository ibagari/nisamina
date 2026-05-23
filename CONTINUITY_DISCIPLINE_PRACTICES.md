# Continuity Discipline Practices

**Authority:** F-046 §3.4 + D-040 (engineer-executes-meta per director directive 2026-05-23 *"apply all supervisor fixes"*)
**Audience:** engineer + supervisor + documentarian — all three channels
**Companion:** `90_supervisor/REVIEW_PROTOCOL.md` + `95_documentarian/DOCUMENTARIAN_PROTOCOL.md`

These three standing practices are binding on all three channels going forward. They make explicit what's currently implicit so future engineers/supervisors/documentarians don't re-derive.

---

## Practice 1 — Citations: peer-review OR brief OR directive; never opinion

Every supervisor finding (`F-###` in `nisamina-supervisor/findings/supervisor_findings.jsonl`) must populate its `citation` field with **one of**:

- a peer-reviewed academic source (arxiv / ACL / journal article / dissertation / preprint with DOI),
- a supervisor architecture brief (`nisamina-supervisor/notes/YYYY-MM-DD_S##_*.md`),
- a director directive (literal quoted phrase + date), OR
- a prior cross-reference (existing finding / decision / manifest / audit / governance entry).

**Never** *"supervisor judges that..."* / *"in supervisor opinion..."* / *"a model UNESCO-compliant platform..."* — F-044 retraction enforces this. Opinion-form claims must be retracted-and-replaced with cited evidence.

Engineer + documentarian apply the same standard when authoring decisions / manifests / audits / thesis content.

---

## Practice 2 — Manifests carry future-engineer-pickup spec

Every M-* manifest (engineer's `90_supervisor/manifests/M-*.md` + documentarian's `95_documentarian/manifests/M-DOC-*.md`) at open-time MUST include the F-046 §3.3.2 template fields:

```markdown
- **Status:** queued | in-progress | shipped
- **Supervisor brief:** <path to brief if any>
- **Director directive:** <verbatim quoted phrase + date>
- **Dependencies:** <other M-* or director sign-offs that must land first>
- **Director sign-off needed:** <specific decision points>
- **Definition of done (DoD gate items):** <bulleted checklist>
- **Citation chain:** <plan section / supervisor brief / memory file / prior decision>
```

When a new engineer or supervisor opens the manifest, they pick up the work without re-deriving scope. `FUTURE_WORK_MANIFESTS.md` aggregates all queued manifests per this template.

---

## Practice 3 — Quarterly meta-architecture re-baseline

`PLATFORM_ARCHITECTURE_INDEX.md` + `FUTURE_WORK_MANIFESTS.md` + `DESIGN_DECISIONS_INDEX.md` are re-baselined every quarter **or** at every Phase transition (whichever is sooner). Cadence:

- **Q-mark:** end of each calendar quarter (Q1 = 2026-03-31, Q2 = 2026-06-30, Q3 = 2026-09-30, Q4 = 2026-12-31)
- **Phase transition mark:** completion of any Phase (0 → 1 → 2 → 3 → 4 → 5 → 6)

The re-baseline updates:
- `PLATFORM_ARCHITECTURE_INDEX.md` — shipped/queued/in-progress status flags
- `FUTURE_WORK_MANIFESTS.md` — new manifests added, completed manifests retired (linked back to A-* audit), deferred manifests re-classified
- `DESIGN_DECISIONS_INDEX.md` — new D-### entries added; downstream-decisions-affected updated

Re-baseline becomes a separate M-DOC-###-REBASELINE manifest+audit pair (documentarian-authored) **OR** a separate M-###-REBASELINE engineer-authored entry if documentarian queue is full.

First re-baseline cadence start: **Phase 3 launch + 90 days, then quarterly** (F-046 §5 default).

---

## Cross-reference

- Practice 1 enforcement: `90_supervisor/REVIEW_PROTOCOL.md` §8 (new section to be added by next supervisor turn) + this file
- Practice 2 enforcement: this file + `FUTURE_WORK_MANIFESTS.md` template
- Practice 3 enforcement: `95_documentarian/DOCUMENTARIAN_PROTOCOL.md` §8 (new section to be added by next documentarian turn) + this file
- All three: standing-watch items on next-engineer / next-supervisor / next-documentarian boots

*Buguya nuani Wamaraga.*
