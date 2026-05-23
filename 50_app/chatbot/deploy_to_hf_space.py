#!/usr/bin/env python3
"""Python deploy helper for the Nisamina chatbot HF Space.

Replaces deploy_to_hf_space.sh's git-push-with-token-in-URL pattern (per F-069
SECURITY remediation + F-074 PN-2). Uses huggingface_hub.HfApi.upload_folder
which:
- Passes the token in HTTP headers (NOT in any URL string)
- Never writes the token to .git/config (no LFS-section leak)
- Auto-handles LFS uploads server-side (no client-side git-lfs install needed)
- Atomic per-commit (less chance of partial-push failures)
- Cleaner Python error handling than bash + curl + git push pipes

Usage:
    export HF_TOKEN=hf_xxxx
    python3 50_app/chatbot/deploy_to_hf_space.py

What this does (matching deploy_to_hf_space.sh's staging logic):
1. Authenticate via HfApi(token=$HF_TOKEN).
2. Create the Space if it doesn't exist (ibagari/nisamina-chatbot-phase3-interim).
3. Stage files into a temporary deploy workdir:
   - chatbot scaffold: __init__.py + brain.py + orchestrator.py + app.py +
     tts_garifuna.py + requirements.txt + Space README with YAML frontmatter
   - MCP server tree (recursive)
   - garifuna_bench tree (recursive, including subpackages)
   - foundry corpus + governance ledgers + lexicon gates + 99_publish/strip_linter
4. Strip __pycache__/*.pyc clutter.
5. Upload_folder to the Space with a deploy commit message.
6. Print Space URL + smoke-test prompts.

Authority: F-069 token-leak remediation + F-074 PHASE-NOW PN-2 + D-055 GGUF brain.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path


# === Configuration ==========================================================

SPACE_OWNER = os.environ.get("HF_SPACE_OWNER", "ibagari")
SPACE_NAME = os.environ.get("HF_SPACE_NAME", "nisamina-chatbot-phase3-interim")
SPACE_SDK = os.environ.get("HF_SPACE_SDK", "gradio")

REPO_ROOT = Path(__file__).resolve().parents[2]  # nisamina-app/


# === Helpers ================================================================

def log(msg: str) -> None:
    print(f"\033[32m[deploy]\033[0m {msg}", flush=True)


def err(msg: str) -> None:
    print(f"\033[31m[deploy ERROR]\033[0m {msg}", file=sys.stderr, flush=True)


def warn(msg: str) -> None:
    print(f"\033[33m[deploy WARN]\033[0m {msg}", flush=True)


def safe_copy_file(src: Path, dst: Path) -> bool:
    """Copy a single file if src exists; create parent dirs. Return success."""
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def safe_copy_tree(src: Path, dst: Path) -> bool:
    """Copy a directory tree if src exists, skipping __pycache__."""
    if not src.exists():
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    return True


def strip_pycache(root: Path) -> None:
    """Remove all __pycache__/ + .pyc files under root."""
    for p in list(root.rglob("__pycache__")):
        shutil.rmtree(p, ignore_errors=True)
    for p in list(root.rglob("*.pyc")):
        try:
            p.unlink()
        except OSError:
            pass


# === Main ===================================================================

def main() -> int:
    token = os.environ.get("HF_TOKEN")
    if not token:
        err("HF_TOKEN not set. Run:  export HF_TOKEN=hf_xxxx  before invoking this script.")
        return 1

    try:
        from huggingface_hub import HfApi
    except ImportError:
        err("huggingface_hub required. Install with:  pip install -U huggingface_hub")
        return 1

    api = HfApi(token=token)
    repo_id = f"{SPACE_OWNER}/{SPACE_NAME}"

    log(f"HF Space target: {repo_id}  (SDK={SPACE_SDK})")
    log("Authenticating + ensuring Space exists")
    try:
        whoami = api.whoami()
        log(f"Authenticated as: {whoami.get('name', '?')}")
    except Exception as e:
        err(f"whoami failed: {e}")
        return 1

    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk=SPACE_SDK,
            exist_ok=True,
        )
    except Exception as e:
        err(f"create_repo failed: {e}")
        return 1

    # Stage files into a temp dir
    with tempfile.TemporaryDirectory(prefix="nisamina-deploy-") as tmp:
        stage = Path(tmp)
        log(f"Staging into: {stage}")

        # 1. Chatbot scaffold (flat at root)
        chatbot = REPO_ROOT / "50_app" / "chatbot"
        for fname in ("__init__.py", "brain.py", "orchestrator.py", "app.py",
                      "tts_garifuna.py", "requirements.txt"):
            safe_copy_file(chatbot / fname, stage / fname)
        # Space README is the chatbot README + YAML frontmatter
        safe_copy_file(chatbot / "README.md", stage / "SPACE_README.md")
        (stage / "README.md").write_text(_space_readme_yaml())

        # 2. MCP server tree
        safe_copy_tree(REPO_ROOT / "40_mcp_server" / "nisamina_mcp", stage / "nisamina_mcp")

        # 3. garifuna_bench tree (including subpackages — tasks/ + fixtures/)
        safe_copy_tree(REPO_ROOT / "80_validation" / "garifuna_bench", stage / "garifuna_bench")

        # 3b. D-071: LMS engine bundle — orchestrator imports lms._engine for
        # SocraticTutor + CompositeVerifier + KGRAPH + MasteryGate + Pathway etc.
        # Without this bundle, orchestrator falls back to _LMS_AVAILABLE=False and
        # tutor features are dark on HF Space.
        (stage / "lms").mkdir(parents=True, exist_ok=True)
        # Empty package init so `lms` is importable
        (stage / "lms" / "__init__.py").write_text(
            '"""Nisamina LMS engine package (HF Space layout)."""\n'
        )
        safe_copy_tree(REPO_ROOT / "50_app" / "lms" / "_engine", stage / "lms" / "_engine")

        # 4. Foundry corpus (LFS-uploaded automatically by HfApi)
        safe_copy_file(
            REPO_ROOT / "30_lexicon" / "foundry_v6" / "foundry_v6_v0_2.jsonl",
            stage / "30_lexicon" / "foundry_v6" / "foundry_v6_v0_2.jsonl",
        )

        # 5. Egress dependencies
        safe_copy_file(REPO_ROOT / "99_publish" / "strip_linter.py", stage / "99_publish" / "strip_linter.py")
        for gate in ("jw_quarantine_filter.py", "magarada_preliminary_gate.py",
                     "catatu_archival_gate.py", "english_language_gate.py"):
            safe_copy_file(REPO_ROOT / "30_lexicon" / gate, stage / "30_lexicon" / gate)

        # 6. Cayetano normalizer
        safe_copy_file(
            REPO_ROOT / "20_normalize" / "cayetano_1992.py",
            stage / "20_normalize" / "cayetano_1992.py",
        )

        # 7. Attribution + consent (cite_sources reads these)
        for fname in ("attribution_register.jsonl", "consent_registry.jsonl"):
            safe_copy_file(REPO_ROOT / "00_governance" / fname, stage / "00_governance" / fname)

        # Strip pycache to keep deploy clean
        strip_pycache(stage)

        # 8. Upload — token goes in HTTP headers, never in any URL
        log("Uploading folder to HF Space (LFS handled server-side)")
        try:
            commit_info = api.upload_folder(
                folder_path=str(stage),
                repo_id=repo_id,
                repo_type="space",
                commit_message="Phase-3 interim chatbot deploy (M-P3.A engineer-build)",
            )
            log(f"Push succeeded — commit: {commit_info.oid[:8] if hasattr(commit_info, 'oid') else commit_info}")
        except Exception as e:
            err(f"upload_folder failed: {e}")
            return 1

    log_summary(repo_id)
    return 0


def _space_readme_yaml() -> str:
    return """---
