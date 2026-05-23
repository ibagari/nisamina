# Nisamina engine API (`50_app/api/`)

**Status:** D-070 scaffold (FastAPI bridge serving Python engine → Next.js UI).

## Why this exists

The Next.js UI at `50_app/web/` cannot run Python directly. This thin FastAPI
layer exposes selected engine state via HTTP/JSON so the UI can fetch:

- pathway resolution (mirrors client-side `resolvePathway()`)
- chart catalog browse (`/api/v1/charts`)
- single chart detail with trilingual items (`/api/v1/charts/{chart_id}`)
- per-envir/per-pathway lesson list + detail (`/api/v1/envir/{envir}/pathway/{pathway}/lessons`)
- learner badges (`/api/v1/badges/{learner_id}`)

## Run

```bash
pip install -r 50_app/api/requirements.txt
cd 50_app/api
uvicorn main:app --reload --port 8000
```

Then visit:
- http://localhost:8000/docs — interactive OpenAPI explorer
- http://localhost:8000/api/v1/charts — chart catalog
- http://localhost:8000/health — health check

The Next.js dev server (port 3000) is CORS-allowed.

## Per-MOE sovereignty

Per F-055 axis #6, the `/api/v1/envir/{envir}/...` routes enforce per-MOE
data residency at the route layer. Production deployment runs **one
FastAPI instance per envir region**; the `{envir}` path parameter is
validated against the instance's allowed envirs.

## Deferred (multi-session)

- Write endpoints (POST tutor turn, POST badge revocation, POST neologism
  proposal) — not in D-070 scope
- Auth (currently anonymous read-only; production wires per-MOE LTI 1.3
  identity tokens)
- Rate limiting + per-cohort quota — production-side concern
- WebSocket streaming for SocraticTutor real-time scaffold feedback
- gRPC alternative for high-throughput cohort-LRS routing
