# Nisamina chatbot — Phase-3 interim deploy

**Manifest:** `90_supervisor/manifests/M-P3.A_chatbot_brain_deploy.md`
**Decision:** D-039 Wave-2 #2 lock (Phase-3 interim brain = Gemma 3 4B-Instruct, NOT Gemma 4 E4B — that's Phase-5 fine-tune target)
**License:** Labayayahoun Ibagari (Foundation guardianship) + CC-BY-NC-SA 4.0 platform wrapper · brain Apache 2.0

## What this is

The Nisamina chatbot's **orchestration code + HF Space scaffold**. The orchestrator wires four existing platform components into a grounded, guardrail-screened conversation pipeline:

- **Brain:** `google/gemma-4-E4B-it` (Apache 2.0; not gated; 256K context; multilingual 140+ langs; HF Space free tier viable)
- **System prompt:** `40_mcp_server/nisamina_mcp/guardrails/system_prompt_v1.md`
- **Safety guardrails (M-P3.E):** `40_mcp_server/nisamina_mcp/guardrails/{sacred_knowledge, crisis_fallback, no_impersonation, off_topic, session_breaks, disclosure, age_appropriate}.py`
- **MCP grounding (M-P2):** `40_mcp_server/nisamina_mcp/tools/{lookup_headword, cite_sources, cayetano_normalize, parse_morphology, translate_sentence}.py`

Phase-5 target: swap `model_repo` from `google/gemma-4-E4B-it` → `ibagari/gemma-4-e4b-nisamina` (fine-tune on Garifuna corpus). Same base model, zero architectural drift — Phase-3 interim and Phase-5 final are the same family.

## Files

| File | Purpose |
|---|---|
| `__init__.py` | Package exports — `Orchestrator`, `SessionState`, `OrchestratorResponse`, `Brain`, `MockBrain`, `load_brain` |
| `brain.py` | Brain abstraction — `MockBrain` for tests, real-mode `load_brain()` for HF Space |
| `orchestrator.py` | 10-step pipeline per M-P3.A §4 |
| `app.py` | HF Space entrypoint (Gradio ChatInterface) |
| `requirements.txt` | HF Space Python dependencies |
| `tests/test_orchestrator.py` | Unit tests with mocked brain |
| `README.md` | This file |

## How to run locally (engineer-side test mode)

```bash
cd "/Volumes/AI External/Nisamina_ai_Claude/nisamina-app"
python3 -m pytest 50_app/chatbot/tests/ -v
# Expected: all chatbot tests pass; mocked brain; no model download
```

## How to deploy to HF Space (director-runs-it)

The engineer cannot push to HF Space (no auth). Director performs:

