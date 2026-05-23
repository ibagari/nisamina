"""Tests for the server entrypoint (no `mcp` SDK required for these)."""
from __future__ import annotations
import importlib
import subprocess
import sys
from pathlib import Path

import pytest


def test_server_module_imports_without_mcp():
    """The package itself (loaders, tools, egress) must import even when the
    mcp SDK isn't installed."""
    mod = importlib.import_module("nisamina_mcp.server")
    assert hasattr(mod, "main")
    assert hasattr(mod, "build_server")
    assert callable(mod.main)


def test_build_server_raises_clear_error_without_mcp():
    """If mcp is missing, build_server() must raise SystemExit with install hint."""
    try:
        import mcp  # noqa: F401
        pytest.skip("mcp SDK is installed in this env; can't test missing-mcp path")
    except ImportError:
        pass
    from nisamina_mcp.server import build_server
    with pytest.raises(SystemExit) as ei:
        build_server()
    msg = str(ei.value).lower()
    assert "mcp" in msg
    assert "pip install" in msg


def test_entrypoint_version_flag_works():
    """`server.py --version` should exit 0 + print version without mcp installed."""
    entry = Path(__file__).resolve().parent.parent / "server.py"
    assert entry.exists()
    res = subprocess.run(
        [sys.executable, str(entry), "--version"],
        capture_output=True, text=True, timeout=30,
    )
    assert res.returncode == 0, f"stderr: {res.stderr}"
    assert "nisamina-mcp" in res.stdout
