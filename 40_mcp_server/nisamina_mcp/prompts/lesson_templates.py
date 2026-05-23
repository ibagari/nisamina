"""Parametrized Garifuna lesson prompts — foundry-attested examples ONLY.

Per plan v1 line 170: prompts pull example sentences directly from the
foundry's `examples[]` field. They do NOT ask the LLM to generate Garifuna
content from scratch; the LLM's role is pedagogical framing around attested
examples (translation, contextualization, drilling).

Each template returns a fully-rendered prompt string the MCP client passes
to the LLM. Source IDs are appended so the LLM (and the human reader) can
trace every Garifuna fragment to its foundry record.
"""
from __future__ import annotations

from ..foundry_loader import FoundryIndex


def vocab_drill_prompt(index: FoundryIndex, headword: str) -> str | None:
    """Return a vocab-drill prompt for `headword` using its foundry examples.

    Returns None if the headword is not in the public foundry.
    """
    matches = index.lookup_exact(headword)
    if not matches:
        return None
    rec = matches[0]
    sense_lines: list[str] = []
    for i, s in enumerate(rec.get("senses", []) or []):
        gloss = s.get("gloss_en") or "(no gloss)"
        pos = s.get("pos") or "(no pos)"
        sense_lines.append(f"  {i+1}. ({pos}) {gloss}  [source: {s.get('source', '?')}]")
    example_lines: list[str] = []
    for ex in rec.get("examples", []) or []:
        example_lines.append(f"  - GAR: {ex.get('gar', '?')}")
        example_lines.append(f"    EN:  {ex.get('en', '?')}")
        example_lines.append(f"    [source: {ex.get('source', '?')}]")
    sources_str = ", ".join(rec.get("sources", []) or [])
    return (
        f"You are tutoring a learner studying Garifuna. The headword is **{rec.get('headword')}** "
        f"(normalized: {rec.get('headword_normalized')}, tier {rec.get('tier')}).\n\n"
        f"Recorded senses (from the foundry — do NOT invent additional ones):\n"
        f"{chr(10).join(sense_lines) if sense_lines else '  (no senses recorded)'}\n\n"
        f"Recorded examples (from the foundry — do NOT invent additional ones):\n"
        f"{chr(10).join(example_lines) if example_lines else '  (no examples recorded)'}\n\n"
        f"Task: walk the learner through these recorded materials. For each sense, briefly explain the "
        f"meaning in English, point out morphological structure if recorded, and contextualize when one would use it. "
        f"Then read the recorded examples slowly and break down how the headword is used in each. "
        f"Do NOT invent new Garifuna sentences or new glosses — limit yourself to the recorded foundry content. "
        f"If the learner asks for more examples and there are none recorded, say so honestly and suggest they "
        f"check `lookup_headword` for related headwords.\n\n"
        f"Source IDs (cite when concluding): {sources_str}"
    )


def sentence_breakdown_prompt(index: FoundryIndex, sentence: str) -> str:
    """Return a sentence-breakdown prompt that pre-resolves token glosses
    from the foundry (so the LLM works with attested data, not guesses).
    """
    # Build a token-by-token gloss line from the foundry.
    import re
    tokens = re.findall(r"[A-Za-zÀ-ÿñÑüÜ'\-]+", sentence)
    gloss_lines: list[str] = []
    for tok in tokens:
        matches = index.lookup_exact(tok)
        if matches:
            r = matches[0]
            first_sense = (r.get("senses") or [{}])[0]
            gloss = first_sense.get("gloss_en") or "(no gloss recorded)"
            src = (r.get("sources") or ["?"])[0]
            gloss_lines.append(f"  - {tok}  →  {gloss}  [source: {src}]")
        else:
            gloss_lines.append(f"  - {tok}  →  (NOT IN FOUNDRY — do not invent a gloss)")
    return (
        f"You are helping a learner parse a Garifuna sentence. Sentence:\n\n"
        f"  > {sentence}\n\n"
        f"Per-token foundry lookup (use ONLY these glosses; do NOT invent meanings for unmatched tokens):\n"
        f"{chr(10).join(gloss_lines)}\n\n"
        f"Task: walk the learner through the sentence's literal structure using ONLY the foundry-attested glosses above. "
        f"For any token marked NOT IN FOUNDRY, explicitly say it is not in the dictionary and you cannot translate it. "
        f"Conclude with a one-line English approximation if and only if every token has a recorded gloss; otherwise "
        f"explain which tokens block a complete translation."
    )


PROMPT_REGISTRY: dict[str, str] = {
    # name -> short description (shown to MCP client)
    "vocab_drill": "Walk a learner through a single headword using its foundry-recorded senses + examples only.",
    "sentence_breakdown": "Per-token parse of a Garifuna sentence using foundry-attested glosses only.",
}
