"""Shared runtime helpers for EEGLAB MCP handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

try:
    from .backend import DEBUG_ERRORS as DEBUG_ERRORS
    from .backend import cfg as cfg
    from .backend import matlab as matlab
    from .matlab_literals import (
        _arr,
        _cell,
        _esc,
        _matlab_text,
        matlab_cell,
        matlab_field_name,
        matlab_numeric_array,
        matlab_string,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from backend import DEBUG_ERRORS as DEBUG_ERRORS
    from backend import cfg as cfg
    from backend import matlab as matlab
    from matlab_literals import (
        _arr,
        _cell,
        _esc,
        _matlab_text,
        matlab_cell,
        matlab_field_name,
        matlab_numeric_array,
        matlab_string,
    )

_matlab_identifier = matlab_field_name

__all__ = [
    "DEBUG_ERRORS",
    "_arr",
    "_cell",
    "_eeglab_init_code",
    "_error_response",
    "_esc",
    "_json_response",
    "_matlab_identifier",
    "_matlab_text",
    "_maybe_init",
    "cfg",
    "matlab",
    "matlab_cell",
    "matlab_numeric_array",
    "matlab_string",
]


def _eeglab_init_code() -> str:
    """Build the EEGLAB initialization code (initialization happens only on the first call)."""
    code = ""
    if cfg.EEGLAB_PATH:
        code += f"addpath(genpath({matlab_string(cfg.EEGLAB_PATH)})); "
    code += "eeglab nogui; "
    return code


def _maybe_init() -> str:
    """Return the initialization code when EEGLAB has not been initialized yet."""
    if matlab._mode == "cli":
        return _eeglab_init_code()
    if matlab.eeglab_initialized:
        return ""
    return _eeglab_init_code()


def _json_response(payload: dict[str, Any]) -> list[TextContent]:
    """Return MCP text content, always JSON."""
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _error_response(
    code: str,
    message: str,
    *,
    next_step: str = "",
    details: dict[str, Any] | None = None,
) -> list[TextContent]:
    """Build a uniform tool error response."""
    payload: dict[str, Any] = {
        "status": "error",
        "code": code,
        "error": message,
    }
    if next_step:
        payload["next_step"] = next_step
    if details:
        payload["details"] = details
    return _json_response(payload)