title: Nisamina Chatbot Phase-3 Interim
emoji: 🪶
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 5.0.0
python_version: "3.12"
app_file: app.py
pinned: false
license: cc-by-nc-sa-4.0
---

# Nisamina · Garifuna Language Assistant (Phase-3 interim)

Grounded-only Garifuna learning chatbot. Apache 2.0 brain
(`google/gemma-4-E4B-it` via GGUF Q4_K_M; not gated; 256K context; 140+ languages).
License: Labayayahoun Ibagari + CC-BY-NC-SA 4.0.

See `SPACE_README.md` for the full deploy + architecture notes.
"""


def log_summary(repo_id: str) -> None:
    space_url = f"https://huggingface.co/spaces/{repo_id}"
    print(f"""
{'-' * 72}
Deploy submitted.

Space URL:    {space_url}
Build logs:   {space_url}/logs/build

First-boot will:
  - pip-install llama-cpp-python + huggingface_hub + transformers + torch + gradio
  - Download GGUF: unsloth/gemma-4-E4B-it-GGUF / gemma-4-E4B-it-Q4_K_M.gguf (~4.7 GB)
  - Launch the Gradio Blocks UI at the Space URL

Smoke-test on the live Space:
  - "What does abayayahouni mean?"   (Tier-5 V_VAULT)
  - "How do you say 'my name is' in Garifuna?"
  - "What is walagallo?"             (anthropological recognition OK)
  - "Can you teach me numbers 1 to 5?"

Per M-P3.A safety contract:
  - Crisis signals → regional emergency resources (988 / 144 / 132 / etc.)
  - Impersonation asks → refusal + referral
  - Sacred-knowledge specifics → community elder / Commission routing
  - 3-hour California-law hard-stop
{'-' * 72}
""", flush=True)


if __name__ == "__main__":
    sys.exit(main())
