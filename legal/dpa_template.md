# Data Processing Agreement — Template (DRAFT)

**Status:** DRAFT (per F-072-A1 + F-074 PN-5). Foundation legal counsel finalizes
per-counterparty negotiation (G14 PHASE-LATER). Engineer template; not legal advice.

**Version:** 0.1 — 2026-05-23

---

This Data Processing Agreement ("DPA") forms part of the platform-access or sub-processor agreement
between **Ibagari Foundation** (the *Controller*) and **{{COUNTERPARTY_NAME}}** (the *Processor*).

## 1. Definitions

Capitalized terms follow GDPR Article 4 definitions. "Personal Data" = any data that identifies or could
identify a natural person. "Sub-Processor" = any third party engaged by Processor to perform Personal-Data
processing on behalf of Controller.

## 2. Scope + subject matter

The Processor processes Personal Data only for the purposes set out in **Schedule A** (services, data
categories, data subjects, processing operations). Any processing outside Schedule A scope is prohibited.

## 3. Processor obligations

The Processor agrees to:
1. **Process only on documented instructions** from Controller (these instructions are reflected in
   Schedule A + any subsequent written amendments)
2. **Confidentiality** — ensure persons authorized to process Personal Data have committed themselves to
   confidentiality (or are under statutory obligation)
3. **Security** — implement appropriate technical and organizational measures per GDPR Article 32,
   including: encryption at rest + in transit (TLS 1.3+); access controls; audit logging; incident
   detection
4. **Sub-Processors** — engage sub-processors only with prior specific or general written authorization
   from Controller; maintain a current sub-processor list (Schedule B); flow down DPA terms
5. **Assistance with data-subject rights** — assist Controller fulfilling access/correction/deletion/portability
   requests within 10 business days
6. **Assistance with security + breach notification** — assist with risk assessments + data protection
   impact assessments; notify Controller of any Personal Data breach within 72 hours of becoming aware
7. **Return or delete Personal Data** at termination of services (Controller chooses); certify in writing
8. **Audit cooperation** — make available all information necessary to demonstrate compliance + permit
   audits at reasonable notice (no more than once per 12 months absent suspected breach)

## 4. International transfers

If Processor transfers Personal Data outside the data subject's residence jurisdiction, Processor must
ensure adequate safeguards per GDPR Chapter V (or equivalent under SVG DPA / Belize DPA / etc.):
- EU Standard Contractual Clauses (SCCs) where applicable
- UK International Data Transfer Agreement (IDTA) for UK-origin data
- Belize / Honduras / Guatemala / Nicaragua / SVG equivalents

For US-origin data transfers: rely on adequacy decisions, SCCs with supplementary measures, or
data-subject explicit consent.

## 5. Per-MOE sovereignty (Foundation-specific)

Per F-055 axis #6, Personal Data collected for a specific MOE cohort (Belize/Honduras/Guatemala/Nicaragua/SVG)
stays within that envir's data residency. Sub-processors handling per-MOE data must:
- Honor the data-residency constraint
- Refuse cross-envir queries originating outside the MOE's institutional channel
- Allow MOE to request deletion of MOE-cohort data without affecting other envirs

## 6. Children's data (COPPA + GDPR Article 8)

Where the Processor processes data of users under 13 (COPPA) or 16 (GDPR), Processor agrees to:
- Honor the parental-consent record provided by Controller
- Disable all third-party advertising / profiling features for these data subjects
- Apply enhanced retention limits + deletion priorities

## 7. Sacred-knowledge restriction (Foundation-specific)

Per Labayayahoun Ibagari stewardship principle: Personal Data tied to sacred-knowledge routing decisions
must NOT be aggregated, sold, or used for any purpose other than the safety-routing it was collected for.
Caliper aggregate events referencing sacred-knowledge routes contain ONLY the routing decision, never
underlying content.

## 8. Term + termination

This DPA is effective from {{EFFECTIVE_DATE}} and remains in force while the underlying services
agreement is active. On termination, Processor must:
- Return or delete all Personal Data within 30 days
- Certify in writing
- Maintain confidentiality obligations indefinitely for any data that survives termination by law

## 9. Liability

Processor is liable for damages caused by processing only where it has failed to comply with this DPA or
acted outside Controller's lawful instructions, per GDPR Article 82.

## 10. Governing law

Per Foundation governing law (pending F-074 PL-A) — defaults to the law of Controller's registration
jurisdiction unless Controller + Processor agree otherwise in Schedule A.

## 11. Schedules

- **Schedule A** — Services, data categories, data subjects, processing operations (per-counterparty)
- **Schedule B** — Sub-Processor list (current; updated within 14 days of any change)
- **Schedule C** — Security measures (TOMs; aligned with ISO 27001 controls where feasible)

## 12. Signatures

**Controller:**
Ibagari Foundation
By: ________________________________   Date: __________
Title: ________________________________

**Processor:**
{{COUNTERPARTY_NAME}}
By: ________________________________   Date: __________
Title: ________________________________

---

*Buguya nuani Wamaraga.*
