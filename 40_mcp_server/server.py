#!/usr/bin/env python3
"""Entrypoint script for `claude mcp add nisamina ./nisamina-app/40_mcp_server/server.py`.

Thin wrapper: ensures the local `nisamina_mcp/` package is on sys.path (for
dev-from-source use) and hands off to `nisamina_mcp.server.main()`. When the
package is pip-installed, the `nisamina-mcp` console script also calls
`nisamina_mcp.server:main` (see pyproject.toml).
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from nisamina_mcp.server import main  # noqa: E402

if __name__ == "__main__":
    main()
