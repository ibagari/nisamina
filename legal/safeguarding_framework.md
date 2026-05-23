# Nisamina Safeguarding Framework — DRAFT

**Status:** DRAFT (per F-072-A3 + F-074 PN-6). Foundation Safeguarding Officer plugs in when designated
(G16 PHASE-LATER parallel-track). Engineer-built framework; Officer adapts + activates.

**Version:** 0.1 — 2026-05-23
**Authority:** F-072 PHASE-A pre-pilot blocker A3 + Commission consultation per F-031 + COPPA + UNCRC + applicable jurisdictional child-safety laws

---

## 1. Purpose

This Framework establishes the safeguarding policies + procedures Nisamina applies to protect children +
vulnerable users from harm in the course of platform use. Adopted by the Ibagari Foundation Board (per
F-074 PL-A) once formally constituted; until then, the Director assumes interim Safeguarding Officer
responsibilities per Commission practice.

## 2. Scope

Applies to:
- All learners (any age) using the chatbot, LMS, or web app
- All Foundation staff, Commission members, volunteer elder mentors
- All sub-processors handling user data (per DPA Schedule A scope)
- All envir cohorts under MOE-LTI integration

## 3. Roles + responsibilities

| Role | Responsibility |
|---|---|
| **Safeguarding Officer** | Designated by Foundation Board; receives all crisis-routing flags + safeguarding concerns; coordinates response; reports to Board quarterly; ultimately responsible for Framework operation |
| **Director (interim)** | Until Officer designation lands, acts as interim Safeguarding Officer per F-074 PL-E |
| **Engineering** | Builds + maintains safety guardrails (crisis_fallback + no_impersonation + sacred_knowledge + off_topic + session_breaks + age_appropriate + disclosure per M-P3.E) |
| **Commission members + volunteer elders** | Receive routed sacred-knowledge inquiries via M-P3.LMS.ELDER_LOOP; report concerns about learner welfare back to Officer |
| **Teachers / MOE staff (cohort)** | Per LTI 1.3 integration; receive cohort-level aggregate analytics (Caliper events; no PII); report concerns about individual learners through their school's mandated-reporting channel |

## 4. Age verification + parental consent

### Under 13 (COPPA US + applicable elsewhere)

- First sign-up flow checks self-reported age
- If under 13: requires **Verifiable Parental Consent** before any data collection beyond minimal account
  bootstrap
- Methods of verification (any one): credit-card $0.01 charge-back; signed paper consent; government ID
  upload + Officer review; school-administered cohort enrollment (MOE-LTI flow)
- Refresh required at age-13 birthday (re-consent flow)

### Under 16 (GDPR Article 8 — EU diaspora cohorts)

- Same protocol as under 13 where required by member-state implementation
- Default to Article 8 protection in absence of explicit member-state guidance

### Cohort enrollment (any age)

- MOE-LTI 1.3 integration treats school as the institutional consent-channel
- Per-MOE consent records logged in 00_governance/consent_registry.jsonl with `cohort_ref` link
- Officer may audit consent records at any time

## 5. Crisis routing

### Triggers (programmatic; per M-P3.E crisis_fallback guardrail)

The chatbot detects + routes on these signals (non-exhaustive):
- Suicidal ideation language (per WHO suicide-prevention guidance)
- Self-harm language
- Disclosure of abuse (sexual / physical / emotional / neglect)
- Domestic-violence language
- Immediate-danger language

### Response

1. Chatbot surfaces regional emergency resources INLINE (no waiting for next turn):
   - US: 988 (suicide & crisis lifeline) + 911
   - Belize: Mental Health Association of Belize + 911
   - Honduras: Línea de Vida 132 + 911
   - Guatemala: Línea Crisis 1543 + 119
   - Nicaragua: 911 + 118
   - SVG: 999 + 911
   - Diaspora: country-of-residence emergency number
