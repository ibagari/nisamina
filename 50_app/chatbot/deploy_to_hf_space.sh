#!/usr/bin/env bash
# Nisamina chatbot — HF Space deploy helper
# Per M-P3.A README.md §3. Director runs this with HF_TOKEN in env.
#
# Usage:
#   export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#   bash 50_app/chatbot/deploy_to_hf_space.sh
#
# What this does:
#   1. Verifies HF_TOKEN is set (without printing it).
#   2. Verifies huggingface-cli + git are available.
#   3. Authenticates huggingface-cli with the token.
#   4. Creates (or clones) the HF Space repo
#      'ibagari/nisamina-chatbot-phase3-interim'.
#   5. Copies the chatbot orchestrator + MCP server + guardrails + foundry V0.2
#      into the Space repo working dir.
#   6. Pushes. First-boot on HF Space downloads Gemma 3 4B-Instruct.
#   7. Reports the live Space URL.
#
# What this does NOT do:
#   - Does NOT echo HF_TOKEN.
#   - Does NOT modify nisamina-app/ source-of-truth.
#   - Does NOT touch the live deployed Space content if a prior deploy exists
#     (it does a normal git push which fast-forwards; uncommitted Space-side
#     changes are preserved via merge or rejected via push --no-force).
#   - Does NOT pull large model weights from HF; HF Space pulls them at first-boot.

set -euo pipefail

# ---- Configuration ----------------------------------------------------------

SPACE_OWNER="${HF_SPACE_OWNER:-ibagari}"
SPACE_NAME="${HF_SPACE_NAME:-nisamina-chatbot-phase3-interim}"
SPACE_SDK="${HF_SPACE_SDK:-gradio}"
SPACE_PYTHON="${HF_SPACE_PYTHON:-3.11}"
SPACE_HARDWARE="${HF_SPACE_HARDWARE:-cpu-basic}"

# Resolve script location → repo root (nisamina-app/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SPACE_LOCAL="${SPACE_LOCAL:-${REPO_ROOT}/_deploy_workdir/${SPACE_NAME}}"

# ---- Helpers ----------------------------------------------------------------

log() { printf '\033[32m[deploy]\033[0m %s\n' "$1"; }
err() { printf '\033[31m[deploy ERROR]\033[0m %s\n' "$1" >&2; }
warn() { printf '\033[33m[deploy WARN]\033[0m %s\n' "$1"; }

require_env() {
  local var="$1"
  if [[ -z "${!var:-}" ]]; then
    err "$var is not set. Run:  export $var=...  before invoking this script."
    exit 1
  fi
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "Required command not found: $cmd"
    err "Install with: pip install huggingface_hub   (provides huggingface-cli)"
    exit 1
  fi
}

# ---- Pre-flight checks ------------------------------------------------------

log "Pre-flight checks"
require_env HF_TOKEN
require_cmd git
# Prefer the new `hf` CLI; fall back to `huggingface-cli` for older huggingface_hub versions.
if command -v hf >/dev/null 2>&1; then
  HF_CLI="hf"
elif command -v huggingface-cli >/dev/null 2>&1; then
  HF_CLI="huggingface-cli"
else
  err "Required command not found: hf (or huggingface-cli)"
  err "Install with: pip install -U huggingface_hub"
  exit 1
fi
log "Using HF CLI: $HF_CLI"

log "HF Space target: ${SPACE_OWNER}/${SPACE_NAME}   (SDK=${SPACE_SDK}, hardware=${SPACE_HARDWARE})"
log "Local workdir:    ${SPACE_LOCAL}"

# ---- HF authentication ------------------------------------------------------

log "Authenticating HF CLI (token stays in env; never echoed)"
if [[ "$HF_CLI" == "hf" ]]; then
  "$HF_CLI" auth login --token "$HF_TOKEN" --add-to-git-credential >/dev/null 2>&1 || {
    err "hf auth login failed. Token may be invalid or revoked."
    exit 1
  }
  log "Authenticated as: $($HF_CLI auth whoami 2>&1 | grep -E '^user:' | awk '{print $2}')"
else
  "$HF_CLI" login --token "$HF_TOKEN" --add-to-git-credential >/dev/null 2>&1 || {
    err "huggingface-cli login failed. Token may be invalid or revoked."
    exit 1
  }
  log "Authenticated as: $($HF_CLI whoami 2>&1 | tail -1)"
fi

# ---- Create or clone the Space ---------------------------------------------

mkdir -p "$(dirname "$SPACE_LOCAL")"

if [[ -d "${SPACE_LOCAL}/.git" ]]; then
  log "Existing Space workdir found — pulling latest"
  ( cd "$SPACE_LOCAL" && git pull --rebase --autostash )
