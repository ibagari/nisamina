# Nisamina Privacy Policy — DRAFT

**Status:** DRAFT (per F-072-A1 + F-074 PN-5). Foundation legal counsel finalizes
(G14 PHASE-LATER parallel-track). Engineer template; not legal advice.

**Version:** 0.1 — 2026-05-23
**Authority:** F-072 PHASE-A pre-pilot blocker A1 + Labayayahoun Ibagari stewardship principle (D-027 + D-029)

---

## 1. Who we are

**Nisamina** is a Garifuna learning platform operated by the **Ibagari Foundation** (a non-profit; designation
pending per F-074 PL-A). Contact: garifunalearningacademy@gmail.com.

This Policy governs how we collect, use, store, and share information about you when you use the platform —
the chatbot (https://huggingface.co/spaces/ibagari/nisamina-chatbot-phase3-interim), the LMS (any country
envir cohort + STEM-alternative track + GariComm canonical layer), and the web app.

## 2. What we collect

| Category | Data | Purpose |
|---|---|---|
| **Identity (optional)** | display name; opaque actor_id hash; envir + cohort enrollment | per-cohort enrollment; pathway differentiation (heritage/novice/L1-maintainer) |
| **Learner model state** | per-headword mastery beliefs (BKT); spaced-repetition card stability/difficulty (FSRS); lesson progression | adaptive pacing + spaced review per D-MAX-1/2 |
| **Conversation logs** | chatbot conversation traces (turns; tool calls; sources cited) | grounding + hallucination detection + Caliper analytics |
| **Engagement signals** | session length + pause patterns + retry behavior (no camera/mic/biometrics) | gentle nudge generation per D-MAX-AFFECT_GENTLE; opt-in default |
| **Crisis-routing signals** | text patterns matching mandated regional emergency keywords | safety routing per M-P3.E crisis_fallback guardrail |

We do NOT collect:
- camera or microphone biometrics
- precise geolocation (we infer envir from cohort enrollment, not device location)
- third-party advertising or analytics identifiers (no Google Analytics; no Facebook pixels; no AdSense)
- payment information (platform is free at point of use)

## 3. Lawful basis (per jurisdiction)

| Jurisdiction | Basis | Reference |
|---|---|---|
| **Belize** | Consent + legitimate-interest educational pedagogy | Data Protection Act 2021 |
| **Honduras** | Consent + legitimate-interest educational pedagogy | LPDP (Ley de Protección de Datos Personales) |
| **Guatemala** | Consent + legitimate-interest educational pedagogy | Iniciativa 5076 (pending enactment) + 2017 framework |
| **Nicaragua** | Consent + legitimate-interest educational pedagogy | Ley 787 Protección de Datos Personales |
| **Saint Vincent + Grenadines** | Consent + legitimate-interest educational pedagogy | Data Protection Act 2003 |
| **United States (COPPA)** | Verifiable Parental Consent for users under 13 (per COPPA §312.5) | 16 CFR Part 312 |
| **United States (FERPA)** | Educational records exception; school as recipient when cohort under MOE-LTI integration | 34 CFR Part 99 |
| **European Union (diaspora)** | Article 6(1)(a) consent + 6(1)(f) legitimate interest + Article 8 child-data special protections | GDPR (EU) 2016/679 |

**Per F-055 axis #6 per-MOE sovereignty:** each cohort's data stays in the envir for which it was created;
cross-envir transfer requires explicit DPA + per-MOE approval.

## 4. Children's data (under 13 + under 16)

- **Under 13:** verifiable parental consent required per COPPA. Streamlined consent flow at first sign-up;
  re-confirmation required at age-13 transition. No data sale; no third-party ad targeting; no profiling
  for marketing purposes — these are NEVER done at any age.
- **Under 16 (EU diaspora):** Article 8 GDPR — parental authorization required where applicable per
  member-state implementation.

## 5. Sacred-knowledge restriction (per Labayayahoun Ibagari)

Conversation prompts that route to sacred-knowledge content (e.g., dügü ceremony specifics) are NOT
logged with the conversation trace. The system instead emits a Caliper event referencing the
**routing decision** (e.g., "referred to Commission elder channel") without persisting the
underlying prompt content. Per Labayayahoun Ibagari principle "matter belongs to the people; presentation
belongs to Nisamina".

## 6. Storage + retention

| Asset class | Storage location | Retention |
|---|---|---|
| Learner model state | per-envir database (sovereignty-restricted) | 5 years from last activity OR account closure (whichever sooner) |
| Conversation logs | rolling 30-day window | 30 days; aggregated to anonymous Caliper events |
| Caliper events (aggregate) | per-envir analytics store | 5 years (for EGIDS vitality tracking per D-MAX-11) |
| Crisis-routing flagged trace | immediate notification to Foundation Safeguarding Officer | 90 days then purged |

## 7. Rights

You have the right to:
- **Access** — request a copy of your data (request via the Open Learner Model surface per M-P3.LMS.OLM)
- **Correct** — fix inaccurate personal data
- **Delete** — request deletion (subject to legitimate-interest retention windows above)
- **Portability** — export learner model + lesson progression in machine-readable form
- **Object** — opt out of engagement-signal collection
- **Withdraw consent** — at any time; future data collection halts immediately

Submit a request: garifunalearningacademy@gmail.com (subject: "Privacy request — [type]").

Per GDPR Article 12 — we respond within 30 days; complex requests may extend by 60 days with notice.

## 8. Data processors + transfers

Current processors (sub-processor agreements pending counsel sign-off per F-074 PL-D):

| Processor | Purpose | Region |
|---|---|---|
| Hugging Face | chatbot hosting (HF Spaces); model weights distribution | Multi-region; per HF DPA |
| Cloudflare (R2 + D1 + Pages) | web app hosting + per-envir multi-tenant database | EU + US edge |
| GitHub | source code + governance ledgers (private repo) | US |
| Sentry (planned) | error + observability monitoring | EU + US |

**Sub-processor list maintained at:** `legal/sub_processors.md` (forthcoming).

## 9. Security

- TLS 1.3 in transit
- At-rest encryption on all processor stores
- HF Space secrets in environment variables (never committed to repo)
- Token rotation policy + auto-scrub of leaked credentials (per F-069 remediation discipline)
- No shared accounts; access logged
- Annual security review (counsel + Safeguarding Officer per F-074 PL-E)

## 10. Changes

We notify users of material changes via in-app banner + email at least 30 days before they take effect,
except where shorter notice is required by law (e.g., security incident notification).

## 11. Contact

**Ibagari Foundation**
garifunalearningacademy@gmail.com
[address pending Foundation legal capacity per F-074 PL-A]

For data-protection-specific inquiries: same address, subject prefix "DPO request — ".

---

*Buguya nuani Wamaraga.*