2. Refuses to engage as substitute for crisis-counselor; explicit non-impersonation disclosure
3. Flags the routing event to Safeguarding Officer via Caliper crisis_event surface (NOT the user's
   underlying message content — only the routing decision + timestamp + envir; per privacy policy §5)
4. Officer reviews within 24h + escalates per mandated-reporting law where applicable

## 6. Content moderation

### Inbound (user-generated content)

- Pre-publication review for any user content that would appear public (claim-attribution forms,
  community-translation submissions, neologism proposals)
- Reviewer: Officer or Officer-delegated trusted volunteer
- Removal of: harassment, hate speech, sexual content involving minors, doxxing, personal-data scraping,
  spam

### Outbound (AI-generated content)

- M-P3.E guardrails enforce: no_impersonation (refuses doctor/lawyer/therapist role-play),
  off_topic (refuses non-Garifuna-learning topics), sacred_knowledge (routes specifics to elder channel),
  age_appropriate (filters content by content_tier_for_age)
- session_breaks: 3-hour California-law hard-stop + soft nudges at 50/110/170 minutes
- disclosure: opening disclosure on every conversation that this is AI + grounded + not substitute for
  human teacher / elder / professional

## 7. Mandatory reporting

Where law requires Foundation/Officer to report suspected child abuse to authorities (e.g., Belize Family
Court; Honduras DINAF; Guatemala SBS; Nicaragua MIFAN; SVG Family Services; US state CPS; etc.):

1. Officer escalates within the legally-mandated window
2. Foundation cooperates with investigation
3. Documentation preserved in tamper-evident form (per audit-trail discipline)

## 8. Volunteer + elder-mentor vetting

Per F-031 Commission collaboration + M-P3.LMS.ELDER_LOOP:

- Background check (per jurisdiction; typically clear-criminal-record certificate + 2 character references)
- Code of Conduct sign-off
- Annual safeguarding training (Foundation provides materials; Officer tracks completion)
- Direct-message channels with learners DISABLED by default; routes via Officer-mediated queues only

## 9. Incident response

Steps when a safeguarding concern is identified:

1. **Immediate** (≤1h): Officer notified via Caliper crisis_event channel + email alert
2. **Triage** (≤4h): Officer assesses severity + immediate-action need
3. **Action** (≤24h):
   - Emergency action where life/safety at risk (involve emergency services)
   - Account hold / suspension where necessary
   - Mandated-report filing where applicable
4. **Communication**: with learner (age-appropriate), guardian (where relevant), MOE (cohort cases),
   sub-processors (where they have a role)
5. **Documentation**: incident record in `00_governance/safeguarding_incident_log.jsonl` (private,
   sovereignty-restricted)
6. **Review** (within 7d): Officer + Director + relevant Commission member review for systemic causes
7. **Board reporting**: aggregate quarterly to Board

## 10. Training

- Officer: annual safeguarding training (UNICEF or equivalent provider)
- Foundation staff + Commission members + volunteer elders: annual safeguarding refresher
- Engineering: annual code-of-practice review (especially for guardrail tuning)
- Documentation in `legal/safeguarding_training_records.jsonl`

## 11. Review

Framework reviewed annually by Officer + Board. Material changes notified to users per Privacy Policy §10.

## 12. Cross-references

- Privacy Policy `legal/privacy_policy.md`
- Terms of Service `legal/terms_of_service.md`
- DPA Template `legal/dpa_template.md`
- M-P3.E guardrails — `40_mcp_server/nisamina_mcp/guardrails/{crisis_fallback,no_impersonation,sacred_knowledge,off_topic,session_breaks,age_appropriate,disclosure}.py`
- F-031 Commission consultation + per-MOE collaboration
- F-055 axis #6 per-MOE sovereignty (cohort data residency)
- F-072 PHASE-A pre-pilot blockers + F-074 PHASE-NOW/PHASE-LATER split

---

*Buguya nuani Wamaraga.*