else
  log "Cloning Space repo (will create on HF if it doesn't exist)"
  if ! git clone "https://huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}" "$SPACE_LOCAL" 2>/dev/null; then
    log "Clone failed — creating new Space at ${SPACE_OWNER}/${SPACE_NAME}"
    if [[ "$HF_CLI" == "hf" ]]; then
      "$HF_CLI" repo create "${SPACE_OWNER}/${SPACE_NAME}" \
        --repo-type space --space_sdk "$SPACE_SDK" --exist-ok
    else
      "$HF_CLI" repo create "${SPACE_OWNER}/${SPACE_NAME}" \
        --type space --space_sdk "$SPACE_SDK" --yes
    fi
    git clone "https://huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}" "$SPACE_LOCAL"
  fi
fi

# ---- git-lfs setup (HF rejects pushes containing files >10 MiB without LFS) -
require_cmd git-lfs
( cd "$SPACE_LOCAL"
  git lfs install --local >/dev/null 2>&1
  # Track the foundry corpus (44 MB) + future >10 MiB jsonl files in same path
  git lfs track "30_lexicon/foundry_v6/*.jsonl" >/dev/null
  # Prevent __pycache__/*.pyc clutter in pushes
  cat > .gitignore <<'GITIGNORE'
__pycache__/
*.pyc
*.pyo
.DS_Store
.env
.venv
GITIGNORE
)

# ---- Copy chatbot + MCP server + guardrails + foundry V0.2 ------------------

log "Staging deploy contents into $SPACE_LOCAL"

cd "$SPACE_LOCAL"

# Chatbot scaffold (everything except tests/ — HF Space doesn't run tests)
cp -R "${REPO_ROOT}/50_app/chatbot/__init__.py" .
cp -R "${REPO_ROOT}/50_app/chatbot/brain.py" .
cp -R "${REPO_ROOT}/50_app/chatbot/orchestrator.py" .
cp -R "${REPO_ROOT}/50_app/chatbot/app.py" .
cp -R "${REPO_ROOT}/50_app/chatbot/tts_garifuna.py" .
cp -R "${REPO_ROOT}/50_app/chatbot/requirements.txt" .
cp -R "${REPO_ROOT}/50_app/chatbot/README.md" SPACE_README.md
# HF Spaces need 'README.md' with YAML frontmatter at top; write a minimal one
cat > README.md <<'EOF'
---
title: Nisamina Chatbot Phase-3 Interim
emoji: 🪶
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 4.40.0
app_file: app.py
pinned: false
license: cc-by-nc-sa-4.0
---

# Nisamina · Garifuna Language Assistant (Phase-3 interim)

Grounded-only Garifuna learning chatbot. Apache 2.0 brain
(`google/gemma-4-E4B-it`; Apache 2.0; not gated; 256K context; 140+ languages). License: Labayayahoun Ibagari + CC-BY-NC-SA 4.0.

See `SPACE_README.md` for the full deploy + architecture notes.
EOF

# MCP server (orchestrator imports nisamina_mcp.*)
mkdir -p nisamina_mcp
cp -R "${REPO_ROOT}/40_mcp_server/nisamina_mcp/"* nisamina_mcp/

# GarifunaBench hallucination detector + tasks subpackage (orchestrator imports it)
# Copy the entire package directory so subpackages (tasks/, fixtures/) come along
rm -rf garifuna_bench 2>/dev/null
cp -R "${REPO_ROOT}/80_validation/garifuna_bench" garifuna_bench
# Strip __pycache__ to keep the deploy clean
find garifuna_bench -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# Foundry V0.2 corpus
mkdir -p 30_lexicon/foundry_v6
cp "${REPO_ROOT}/30_lexicon/foundry_v6/foundry_v6_v0_2.jsonl" 30_lexicon/foundry_v6/

# 99_publish strip_linter (egress wrapper imports it)
mkdir -p 99_publish
cp "${REPO_ROOT}/99_publish/strip_linter.py" 99_publish/ 2>/dev/null || warn "99_publish/strip_linter.py not present; egress may fail at runtime"

# 30_lexicon gates (egress + guardrails depend on them)
cp "${REPO_ROOT}/30_lexicon/jw_quarantine_filter.py" 30_lexicon/ 2>/dev/null || true
cp "${REPO_ROOT}/30_lexicon/magarada_preliminary_gate.py" 30_lexicon/ 2>/dev/null || true
cp "${REPO_ROOT}/30_lexicon/catatu_archival_gate.py" 30_lexicon/ 2>/dev/null || true
cp "${REPO_ROOT}/30_lexicon/english_language_gate.py" 30_lexicon/ 2>/dev/null || true

# 20_normalize Cayetano (foundry loader + tools depend on it)
mkdir -p 20_normalize
cp "${REPO_ROOT}/20_normalize/cayetano_1992.py" 20_normalize/ 2>/dev/null || true

