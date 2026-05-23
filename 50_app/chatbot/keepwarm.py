#!/usr/bin/env python3
"""M-P3.A.KEEPWARM — HF Space keep-warm pinger.

Per F-064 PART A + F-074 PN-8. HF Space free-tier sleeps after 48 hours of
inactivity. This script hits the Space URL to reset the sleep timer. Run
every ~36 hours via cron / launchd / GitHub Actions schedule.

Free; no gate. No paid service required.

Usage:
    # One-shot ping (exit non-zero if Space unreachable):
    python3 50_app/chatbot/keepwarm.py

    # macOS launchd / Linux cron — every 36 hours:
    #   0 0 */36 * * /Volumes/AI External/Nisamina_ai_Claude/nisamina-app/50_app/chatbot/keepwarm.py

    # GitHub Actions (recommended when GitHub repo exists; see PN-17):
    #   on: schedule: - cron: '0 */36 * * *'   # every 36h
    #   jobs: keepwarm: ... python keepwarm.py
"""
from __future__ import annotations

import os
import sys
import time
import urllib.error
import urllib.request


SPACE_OWNER = os.environ.get("HF_SPACE_OWNER", "ibagari")
SPACE_NAME = os.environ.get("HF_SPACE_NAME", "nisamina-chatbot-phase3-interim")

SPACE_URL = f"https://huggingface.co/spaces/{SPACE_OWNER}/{SPACE_NAME}"
RUNTIME_API = f"https://huggingface.co/api/spaces/{SPACE_OWNER}/{SPACE_NAME}/runtime"

TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 10


def fetch_url(url: str, timeout: int = TIMEOUT_SECONDS) -> tuple[int, str]:
    """GET a URL; return (status_code, body_excerpt)."""
    req = urllib.request.Request(url, headers={"User-Agent": "nisamina-keepwarm/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2048).decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as e:
        return -1, repr(e)


def main() -> int:
    print(f"[keepwarm] Target Space: {SPACE_URL}", flush=True)

    for attempt in range(1, MAX_RETRIES + 1):
        # First, check runtime state via the API
        status_code, body = fetch_url(RUNTIME_API)
        if status_code == 200:
            stage = "?"
            if '"stage"' in body:
                # very light parse — avoid json dep edge cases
                idx = body.find('"stage"')
                rest = body[idx:idx + 80]
                if ":" in rest:
                    stage = rest.split(":", 1)[1].strip().split(",")[0].strip().strip('"')
            print(f"[keepwarm] runtime stage = {stage}", flush=True)
            if stage in ("RUNNING", "SLEEPING", "APP_STARTING", "BUILDING"):
                # Either active (RUNNING) or warming up — call the public URL to keep warm
                resp_code, _ = fetch_url(SPACE_URL)
                print(f"[keepwarm] Space-URL probe returned {resp_code}", flush=True)
                if resp_code in (200, 302, 303):
                    print("[keepwarm] OK — sleep timer reset", flush=True)
                    return 0
            elif stage == "RUNTIME_ERROR":
                print("[keepwarm] WARNING — Space in RUNTIME_ERROR; keep-warm still pings but engineer should redeploy", flush=True)
                fetch_url(SPACE_URL)
                return 2  # non-zero so cron monitoring alerts
        else:
            print(f"[keepwarm] runtime API returned {status_code}; attempt {attempt}/{MAX_RETRIES}", flush=True)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    print("[keepwarm] FAILED after retries", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
