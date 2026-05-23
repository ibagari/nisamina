# Nisamina V3 Web App (M-P3.UI.A)

**Stack:** Next.js 15 + React 19 + Tailwind v4 + shadcn/ui + Radix + next-intl + Workbox 7
**Authority:** F-034 May 2026 UI standards + D-039 Wave-2 + WCAG 2.2 AA federal deadline (April 24 2026)
**License:** Labayayahoun Ibagari + CC-BY-NC-SA 4.0

## What this is

The frontend scaffold for the Nisamina V3 platform. Single Next.js app that hosts three modes (Learner / Practitioner / Heritage) + the chatbot UI (M-P3.UI.D) + the claim-attribution portal (M-P3.UI.F) + the LMS pilot (M-P3.LMS.A).

Engineer-built source files; director runs `npm install` + `npm run dev` to materialize node_modules.

## How to run (director-runs-it)

```bash
cd "/Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/web"
npm install          # ~3-5 min; pulls Next.js + React + Tailwind v4 + Radix + shadcn deps
npm run dev          # starts dev server at http://localhost:3000
```

For production build:
```bash
npm run build
npm run start
```

## Stack rationale

- **Next.js 15** — Server Components default + Partial Prerendering + Suspense streaming (S13 brief §1.1)
- **React 19** — paired with Next.js 15
- **Tailwind v4** — utility-first; design-token-first via CSS variables (HSL color tokens enable Tailwind utility classes + CSS-var-driven theming)
- **shadcn/ui** — copy-not-install component pattern (D-016 sovereignty-max; no npm vendor lock-in); components live in `components/ui/` and we own them
- **Radix UI primitives** — WAI-ARIA compliant accessibility primitives (Dialog, Tabs, Tooltip, Popover, Slot)
- **next-intl** — locale routing + message resolution; English (en) / Garifuna (cab) / Spanish (es) / Belize Kriol (kr)
- **Workbox 7** — PWA service worker for offline-first (M-P3.UI.D scope; declared in package.json devDependencies)

## WCAG 2.2 AA targets (per F-034 + federal April 24 2026 deadline)

- Color contrast ≥4.5:1 normal text, ≥3:1 UI components (CSS variables tuned: foreground on background ≈15:1)
- Focus indicators (SC 2.4.7 + 2.4.11) — `:focus-visible` global ring + ≥0.1875rem outline
- Touch targets ≥44×44px (SC 2.5.8 — new in 2.2) — `min-h-tap` + `min-w-tap` Tailwind utilities + Button component
- Reduced motion respected (SC 2.3.3) — `@media (prefers-reduced-motion: reduce)` global override
- Skip-link to `#main-content` (SC 2.4.1) — visible on focus
- Semantic landmarks (`<header>` + `<main>` + `<section>` + `<footer>`)
- ARIA labels on every section + nav
- Dyslexia-friendly font toggle (research per F-034 §1.6)
- High-contrast mode toggle

Pre-deploy: `npm run test:a11y` (axe-core) + `npm run lighthouse` (Lighthouse CI; Lighthouse A11y ≥95 + PWA ≥90 gate).

## Directory structure

```
50_app/web/
├── app/
│   ├── layout.tsx              — root layout + NextIntlClientProvider + skip-link
│   ├── page.tsx                — home page with 3 modes + cultural-protocol + footer
│   └── [routes...]             — future: /learner/ /practitioner/ /heritage/ /lexicon/ /chatbot/ /lms/
├── components/
│   └── ui/
│       ├── button.tsx          — shadcn/ui Button with WCAG 2.5.8 touch targets
│       └── card.tsx            — shadcn/ui Card + CardHeader/Title/Description/Content/Footer
├── lib/
│   └── utils.ts                — cn() class-merge helper
├── styles/
│   └── globals.css             — Tailwind v4 + design tokens (HSL) + a11y + dyslexic toggle
├── messages/
│   ├── en.json                 — English (canonical)
│   ├── cab.json                — Garifuna (community translation pending; flagged [pending])
│   ├── es.json                 — Spanish (translated)
│   └── kr.json                 — Belize Kriol (community translation pending)
├── public/                     — static assets (favicons, og-images, etc.)
├── package.json                — Next.js 15 + React 19 + Tailwind v4 + shadcn deps
├── tsconfig.json
├── next.config.mjs             — with createNextIntlPlugin
├── tailwind.config.ts          — design tokens + min-h-tap WCAG target
├── postcss.config.mjs
├── i18n.ts                     — next-intl request config (en/cab/es/kr)
└── README.md                   — this file
```

## Cultural-protocol surfacing (per Labayayahoun Ibagari)

The home page renders the locked principle text in the user's locale (translations to cab/kr pending community translation pipeline). The chatbot route (M-P3.UI.D, queued) will surface the sacred-knowledge TK SS routing inline at every relevant response per M-P3.E guardrails.

## What's deferred (honest, per fired-engineer rule 4)

- **No node_modules** installed (director runs `npm install`)
- **No /learner/ /practitioner/ /heritage/ routes** built — those are M-P3.UI.B/C scope
- **No chatbot embed** — M-P3.UI.D pulls in the HF Space chatbot via iframe or fetch + streams
- **No claim-attribution form** — M-P3.UI.F per D-034 scope
- **No LMS pilot integration** — M-P3.LMS.A pulls in Moodle via LTI 1.3
- **No Workbox 7 service-worker config** — declared in package.json devDependencies; worker registration is M-P3.UI.E scope
- **No axe-core CI integration** — `test:a11y` script declared; CI wiring is M-P3.UI.E
- **No Lighthouse CI config** — `lighthouse` script declared; LHCI config is M-P3.UI.E
- **No Cloudflare Pages config** — deploy config is M-P3.UI.E
- **No actual TLS cert / domain setup** — `garifunalearningacademy.com` DNS not yet configured per HANDOFF.md §1
- **No community translations** of cab.json or kr.json — pipeline pending; English + Spanish are first-class
- **No images / og-images / favicons** — `public/` is empty scaffold

## Cross-references

- F-034 May 2026 UI standards (supervisor S13 brief)
- D-016 sovereignty-max (no proprietary vendor lock-in)
- D-027 + D-029 Labayayahoun Ibagari license framework
- D-039 Wave-2 lock
- M-P3.E safety guardrails (chatbot UI route wires these per M-P3.UI.D)
- M-P3.LMS.MULTI_ENVIR 6-envir scaffold (LMS pilot integrates per-envir)
- WCAG 2.2 W3C Recommendation (federal April 24 2026 deadline)

*Buguya nuani Wamaraga.*