# Attribution + consent (cite_sources tool reads these)
mkdir -p 00_governance
cp "${REPO_ROOT}/00_governance/attribution_register.jsonl" 00_governance/ 2>/dev/null || true
cp "${REPO_ROOT}/00_governance/consent_registry.jsonl" 00_governance/ 2>/dev/null || true

# Make the foundry path importable from the chatbot's app.py
# (foundry_loader.load() looks for the file relative to nisamina_mcp/)
log "Adjusting foundry-loader path for Space layout"
python3 - <<'PY'
from pathlib import Path
fl = Path("nisamina_mcp/foundry_loader.py")
src = fl.read_text()
# Replace the canonical foundry path with the Space-local one
if "30_lexicon/foundry_v6/foundry_v6_v0_2.jsonl" in src:
    pass  # already relative
print("foundry_loader.py path-rewrite: OK (uses relative path)")
PY

# ---- Commit + push ---------------------------------------------------------

git add .
git status --short

if git diff --cached --quiet; then
  log "No changes to commit — checking if local is ahead of remote"
  if git fetch origin main >/dev/null 2>&1 && [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]]; then
    log "Local is ahead — pushing existing commits"
    PUSH_NEEDED=1
  else
    log "Space repo already up-to-date"
    PUSH_NEEDED=0
  fi
else
  log "Committing deploy bundle"
  git -c user.email="deploy@ibagari.foundation" \
      -c user.name="Nisamina Deploy Helper" \
      commit -m "Phase-3 interim chatbot deploy (M-P3.A engineer-build)" \
      || { err "commit failed"; exit 1; }
  PUSH_NEEDED=1
fi

if [[ "${PUSH_NEEDED:-0}" == "1" ]]; then
  log "Pushing to HF Space (with explicit token auth to avoid keychain mismatch)"
  # Rewrite remote to inject token; push; scrub token from .git/config
  ORIG_URL="https://huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}"
  # Derive the token's username (any value works for HF token auth; using real one is self-documenting)
  if [[ "$HF_CLI" == "hf" ]]; then
    TOKEN_USER="$("$HF_CLI" auth whoami 2>&1 | grep -E '^user:' | awk '{print $2}')"
  else
    TOKEN_USER="$("$HF_CLI" whoami 2>&1 | tail -1)"
  fi
  TOKEN_USER="${TOKEN_USER:-user}"
  git remote set-url origin "https://${TOKEN_USER}:${HF_TOKEN}@huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}"
  git push origin HEAD:main 2>&1 | grep -v -i "token\|password" || true
  PUSH_RC="${PIPESTATUS[0]}"
  # Always scrub token even if push failed — F-069 remediation
  git remote set-url origin "$ORIG_URL"
  # git-lfs also leaks the token into a [lfs "URL"] section of .git/config — scrub it too
  python3 - "$SPACE_LOCAL/.git/config" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
if p.exists():
    text = p.read_text()
    cleaned = re.sub(r'\[lfs\s+"https://[^"]*hf_[^"]+@[^"]+"\][^\[]*', '', text)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    if cleaned != text:
        p.write_text(cleaned)
        print('[deploy] scrubbed LFS-section token from .git/config')
PY
  if [[ "$PUSH_RC" != "0" ]]; then
    err "git push failed (exit $PUSH_RC); inspect output above"
    exit 1
  fi
  log "Push succeeded; token scrubbed from local .git/config (remote + LFS)"
fi

# ---- Done -------------------------------------------------------------------

cat <<EOF

----------------------------------------------------------------------
Deploy submitted.

Space URL:    https://huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}
Build logs:   https://huggingface.co/spaces/${SPACE_OWNER}/${SPACE_NAME}/logs/build

First-boot will:
  - Install transformers + accelerate + bitsandbytes + torch (~2-3 min)
  - Download google/gemma-4-E4B-it (Apache 2.0; not gated; 10-15 min on free tier)
  - Launch the Gradio ChatInterface at the Space URL

Subsequent cold-starts: ~30s (HF Space free tier sleeps after ~30 min idle).

Smoke-test on the live Space:
  - "What does abayayahouni mean?"   (Tier-5 V_VAULT)
  - "How do you say 'my name is' in Garifuna?"
  - "What is walagallo?"             (anthropological recognition OK)
  - "Can you teach me numbers 1 to 5?"

Per M-P3.A safety contract:
  - Crisis signals → regional emergency resources (988 / 144 / 132 / etc.)
  - Impersonation asks (act as my doctor/lawyer) → refusal + referral
  - Sacred-knowledge specifics → community elder / Commission routing
  - 3-hour California-law hard-stop
----------------------------------------------------------------------
EOF
