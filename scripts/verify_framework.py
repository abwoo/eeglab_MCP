"""Verify the EEGLAB MCP product framework without EEG test data."""

from __future__ import annotations

import asyncio
import ast
import json
import tomllib
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _parse_python() -> None:
    paths = [
        ROOT / "eeglab_mcp_server" / "server.py",
        ROOT / "eeglab_mcp_server" / "schemas.py",
        ROOT / "eeglab_mcp_server" / "workflows.py",
        ROOT / "eeglab_mcp_server" / "backend.py",
        ROOT / "eeglab_mcp_server" / "matlab_literals.py",
    ]
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"))


def _check_configs_and_skill() -> None:
    configs = ROOT / "configs"
    tomllib.loads((configs / "codex.config.toml").read_text(encoding="utf-8"))
    for name in ("claude_desktop_config.json", "cursor.mcp.json", "vscode.mcp.json", "openclaw.mcp.json"):
        payload = json.loads((configs / name).read_text(encoding="utf-8"))
        servers = payload.get("mcpServers") or payload.get("servers") or {}
        _require("eeglab" in servers, f"{name} missing eeglab server")

    skill = ROOT / "skills" / "eeglab-analysis"
    for rel in ("SKILL.md", "references/workflows.md", "references/tools.md", "references/setup.md"):
        path = skill / rel
        _require(path.exists(), f"missing skill file: {rel}")
        text = path.read_text(encoding="utf-8")
        _require("eeglab" in text.lower(), f"skill file missing eeglab term: {rel}")


def _first_text(result: Any) -> dict[str, Any]:
    _require(bool(result.content), "tool returned no content")
    return json.loads(result.content[0].text)


async def _check_mcp() -> None:
    params = StdioServerParameters(command="python", args=["-B", "eeglab_mcp_server/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            _require(len(tool_names) == 40, f"expected 40 tools, got {len(tool_names)}")
            _require("eeglab_workflow_recommend" in tool_names, "missing workflow recommendation tool")

            prompts = await session.list_prompts()
            prompt_names = [prompt.name for prompt in prompts.prompts]
            for name in (
                "eeglab_project_intake",
                "eeglab_strict_qc_protocol",
                "eeglab_dual_mcp_routing",
                "eeglab_report_template",
            ):
                _require(name in prompt_names, f"missing prompt: {name}")

            resources = await session.list_resources()
            resource_uris = [str(resource.uri) for resource in resources.resources]
            for uri in (
                "eeglab://skill/SKILL.md",
                "eeglab://references/workflows.md",
                "eeglab://references/tools.md",
                "eeglab://references/setup.md",
            ):
                _require(uri in resource_uris, f"missing resource: {uri}")
                resource = await session.read_resource(uri)
                _require(bool(resource.contents), f"resource returned no contents: {uri}")

            recommendation = _first_text(await session.call_tool("eeglab_workflow_recommend", {}))
            _require(recommendation.get("status") == "success", "workflow recommendation failed")


def _check_cleanliness() -> None:
    forbidden_names = {"test_eeg.set", "test_eeg.fdt", "reports"}
    for path in ROOT.rglob("*"):
        _require(path.name not in forbidden_names, f"forbidden test artifact present: {path}")
        _require(path.name != "__pycache__", f"python cache present: {path}")
        _require(path.suffix != ".pyc", f"pyc cache present: {path}")


def main() -> None:
    _parse_python()
    _check_configs_and_skill()
    asyncio.run(_check_mcp())
    _check_cleanliness()
    print("framework_ok=True")
    print("tool_count=40")
    print("prompt_count=4")
    print("resource_count=4")


if __name__ == "__main__":
    main()
