"""Verify the EEGLAB MCP product framework without EEG test data."""

from __future__ import annotations

import asyncio
import ast
import json
import shutil
import tomllib
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]

LEGACY_TOOL_NAMES = {
    "eeglab_init",
    "eeglab_load_data",
    "eeglab_save_data",
    "eeglab_import_bids",
    "eeglab_info",
    "eeglab_history",
    "eeglab_filter",
    "eeglab_resample",
    "eeglab_reref",
    "eeglab_select_channels",
    "eeglab_interpolate_channels",
    "eeglab_edit_channels",
    "eeglab_clean_line_noise",
    "eeglab_clean_rawdata",
    "eeglab_run_ica",
    "eeglab_classify_ica",
    "eeglab_flag_components",
    "eeglab_remove_components",
    "eeglab_reject_epochs",
    "eeglab_get_events",
    "eeglab_epoch",
    "eeglab_erp_analysis",
    "eeglab_sort_epochs",
    "eeglab_average_erp",
    "eeglab_spectral",
    "eeglab_timefreq",
    "eeglab_connectivity",
    "eeglab_topoplot",
    "eeglab_plot_erp",
    "eeglab_plot_timefreq",
    "eeglab_plot_components",
    "eeglab_source_localization",
    "eeglab_source_settings",
    "eeglab_study_create",
    "eeglab_study_design",
    "eeglab_study_statistics",
    "eeglab_pipeline",
    "eeglab_qc_report",
    "eeglab_erp_light_workflow",
    "eeglab_workflow_recommend",
}

RESEARCH_TOOL_NAMES = {
    "eeglab_project_plan",
    "eeglab_protocol_export",
    "eeglab_plugin_check",
    "eeglab_event_semantics_audit",
}

REQUIRED_PROMPTS = {
    "eeglab_project_intake",
    "eeglab_strict_qc_protocol",
    "eeglab_dual_mcp_routing",
    "eeglab_report_template",
    "eeglab_erp_research_entry",
    "eeglab_resting_research_entry",
    "eeglab_time_frequency_entry",
    "eeglab_ica_cleanup_entry",
    "eeglab_bids_study_entry",
    "eeglab_source_connectivity_entry",
}

REQUIRED_RESOURCES = {
    "eeglab://skill/SKILL.md",
    "eeglab://references/workflows.md",
    "eeglab://references/tools.md",
    "eeglab://references/setup.md",
    "eeglab://official/references.md",
}

RESEARCH_TERMS = {
    "pop_",
    "clean_rawdata",
    "ICLabel",
    "DIPFIT",
    "BIDS",
    "STUDY",
    "LIMO",
    "provenance",
    "event semantics",
    "QC gates",
}


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

    docs = ROOT / "docs"
    for rel in ("research-standard.md", "user-workflows.md"):
        path = docs / rel
        _require(path.exists(), f"missing docs file: {rel}")

    combined = "\n".join(
        [
            (skill / "SKILL.md").read_text(encoding="utf-8"),
            (skill / "references" / "workflows.md").read_text(encoding="utf-8"),
            (skill / "references" / "tools.md").read_text(encoding="utf-8"),
            (docs / "research-standard.md").read_text(encoding="utf-8"),
        ]
    )
    for term in RESEARCH_TERMS:
        _require(term.lower() in combined.lower(), f"missing research-standard term: {term}")


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
            tool_set = set(tool_names)
            missing_legacy = sorted(LEGACY_TOOL_NAMES - tool_set)
            _require(not missing_legacy, f"missing legacy tools: {missing_legacy}")
            missing_research = sorted(RESEARCH_TOOL_NAMES - tool_set)
            _require(not missing_research, f"missing research tools: {missing_research}")
            _require(len(tool_names) >= len(LEGACY_TOOL_NAMES) + len(RESEARCH_TOOL_NAMES), f"unexpected tool count: {len(tool_names)}")

            prompts = await session.list_prompts()
            prompt_names = [prompt.name for prompt in prompts.prompts]
            for name in REQUIRED_PROMPTS:
                _require(name in prompt_names, f"missing prompt: {name}")

            resources = await session.list_resources()
            resource_uris = [str(resource.uri) for resource in resources.resources]
            for uri in REQUIRED_RESOURCES:
                _require(uri in resource_uris, f"missing resource: {uri}")
                resource = await session.read_resource(uri)
                _require(bool(resource.contents), f"resource returned no contents: {uri}")

            recommendation = _first_text(await session.call_tool("eeglab_workflow_recommend", {}))
            _require(recommendation.get("status") == "success", "workflow recommendation failed")
            _require("not_recommended" in recommendation.get("summary", {}), "workflow recommendation missing not_recommended")

            plan = _first_text(
                await session.call_tool(
                    "eeglab_project_plan",
                    {"analysis_type": "auto", "event_types": ["s1000"], "has_channel_locations": False},
                )
            )
            _require(plan.get("status") == "success", "project plan failed")
            _require("blocking_conditions" in plan.get("summary", {}), "project plan missing blocking conditions")

            audit = _first_text(
                await session.call_tool(
                    "eeglab_event_semantics_audit",
                    {
                        "event_types": ["s1000", "Impedance"],
                        "event_counts": {"s1000": 18, "Impedance": 2},
                        "segment_markers": ["s1000"],
                        "exclude_markers": ["Impedance"],
                    },
                )
            )
            _require(audit.get("status") == "success", "event semantics audit failed")
            _require(audit.get("summary", {}).get("confirmed_analysis_events") == [], "segment/impedance markers must not become analysis events")

            protocol = _first_text(
                await session.call_tool(
                    "eeglab_protocol_export",
                    {"format": "markdown", "research_goal": "framework verification", "steps": ["quick_qc"]},
                )
            )
            _require(protocol.get("status") == "success", "protocol export failed")
            _require("protocol_text" in protocol.get("outputs", {}), "protocol export missing text")


def _check_cleanliness() -> None:
    for cache_dir in ROOT.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
    for pyc in ROOT.rglob("*.pyc"):
        pyc.unlink()

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
    print(f"legacy_tool_count={len(LEGACY_TOOL_NAMES)}")
    print(f"research_tool_count={len(RESEARCH_TOOL_NAMES)}")
    print(f"prompt_count={len(REQUIRED_PROMPTS)}")
    print(f"resource_count={len(REQUIRED_RESOURCES)}")


if __name__ == "__main__":
    main()
