"""Brain loader for the Nisamina chatbot.

Phase-3 interim: Gemma 3 4B-Instruct (Apache 2.0; ~2.5 GB 4-bit; HF Space free
tier). Phase-5 final: Gemma-4-E4B-Nisamina (fine-tune of Gemma 4 E4B).

Two modes:
- `MockBrain` — deterministic response for tests / CI; no model download
- Real-mode `load_brain()` — loads `google/gemma-4-E4B-it` via transformers +
  bitsandbytes 4-bit quantization on HF Space; cold-start ~30s

The real-mode import of `transformers` is lazy so this module imports cleanly
in test environments where transformers isn't installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


GEMMA4_E4B_IT_REPO: str = "google/gemma-4-E4B-it"  # Phase-3 interim brain (Apache 2.0; not gated; 256K context; 140+ langs)
# Backwards-compat alias for any external code still referencing the legacy name.
GEMMA3_4B_IT_REPO: str = GEMMA4_E4B_IT_REPO
PHASE5_FINAL_REPO_TARGET: str = "ibagari/gemma-4-e4b-nisamina"  # Phase-5 final = same base, fine-tuned
DEFAULT_MAX_TOKENS: int = 512
DEFAULT_TEMPERATURE: float = 0.3


@dataclass
class Brain:
    """Abstract brain interface.

    Implementations: `MockBrain` (test/dev), `HFTransformersBrain` (HF Space).
    """

    model_repo: str
    is_real: bool = False
    _client: Any = field(default=None, repr=False)

    def generate(
        self,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        raise NotImplementedError("subclass must implement generate()")


@dataclass
class MockBrain(Brain):
    """Deterministic test/dev brain.

    Returns a response that echoes a portion of the prompt + appends a fixed
    suffix so orchestrator tests can verify the brain was called and the
    response routes through post-screens correctly.
    """

    def __init__(
        self,
        canned_response: Optional[str] = None,
        echo_last_user_message: bool = True,
    ) -> None:
        super().__init__(model_repo="mock://MockBrain", is_real=False)
        self.canned_response = canned_response
        self.echo_last_user_message = echo_last_user_message

    def generate(
        self,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        if self.canned_response is not None:
            return self.canned_response
        # Extract the last "user:" segment if present; otherwise echo head
        last_user = prompt.rsplit("user:", 1)
        if len(last_user) > 1:
            user_text = last_user[1].split("\n", 1)[0].strip()[:100]
        else:
            user_text = prompt[:100]
        return (
            f"[MOCK BRAIN] Acknowledged: {user_text!r}. "
            "In real-mode this is where Gemma 3 4B-Instruct would respond "
            "using the MCP-retrieved foundry context. Buguya nuani."
        )


# GGUF brain config (D-055 Path A; per F-064 free-tier deployment)
GGUF_REPO: str = "unsloth/gemma-4-E4B-it-GGUF"
GGUF_FILENAME: str = "gemma-4-E4B-it-Q4_K_M.gguf"  # 4.7 GB; quality ~95% of FP16; CPU-friendly
GGUF_CONTEXT_WINDOW: int = 8192  # Gemma 4 supports up to 256K; 8K is enough for chatbot + safer on free-tier RAM


def load_brain(
    repo: str = GGUF_REPO,
    filename: str = GGUF_FILENAME,
    real_mode: bool = False,
    n_ctx: int = GGUF_CONTEXT_WINDOW,
    n_threads: Optional[int] = None,
) -> Brain:
    """Load the brain.

    - `real_mode=False` (default) → returns a `MockBrain` for tests / dev /
      pre-deploy environments without llama-cpp-python installed.
    - `real_mode=True` → lazy-import llama-cpp-python and load a GGUF
      quantization (default: gemma-4-E4B-it Q4_K_M; ~4.7 GB; Apache 2.0;
      free-tier CPU-friendly). Raises ImportError with a clear message
      if dependencies are missing.

    Why GGUF: HF Space free-tier CPU-basic has ~16 GB RAM. Loading the full
    BF16 16 GB safetensors OOMs during forward pass; Q4_K_M fits in ~5 GB with
    headroom for the rest of the chatbot pipeline. Per D-055 + F-064.

    HF Space deploy uses `real_mode=True`. Engineer-side dev uses default
    `real_mode=False`.
    """
    if not real_mode:
        return MockBrain()

    try:
        from llama_cpp import Llama
    except ImportError as e:
        raise ImportError(
            "llama-cpp-python required for real-mode brain (GGUF Path A). "
            "On HF Space: ensure requirements.txt includes 'llama-cpp-python>=0.3'. "
            f"Underlying: {e}"
        ) from e

    llm = Llama.from_pretrained(
        repo_id=repo,
        filename=filename,
        n_ctx=n_ctx,
        n_threads=n_threads,  # None = auto-detect; HF free-tier gives ~2-4 cores
        verbose=False,
    )
    return _LlamaCppBrain(repo=repo, filename=filename, llm=llm)


class _LlamaCppBrain(Brain):
    """Real-mode brain backed by llama-cpp-python loading a GGUF quantization."""

    def __init__(self, repo: str, filename: str, llm: Any) -> None:
        super().__init__(model_repo=f"{repo}/{filename}", is_real=True)
        self.llm = llm

    def generate(
        self,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        out = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<end_of_turn>", "<|im_end|>", "</s>"],  # Gemma chat-template + common stop tokens
        )
        text = out["choices"][0]["text"]
        return text.strip()
