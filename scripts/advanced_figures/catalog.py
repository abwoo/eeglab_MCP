"""Shared helpers for the default advanced EEG figure galleries.

These galleries mirror the official figure atlas, stay default-visible,
and do not replace the canonical MCP tools.
"""

from __future__ import annotations

from typing import Any


def _escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|")


def render_module_doc(module: dict[str, Any], figure_families: list[dict[str, Any]]) -> str:
    """Render one advanced-figure module as Markdown."""
    lines = [
        f"# {module['title']}",
        "",
        module["summary"],
        "",
        "## Default Status",
        "",
        "- Default enabled: yes",
        f"- Python module: `{module['python_module']}`",
        f"- Markdown guide: `{module['markdown_path']}`",
        f"- Default MCP route: `{module['mcp_route']}`",
        "",
        "## Figure Families",
        "",
        "| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for item in figure_families:
        lines.append(
            "| "
            f"{_escape(item['figure_family'])} | "
            f"{_escape(item['status'])} | "
            f"{_escape(item['official_anchor'])} | "
            f"{_escape(item['official_url'])} | "
            f"`{_escape(item['mcp_tool'])}` | "
            f"{_escape(item['official_scope'])} |"
        )

    lines.extend(
        [
            "",
            "## Default Use",
            "",
            "Use this gallery as the default browsable companion to the official figure atlas. Keep the canonical MCP tools as the execution path.",
        ]
    )
    return "\n".join(lines)


def render_index_doc(modules: list[dict[str, Any]]) -> str:
    """Render the gallery index."""
    lines = [
        "# Advanced Figure Gallery",
        "",
        "This default gallery gives the figure families a browsable home outside the MCP execution path. Use it as the normal visual reference, but keep the MCP tools as the execution path.",
        "",
        "| Module | Python file | Markdown guide | Primary branch |",
        "| --- | --- | --- | --- |",
    ]

    for module in modules:
        lines.append(
            "| "
            f"{_escape(module['title'])} | "
            f"`{_escape(module['python_module'])}` | "
            f"`{_escape(module['markdown_path'])}` | "
            f"{_escape(module['branch'])} |"
        )

    lines.extend(
        [
            "",
            "## Default Companion",
            "",
            "Use the module that matches the branch you are about to execute. Each module mirrors the official figure atlas and stays default-visible.",
        ]
    )
    return "\n".join(lines)