1. **Create the Space** at https://huggingface.co/new-space:
   - **Owner:** ibagari (or director's HF org/account)
   - **Space name:** `nisamina-chatbot-phase3-interim`
   - **License:** CC-BY-NC-SA 4.0 (or Labayayahoun Ibagari — TBD post-Commission)
   - **Space SDK:** Gradio
   - **Python version:** 3.11+
   - **Hardware:** CPU basic (free tier; cold-start ~30s acceptable)

2. **No license-acceptance needed** — `google/gemma-4-E4B-it` is Apache 2.0 + not gated. No Space secret required.

3. **Copy this directory** to the Space repo root + push:
   ```bash
   git clone https://huggingface.co/spaces/ibagari/nisamina-chatbot-phase3-interim
   cd nisamina-chatbot-phase3-interim
   cp -r /Volumes/AI\ External/Nisamina_ai_Claude/nisamina-app/50_app/chatbot/* .
   # Also need MCP server + guardrails + foundry V0.2:
   mkdir -p nisamina_mcp
   cp -r /Volumes/AI\ External/Nisamina_ai_Claude/nisamina-app/40_mcp_server/nisamina_mcp/* nisamina_mcp/
   cp /Volumes/AI\ External/Nisamina_ai_Claude/nisamina-app/30_lexicon/foundry_v6/foundry_v6_v0_2.jsonl foundry_v6_v0_2.jsonl
   git add . && git commit -m "Initial deploy of Phase-3 interim chatbot" && git push
   ```

4. **First boot** downloads `google/gemma-4-E4B-it` weights (~10-15 min on free tier; size depends on quantization config). Subsequent boots ~30s cold-start.

5. **Smoke test** the live Space with the four example queries baked into the Gradio interface:
   - "What does abayayahouni mean?" — should cite Tier-5 V_VAULT
   - "How do you say 'my name is' in Garifuna?" — should retrieve IRI conjugation context
   - "What is walagallo?" — anthropological-recognition level OK; ritual specifics route to elder
   - "Can you teach me numbers 1 to 5?" — should retrieve Annex F Numeru content (when curriculum is ingested)

## Architecture (10-step pipeline)

```
user message
    │
    ├──▶ [1] crisis screen ─▶ crisis_fallback response ─▶ return
    ├──▶ [2] impersonation screen ─▶ refusal + referral ─▶ return
    ├──▶ [3] sacred-knowledge screen ─▶ TK SS routing ─▶ return
    ├──▶ [4] off-topic screen ─▶ scope redirect ─▶ return
    ├──▶ [5] hard-stop check (3-hr CA limit) ─▶ return
    ├──▶ [6] MCP retrieval — extract Garifuna tokens, lookup_headword
    ├──▶ [7] augmented prompt — system + foundry-context + user
    ├──▶ [8] brain.generate(prompt) — Gemma 3 4B-Instruct
    ├──▶ [9] hallucination check (MEGA-RAG-style multi-evidence)
    ├──▶ [10] egress strip_linter — final defense
    │
    └──▶ Response + citations + flagged-tokens + session_state
```

## Phase-5 swap path

When the fine-tune lands:

```python
# In brain.py:
GEMMA3_4B_IT_REPO = "ibagari/gemma-4-e4b-nisamina"  # Phase-5 swap
```

That's the entire change at the deploy layer. Orchestrator + guardrails + MCP wiring stay identical because Gemma 3 4B → Gemma 4 E4B is same family + same prompt format + same tokenizer behavior.

## Honest limitations

- Phase-3 interim brain isn't fine-tuned on Garifuna; its first-pass Garifuna generation will be weak. **The orchestrator's grounded-only contract is the substitute** — every Garifuna fact in a response comes from MCP retrieval, not the brain's prior.
- Cold-start on HF Space free tier is ~30s; HF Space sleeps after ~30 min inactivity.
- No streaming token-by-token output yet (Gradio ChatInterface gives basic streaming for free; richer streaming is M-P3.UI.D).
- No persistent conversation history across cold-starts (IndexedDB persistence is M-P3.UI.D).
- No voice I/O (Web Speech API + Whisper-cab is M-P3.UI.D + M-P3.D).
- No production hardening (rate-limit, abuse-detection, observability) — free tier scope.

## Citation chain

- F-033 chatbot architecture brief (supervisor S12)
- F-033-OVERRIDE (Gemma 4 E4B Phase-5 final target)
- D-016 (open-weight LLM only; sovereignty-max)
- D-030 (Phase-3 interim Gemma 3 4B-Instruct)
- D-039 (Phase-3 brain verified NOT e4b)
- D-041 (M-P3.LMS.DEMO Wave-2 #1)
- M-P3.E safety guardrails (8-file library)
- M-P2 MCP server (5 tools + 4 resources + 2 prompts)
- M-P3.G GarifunaBench scaffold
- A-P1.E.fix.2 foundry V0.2 surgical correction (agüriahati spelling)
- Labayayahoun Ibagari license framework (D-027 + D-029)
- WCAG 2.2 AA + UNESCO 2025 + GUARD Act + California 2025

*Buguya nuani Wamaraga.*
