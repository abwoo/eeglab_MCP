"""Helpers for generating safe MATLAB literals and result fields."""

from __future__ import annotations

import math
import re
from typing import Any


def _matlab_text(value: Any) -> str:
    """Return text safe to place inside an already-quoted MATLAB char literal."""
    text = "" if value is None else str(value)
    return (
        text.replace("\\", "/")
        .replace("'", "''")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def matlab_string(value: Any) -> str:
    """Return a single-quoted MATLAB char literal for arbitrary user input."""
    return f"'{_matlab_text(value)}'"


def matlab_cell(items: list[Any]) -> str:
    """Return a MATLAB cell array whose string elements are safely quoted."""
    return "{" + ", ".join(matlab_string(item) for item in items) + "}"


def matlab_numeric_array(items: list[Any]) -> str:
    """Return a MATLAB numeric row vector, rejecting non-numeric values."""
    values: list[str] = []
    for item in items:
        if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(float(item)):
            raise ValueError(f"MATLAB numeric arrays only accept finite numbers, got {item!r}")
        values.append(str(item))
    return "[" + " ".join(values) + "]"


def matlab_field_name(value: Any, *, fallback: str = "field") -> str:
    """Return a conservative MATLAB struct field name for dynamic result keys."""
    text = "" if value is None else str(value)
    field = re.sub(r"\W", "_", text, flags=re.ASCII)
    field = re.sub(r"_+", "_", field).strip("_")
    if not field:
        field = fallback
    if field[0].isdigit():
        field = f"{fallback}_{field}"
    return field[:63]


def matlab_make_valid_name_expr(var_name: str) -> str:
    """Return MATLAB expression that sanitizes a variable into a struct field name."""
    return f"matlab.lang.makeValidName(char({var_name}))"


def _esc(value: Any) -> str:
    """Compatibility helper for legacy code that still wraps values in quotes."""
    return _matlab_text(value)


def _cell(items: list[Any]) -> str:
    """Compatibility wrapper for MATLAB cell literals."""
    return matlab_cell(items)


def _arr(items: list[Any]) -> str:
    """Compatibility wrapper for MATLAB numeric row-vector literals."""
    return matlab_numeric_array(items)
