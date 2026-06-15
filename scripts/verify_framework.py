"""Verify the EEGLAB MCP product framework without EEG test data."""

from __future__ import annotations

import asyncio
import ast
import json
import shutil
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eeglab_mcp_server.handler_registry import TOOL_HANDLERS  # noqa: E402
from eeglab_mcp_server.mcp_surfaces import RESOURCE_FILES  # noqa: E402
from eeglab_mcp_server.official_alignment import (  # noqa: E402
    METHOD_PROFILES,
    OFFICIAL_CLAIMS,
)
from eeglab_mcp_server.tool_registry import (  # noqa: E402
    EXPOSED_TOOL_NAMES,
    LEGACY_LOW_LEVEL_TOOL_NAMES,
    RESEARCH_WORKFLOW_TOOL_NAMES,
    TOTAL_EXPOSED_TOOL_COUNT,
    TOOL_REGISTRY,
    registry_summary,
    validate_handler_map,
    validate_registry,
)

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
    "eeglab://references/official-method-map.md",
    "eeglab://references/gate-policy.md",
    "eeglab://references/method-gates.md",
    "eeglab://references/acquisition-to-derivatives.md",
    "eeglab://references/event-semantics.md",
    "eeglab://references/preprocessing-decision-tree.md",
    "eeglab://references/ica-iclabel-policy.md",
    "eeglab://references/bids-study-policy.md",
    "eeglab://references/source-policy.md",
    "eeglab://references/report-protocol-templates.md",
    "eeglab://references/statistics-reporting.md",
    "eeglab://official/references.md",
    "eeglab://official/topic-index.md",
    "eeglab://official/support-matrix.md",
    "eeglab://official/tool-support-matrix.md",
    "eeglab://official/method-map.md",
    "eeglab://official/gate-policy.md",
    "eeglab://official/plugin-map.md",
    "eeglab://official/plugin-matrix.md",
    "eeglab://official/risk-matrix.md",
    "eeglab://official/report-field-matrix.md",
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
    "override",
    "source_claim_ids",
    "support_level",
    "indexed_only",
    "report field matrix",
    "tool support matrix",
    "HEDTools",
    "import_plugins",
    "data_export",
    "history_scripting",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _parse_python() -> None:
    paths = [
        ROOT / "eeglab_mcp_server" / "server.py",
        ROOT / "eeglab_mcp_server" / "schemas.py",
        ROOT / "eeglab_mcp_server" / "workflows.py",
        ROOT / "eeglab_mcp_server" / "official_alignment.py",
        ROOT / "eeglab_mcp_server" / "tool_registry.py",
        ROOT / "eeglab_mcp_server" / "backend.py",
        ROOT / "eeglab_mcp_server" / "matlab_literals.py",
    ]
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"))


def _check_configs_and_skill() -> None:
    configs = ROOT / "configs"
    tomllib.loads((configs / "codex.config.toml").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((ROOT / "eeglab_mcp_server" / "pyproject.toml").read_text(encoding="utf-8"))
    for section in ("black", "ruff", "mypy"):
        _require(
            section in pyproject.get("tool", {}),
            f"pyproject missing tool.{section} configuration",
        )
    dev_deps = pyproject.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    for dep in ("black", "ruff", "mypy"):
        _require(
            any(str(item).startswith(dep) for item in dev_deps),
            f"pyproject missing dev dependency {dep}",
        )
    for name in (
        "claude_desktop_config.json",
        "cursor.mcp.json",
        "vscode.mcp.json",
        "openclaw.mcp.json",
    ):
        payload = json.loads((configs / name).read_text(encoding="utf-8"))
        servers = payload.get("mcpServers") or payload.get("servers") or {}
        _require("eeglab" in servers, f"{name} missing eeglab server")

    skill = ROOT / "skills" / "eeglab-analysis"
    for rel in (
        "SKILL.md",
        "references/workflows.md",
        "references/tools.md",
        "references/setup.md",
        "references/official-gates.md",
        "references/official-method-map.md",
        "references/gate-policy.md",
        "references/method-gates.md",
        "references/acquisition-to-derivatives.md",
        "references/event-semantics.md",
        "references/preprocessing-decision-tree.md",
        "references/ica-iclabel-policy.md",
        "references/bids-study-policy.md",
        "references/source-policy.md",
        "references/report-protocol-templates.md",
        "references/statistics-reporting.md",
    ):
        path = skill / rel
        _require(path.exists(), f"missing skill file: {rel}")
        text = path.read_text(encoding="utf-8")
        _require("eeglab" in text.lower(), f"skill file missing eeglab term: {rel}")

    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    skill_body = skill_text.split("---", 2)[-1]
    for tag in ("objective", "quick_start", "workflow", "official_gate_routing", "success_criteria"):
        _require(
            f"<{tag}>" in skill_body and f"</{tag}>" in skill_body,
            f"SKILL.md missing XML tag: {tag}",
        )
    heading_lines = [
        index
        for index, line in enumerate(skill_body.splitlines(), start=1)
        if line.startswith("#")
    ]
    _require(not heading_lines, f"SKILL.md body must use XML tags, found markdown headings at lines {heading_lines}")

    docs = ROOT / "docs"
    for rel in (
        "research-standard.md",
        "user-workflows.md",
        "official-topic-index.md",
        "official-support-matrix.md",
        "official-tool-support-matrix.md",
        "official-method-map.md",
        "official-gate-policy.md",
        "official-plugin-map.md",
        "official-risk-matrix.md",
        "official-report-field-matrix.md",
    ):
        path = docs / rel
        _require(path.exists(), f"missing docs file: {rel}")

    combined = "\n".join(
        [
            (skill / "SKILL.md").read_text(encoding="utf-8"),
            (skill / "references" / "workflows.md").read_text(encoding="utf-8"),
            (skill / "references" / "tools.md").read_text(encoding="utf-8"),
            (skill / "references" / "official-method-map.md").read_text(encoding="utf-8"),
            (skill / "references" / "gate-policy.md").read_text(encoding="utf-8"),
            (skill / "references" / "method-gates.md").read_text(encoding="utf-8"),
            (skill / "references" / "acquisition-to-derivatives.md").read_text(encoding="utf-8"),
            (skill / "references" / "event-semantics.md").read_text(encoding="utf-8"),
            (skill / "references" / "ica-iclabel-policy.md").read_text(encoding="utf-8"),
            (skill / "references" / "bids-study-policy.md").read_text(encoding="utf-8"),
            (skill / "references" / "source-policy.md").read_text(encoding="utf-8"),
            (skill / "references" / "statistics-reporting.md").read_text(encoding="utf-8"),
            (docs / "research-standard.md").read_text(encoding="utf-8"),
            (docs / "official-tool-support-matrix.md").read_text(encoding="utf-8"),
        ]
    )
    for term in RESEARCH_TERMS:
        _require(term.lower() in combined.lower(), f"missing research-standard term: {term}")


def _check_registry_documentation_drift() -> None:
    forbidden_tool_count_phrases = (
        "original " + "40",
        "40 " + "stable",
        "旧版 " + "40",
    )
    checked_suffixes = {".md", ".xml", ".ps1", ".py", ".toml", ".json"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in forbidden_tool_count_phrases:
            _require(
                phrase.lower() not in text.lower(),
                f"hard-coded stale tool count phrase in {path}: {phrase}",
            )


def _check_registry_handler_map() -> None:
    errors = validate_handler_map(TOOL_HANDLERS)
    _require(not errors, f"handler registry errors: {errors}")


def _check_static_structure_policy() -> None:
    server_text = (ROOT / "eeglab_mcp_server" / "server.py").read_text(encoding="utf-8")
    forbidden_server_fragments = (
        "class MatlabBackend",
        "class Config:",
        "def matlab_string(",
        "def matlab_cell(",
        "def matlab_numeric_array(",
        "def _matlab_text(",
    )
    for fragment in forbidden_server_fragments:
        _require(
            fragment not in server_text,
            f"server.py must not reimplement backend/literal helper: {fragment}",
        )

    owner_by_definition = {
        "Config": ROOT / "eeglab_mcp_server" / "backend.py",
        "MatlabBackend": ROOT / "eeglab_mcp_server" / "backend.py",
        "matlab_string": ROOT / "eeglab_mcp_server" / "matlab_literals.py",
        "matlab_cell": ROOT / "eeglab_mcp_server" / "matlab_literals.py",
        "matlab_numeric_array": ROOT / "eeglab_mcp_server" / "matlab_literals.py",
        "_matlab_text": ROOT / "eeglab_mcp_server" / "matlab_literals.py",
    }
    for path in (ROOT / "eeglab_mcp_server").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        _require("except:\n" not in text, f"bare except is forbidden: {path}")
        _require(
            "except Exception:\n    pass" not in text,
            f"silent except pass is forbidden: {path}",
        )
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                owner = owner_by_definition.get(node.name)
                _require(
                    owner is None or path == owner,
                    f"{node.name} must be defined only in {owner}: {path}:{node.lineno}",
                )
            if isinstance(node, ast.JoinedStr):
                for value in node.values:
                    if not isinstance(value, ast.FormattedValue):
                        continue
                    expr = ast.unparse(value.value)
                    _require(
                        "args[" not in expr
                        and "args.get(" not in expr
                        and "arguments[" not in expr
                        and "arguments.get(" not in expr,
                        f"direct argument interpolation in MATLAB template is forbidden: {path}:{node.lineno}: {expr}",
                    )


EVAL_STATUS_VALUES = {"pass", "advisory", "blocked", "override_accepted", "unknown_method"}
REPORT_ASSERTION_FIELDS = {
    "requires_protocol_export",
    "requires_gate_results",
    "requires_source_claim_ids",
    "requires_report_fields",
    "requires_report_field_matrix",
    "requires_override_status",
}


def _csv_values(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def _child_texts(node: ET.Element, path: str) -> set[str]:
    return {str(child.text or "").strip() for child in node.findall(path) if str(child.text or "").strip()}


def _eval_resource_uris() -> set[str]:
    eval_path = ROOT / "eeglab_mcp_server" / "evals.xml"
    root = ET.fromstring(eval_path.read_text(encoding="utf-8"))
    return {
        str(resource.attrib.get("uri", "")).strip()
        for resource in root.findall("eval/resource_assertions/resource")
        if str(resource.attrib.get("uri", "")).strip()
    }


def _check_eval_registry_coverage() -> dict[str, int]:
    eval_path = ROOT / "eeglab_mcp_server" / "evals.xml"
    root = ET.fromstring(eval_path.read_text(encoding="utf-8"))
    eval_nodes = root.findall("eval")
    eval_ids = [node.attrib.get("id", "") for node in eval_nodes]
    _require(len(eval_ids) >= 56, f"expected at least 56 evals, found {len(eval_ids)}")
    _require(len(set(eval_ids)) == len(eval_ids), "eval ids must be unique")
    expected_ids = [str(index) for index in range(1, len(eval_nodes) + 1)]
    _require(eval_ids == expected_ids, f"eval ids must be consecutive from 1, found {eval_ids}")
    referenced = {eval_id for spec in TOOL_REGISTRY.values() for eval_id in spec.eval_ids}
    eval_id_set = set(eval_ids)
    unknown_references = sorted(referenced - eval_id_set)
    _require(
        not unknown_references,
        f"registry references unknown eval ids: {unknown_references}",
    )
    uncovered = sorted(eval_id_set - referenced, key=lambda item: int(item) if item.isdigit() else item)
    _require(not uncovered, f"evals missing registry coverage: {uncovered}")

    contract_tools_by_eval: dict[str, set[str]] = {}
    required_tools_by_eval: dict[str, set[str]] = {}
    forbidden_tools_by_eval: dict[str, set[str]] = {}
    gate_profiles: set[str] = set()
    resource_uris: set[str] = set()
    categories: set[str] = set()

    for node in eval_nodes:
        eval_id = str(node.attrib["id"])
        category = str(node.attrib.get("category", "")).strip()
        _require(category, f"eval {eval_id} missing category")
        categories.add(category)
        _require(bool(node.findtext("question", "").strip()), f"eval {eval_id} missing question")
        _require(bool(node.findtext("expected", "").strip()), f"eval {eval_id} missing expected")
        for section in (
            "required_tools",
            "forbidden_tools",
            "required_terms",
            "gate_assertions",
            "resource_assertions",
            "report_assertions",
        ):
            _require(node.find(section) is not None, f"eval {eval_id} missing {section}")

        required_tools = _child_texts(node, "required_tools/tool")
        forbidden_tools = _child_texts(node, "forbidden_tools/tool")
        required_terms = _child_texts(node, "required_terms/term")
        contract_tools = required_tools | forbidden_tools
        required_tools_by_eval[eval_id] = required_tools
        forbidden_tools_by_eval[eval_id] = forbidden_tools
        contract_tools_by_eval[eval_id] = contract_tools

        _require(required_tools, f"eval {eval_id} missing required_tools")
        _require(required_terms, f"eval {eval_id} missing required_terms")
        overlap = sorted(required_tools & forbidden_tools)
        _require(not overlap, f"eval {eval_id} has tools both required and forbidden: {overlap}")
        for tool_name in sorted(contract_tools):
            _require(tool_name in TOOL_REGISTRY, f"eval {eval_id} references unknown tool: {tool_name}")

        for gate in node.findall("gate_assertions/gate"):
            method = str(gate.attrib.get("method", "")).strip()
            _require(method in METHOD_PROFILES, f"eval {eval_id} references unknown method profile: {method}")
            gate_profiles.add(method)
            expected_status = str(gate.attrib.get("expected_status", "")).strip()
            _require(
                expected_status in EVAL_STATUS_VALUES,
                f"eval {eval_id} has invalid expected_status: {expected_status}",
            )
            profile = METHOD_PROFILES[method]
            profile_requirements = {requirement["id"] for requirement in profile.get("requirements", [])}
            missing_requirements = _csv_values(gate.attrib.get("missing_requirements"))
            unknown_missing = sorted(missing_requirements - profile_requirements)
            _require(
                not unknown_missing,
                f"eval {eval_id} gate {method} references unknown requirements: {unknown_missing}",
            )
            claim_ids = _csv_values(gate.attrib.get("claim_ids"))
            _require(claim_ids, f"eval {eval_id} gate {method} missing claim_ids")
            unknown_claims = sorted(claim_ids - set(OFFICIAL_CLAIMS))
            _require(not unknown_claims, f"eval {eval_id} gate {method} references unknown claims: {unknown_claims}")
            profile_claims = set(profile.get("source_claim_ids", []))
            wrong_profile_claims = sorted(claim_ids - profile_claims)
            _require(
                not wrong_profile_claims,
                f"eval {eval_id} gate {method} claims not in profile: {wrong_profile_claims}",
            )

        for resource in node.findall("resource_assertions/resource"):
            uri = str(resource.attrib.get("uri", "")).strip()
            _require(uri in REQUIRED_RESOURCES, f"eval {eval_id} references non-required resource: {uri}")
            _require(uri in RESOURCE_FILES, f"eval {eval_id} references unknown resource: {uri}")
            resource_uris.add(uri)

        for report in node.findall("report_assertions/report"):
            unknown_fields = sorted(set(report.attrib) - REPORT_ASSERTION_FIELDS)
            _require(not unknown_fields, f"eval {eval_id} has unknown report assertion fields: {unknown_fields}")
            _require(
                report.attrib.get("requires_protocol_export") == "true",
                f"eval {eval_id} report assertion must require protocol export",
            )
            _require(
                "eeglab_protocol_export" in required_tools,
                f"eval {eval_id} report assertion missing eeglab_protocol_export required tool",
            )
            for term in ("gate_results", "source_claim_ids", "report_fields", "report field matrix"):
                _require(term in required_terms, f"eval {eval_id} report assertion missing required term: {term}")

    for tool_name, spec in TOOL_REGISTRY.items():
        for eval_id in spec.eval_ids:
            _require(
                tool_name in contract_tools_by_eval[eval_id],
                f"registry eval coverage missing from eval contract: {tool_name} eval {eval_id}",
            )

    missing_research_tool_contracts = sorted(
        tool_name
        for tool_name in RESEARCH_WORKFLOW_TOOL_NAMES
        if not any(tool_name in tools for tools in required_tools_by_eval.values())
    )
    _require(
        not missing_research_tool_contracts,
        f"research workflow tools missing required_tools eval contract: {missing_research_tool_contracts}",
    )

    high_risk_profiles = {
        spec.method_profile for spec in TOOL_REGISTRY.values() if spec.risk_level == "high" and spec.method_profile
    }
    missing_high_risk_profiles = sorted(high_risk_profiles - gate_profiles)
    _require(
        not missing_high_risk_profiles,
        f"high-risk method profiles missing gate_assertions coverage: {missing_high_risk_profiles}",
    )
    missing_method_profiles = sorted(set(METHOD_PROFILES) - gate_profiles)
    _require(
        not missing_method_profiles,
        f"method profiles missing gate_assertions coverage: {missing_method_profiles}",
    )

    _require(
        "eeglab_method_preflight" in required_tools_by_eval["18"],
        "boundary-only ERP eval must require eeglab_method_preflight",
    )
    _require("eeglab_epoch" in forbidden_tools_by_eval["18"], "boundary-only ERP eval must forbid eeglab_epoch")
    _require("eeglab_clean_rawdata" in forbidden_tools_by_eval["19"], "ASR epoched-only eval must forbid execution")
    eval20 = root.find("eval[@id='20']")
    _require(eval20 is not None, "source override eval missing")
    _require(
        {"override_used", "override_reason", "blocked_requirements_acknowledged"}.issubset(
            _child_texts(eval20, "required_terms/term")
        ),
        "source override eval must require override reporting terms",
    )
    _require(
        "eeglab_study_statistics" in forbidden_tools_by_eval["21"],
        "BIDS/STUDY blocked eval must forbid direct group statistics",
    )
    for eval_id in (
        "25",
        "36",
        "40",
        "41",
        "42",
        "44",
        "46",
        "47",
        "48",
        "49",
        "50",
        "51",
        "52",
        "53",
        "54",
        "55",
        "56",
    ):
        _require(
            root.find(f"eval[@id='{eval_id}']/report_assertions/report") is not None,
            f"protocol/report eval {eval_id} missing report assertion",
        )

    preflight_eval_ids = set(TOOL_REGISTRY["eeglab_method_preflight"].eval_ids)
    for eval_id in ("18", "19", "20", "21", "22", "23", "24"):
        _require(
            eval_id in preflight_eval_ids,
            f"eeglab_method_preflight missing research gate eval coverage: {eval_id}",
        )

    return {
        "eval_count": len(eval_nodes),
        "eval_category_count": len(categories),
        "eval_resource_count": len(resource_uris),
        "eval_gate_method_count": len(gate_profiles),
    }


def _check_tool_support_matrix() -> None:
    text = (ROOT / "docs" / "official-tool-support-matrix.md").read_text(encoding="utf-8")
    for tool_name, spec in TOOL_REGISTRY.items():
        _require(
            tool_name in text,
            f"tool support matrix missing tool name: {tool_name}",
        )
        _require(
            spec.method_profile in text or spec.risk_level != "high",
            f"tool support matrix missing method profile for {tool_name}",
        )
    for term in (
        "read_only",
        "executable",
        "gated_executable",
        "guidance_only",
        "source claim IDs",
        "read/write effect",
    ):
        _require(term.lower() in text.lower(), f"tool support matrix missing {term}")


def _first_text(result: Any) -> dict[str, Any]:
    _require(bool(result.content), "tool returned no content")
    return json.loads(result.content[0].text)


def _structured(result: Any, tool_name: str) -> dict[str, Any]:
    """Assert workflow tools return both JSON text and structuredContent."""
    text_payload = _first_text(result)
    structured = getattr(result, "structuredContent", None)
    _require(isinstance(structured, dict), f"{tool_name} missing structuredContent")
    _require(
        structured == text_payload,
        f"{tool_name} structuredContent does not match text JSON",
    )
    for field in (
        "status",
        "workflow",
        "steps",
        "parameters",
        "outputs",
        "summary",
        "limitations",
    ):
        _require(field in structured, f"{tool_name} missing workflow field {field}")
    _require(structured["workflow"] == tool_name, f"{tool_name} workflow mismatch")
    return structured


def _assert_preflight_summary(payload: dict[str, Any], tool_name: str) -> None:
    summary = payload.get("summary", {})
    for field in (
        "gate_status",
        "missing_requirements",
        "critical_missing_requirements",
        "source_claim_ids",
        "safe_next_step",
        "override_used",
    ):
        _require(field in summary, f"{tool_name} preflight summary missing {field}")
    _require(
        isinstance(summary["source_claim_ids"], list),
        f"{tool_name} source_claim_ids must be a list",
    )
    _require(
        summary["gate_status"] in {"pass", "advisory", "blocked", "override_accepted", "unknown_method"},
        f"{tool_name} invalid gate_status: {summary['gate_status']}",
    )


async def _check_mcp() -> None:
    params = StdioServerParameters(command="python", args=["-B", "eeglab_mcp_server/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            tool_set = set(tool_names)
            registry_errors = validate_registry()
            _require(not registry_errors, f"registry errors: {registry_errors}")
            missing_legacy = sorted(LEGACY_LOW_LEVEL_TOOL_NAMES - tool_set)
            _require(not missing_legacy, f"missing legacy low-level tools: {missing_legacy}")
            missing_research = sorted(RESEARCH_WORKFLOW_TOOL_NAMES - tool_set)
            _require(
                not missing_research,
                f"missing research workflow tools: {missing_research}",
            )
            missing_registered = sorted(EXPOSED_TOOL_NAMES - tool_set)
            extra_tools = sorted(tool_set - EXPOSED_TOOL_NAMES)
            _require(not missing_registered, f"missing registry tools: {missing_registered}")
            _require(not extra_tools, f"unregistered MCP tools exposed: {extra_tools}")
            _require(
                len(tool_names) == TOTAL_EXPOSED_TOOL_COUNT,
                f"unexpected tool count: {len(tool_names)}",
            )
            tools_by_name = {tool.name: tool for tool in tools.tools}
            for tool_name in tool_names:
                spec = TOOL_REGISTRY[tool_name]
                description = tools_by_name[tool_name].description or ""
                _require(spec.handler, f"{tool_name} missing registry handler")
                _require(spec.docs_id, f"{tool_name} missing registry docs_id")
                _require(
                    spec.eeglab_function_family,
                    f"{tool_name} missing EEGLAB function family",
                )
                _require(spec.read_write_effect, f"{tool_name} missing read/write effect")
                for term in (
                    "Tool contract:",
                    "EEGLAB function family:",
                    "Official method profile:",
                    "Preflight:",
                    "Read/write effect:",
                    "Derivative output:",
                    spec.eeglab_function_family,
                    spec.read_write_effect,
                ):
                    _require(
                        term in description,
                        f"{tool_name} description missing tool contract term: {term}",
                    )
                if spec.risk_level == "high":
                    _require(
                        spec.method_profile in description,
                        f"{tool_name} description missing method profile",
                    )
                    _require(
                        "eeglab_method_preflight" in description,
                        f"{tool_name} description missing preflight route",
                    )

            prompts = await session.list_prompts()
            prompt_names = [prompt.name for prompt in prompts.prompts]
            for name in REQUIRED_PROMPTS:
                _require(name in prompt_names, f"missing prompt: {name}")

            resources = await session.list_resources()
            resource_uris = [str(resource.uri) for resource in resources.resources]
            for uri in sorted(REQUIRED_RESOURCES | _eval_resource_uris()):
                _require(uri in resource_uris, f"missing resource: {uri}")
                resource = await session.read_resource(uri)
                _require(bool(resource.contents), f"resource returned no contents: {uri}")

            unknown = _first_text(await session.call_tool("eeglab_unknown", {}))
            _require(
                unknown.get("code") == "unknown_tool",
                "unknown tool must return JSON error",
            )

            missing_args = _first_text(await session.call_tool("eeglab_load_data", {}))
            _require(
                missing_args.get("code") == "missing_required_arguments",
                "missing required args must return JSON error",
            )
            _require("next_step" in missing_args, "missing args error missing next_step")

            invalid_contract = _first_text(
                await session.call_tool("eeglab_filter", {"filter_type": "bandpass", "low_cutoff": 1})
            )
            _require(
                invalid_contract.get("code") == "invalid_tool_contract",
                "invalid contract must return JSON error",
            )
            _require("details" in invalid_contract, "invalid contract error missing details")

            recommendation = _structured(
                await session.call_tool("eeglab_workflow_recommend", {}),
                "eeglab_workflow_recommend",
            )
            _require(
                recommendation.get("status") == "success",
                "workflow recommendation failed",
            )
            _require(
                "not_recommended" in recommendation.get("summary", {}),
                "workflow recommendation missing not_recommended",
            )

            plan = _structured(
                await session.call_tool(
                    "eeglab_project_plan",
                    {
                        "analysis_type": "auto",
                        "event_types": ["s1000"],
                        "has_channel_locations": False,
                    },
                ),
                "eeglab_project_plan",
            )
            _require(plan.get("status") == "success", "project plan failed")
            _require(
                "blocking_conditions" in plan.get("summary", {}),
                "project plan missing blocking conditions",
            )

            study_plan = _structured(
                await session.call_tool(
                    "eeglab_project_plan",
                    {
                        "analysis_type": "study",
                        "project_scale": "bids_study",
                    },
                ),
                "eeglab_project_plan",
            )
            study_gate_profiles = {
                item.get("method_profile_id") for item in study_plan.get("summary", {}).get("gate_results", [])
            }
            _require(
                {
                    "bids_metadata",
                    "bids_import",
                    "study_create",
                    "study_design",
                    "study_statistics",
                }.issubset(study_gate_profiles),
                "project plan missing staged BIDS/STUDY gate results",
            )

            audit = _structured(
                await session.call_tool(
                    "eeglab_event_semantics_audit",
                    {
                        "event_types": ["s1000", "Impedance"],
                        "event_counts": {"s1000": 18, "Impedance": 2},
                        "segment_markers": ["s1000"],
                        "exclude_markers": ["Impedance"],
                    },
                ),
                "eeglab_event_semantics_audit",
            )
            _require(audit.get("status") == "success", "event semantics audit failed")
            _require(
                audit.get("summary", {}).get("confirmed_analysis_events") == [],
                "segment/impedance markers must not become analysis events",
            )

            protocol = _structured(
                await session.call_tool(
                    "eeglab_protocol_export",
                    {
                        "format": "markdown",
                        "research_goal": "framework verification",
                        "steps": ["quick_qc"],
                    },
                ),
                "eeglab_protocol_export",
            )
            _require(protocol.get("status") == "success", "protocol export failed")
            _require(
                "protocol_text" in protocol.get("outputs", {}),
                "protocol export missing text",
            )

            protocol_gate = {
                "method_profile_id": "source",
                "gate_status": "override_accepted",
                "source_claim_ids": ["EEGLAB-DIPFIT-001", "EEGLAB-CHANLOC-001"],
                "missing_requirement_ids": ["has_ica", "head_model_defined"],
                "override_used": True,
                "override_reason": "Framework verification override; no source claims will be made.",
                "blocked_requirements_acknowledged": [
                    "has_ica",
                    "head_model_defined",
                ],
            }
            protocol_with_gates = _structured(
                await session.call_tool(
                    "eeglab_protocol_export",
                    {
                        "format": "markdown",
                        "research_goal": "framework verification protocol",
                        "analysis_type": "source",
                        "steps": ["quick_qc", "source_preflight"],
                        "gate_results": [protocol_gate],
                        "report_fields": {
                            "recording_and_acquisition": ["input_path"],
                            "outputs_and_limits": ["official_gate_status"],
                        },
                        "override_used": True,
                        "override_reason": "Framework verification override; no source claims will be made.",
                        "blocked_requirements_acknowledged": [
                            "has_ica",
                            "head_model_defined",
                        ],
                    },
                ),
                "eeglab_protocol_export",
            )
            protocol_summary = protocol_with_gates.get("summary", {})
            _require(
                protocol_summary.get("source_claim_ids") == ["EEGLAB-DIPFIT-001", "EEGLAB-CHANLOC-001"],
                "protocol export should derive source_claim_ids from gate_results",
            )
            _require(
                protocol_summary.get("override_status", {}).get("override_used") is True,
                "protocol export should preserve override_used",
            )
            protocol_text = protocol_with_gates.get("outputs", {}).get("protocol_text", "")
            for term in (
                "Official Gate Results",
                "Report Field Matrix Coverage",
                "Override Status",
                "EEGLAB-DIPFIT-001",
                "has_ica",
            ):
                _require(term in protocol_text, f"protocol text missing {term}")

            preflight = _structured(
                await session.call_tool(
                    "eeglab_method_preflight",
                    {"method": "epoch", "context": {"event_roles": ["boundary"]}},
                ),
                "eeglab_method_preflight",
            )
            _require(preflight.get("status") == "success", "method preflight failed")
            _assert_preflight_summary(preflight, "eeglab_method_preflight")
            _require(
                preflight.get("summary", {}).get("gate_status") == "blocked",
                "boundary epoch preflight should be blocked",
            )

            acquisition = _structured(
                await session.call_tool(
                    "eeglab_method_preflight",
                    {
                        "method": "acquisition_metadata",
                        "context": {
                            "raw_input_preserved": False,
                            "derivative_output_planned": False,
                        },
                    },
                ),
                "eeglab_method_preflight",
            )
            _assert_preflight_summary(acquisition, "eeglab_method_preflight acquisition")
            _require(
                acquisition.get("summary", {}).get("gate_status") == "blocked",
                "acquisition metadata preflight should block missing provenance",
            )

            bids = _structured(
                await session.call_tool(
                    "eeglab_method_preflight",
                    {
                        "method": "bids_metadata",
                        "context": {
                            "bids_path": "sub-01",
                            "events_tsv_columns": ["onset", "duration", "trial_type"],
                        },
                    },
                ),
                "eeglab_method_preflight",
            )
            _assert_preflight_summary(bids, "eeglab_method_preflight bids")
            _require(
                bids.get("summary", {}).get("gate_status") == "blocked",
                "BIDS metadata preflight should block missing sidecar descriptions",
            )

            study_stats = _structured(
                await session.call_tool(
                    "eeglab_method_preflight",
                    {
                        "method": "study_statistics",
                        "context": {
                            "project_scale": "bids_study",
                            "design_variables": ["condition"],
                            "measure": "erp",
                            "alpha": 0.05,
                        },
                    },
                ),
                "eeglab_method_preflight",
            )
            _assert_preflight_summary(study_stats, "eeglab_method_preflight study_statistics")
            study_stats_missing = {
                item.get("id") for item in study_stats.get("summary", {}).get("critical_missing_requirements", [])
            }
            _require(
                "single_subject_protocol_locked" in study_stats_missing,
                "STUDY statistics preflight should require protocol lock",
            )

            override = _structured(
                await session.call_tool(
                    "eeglab_method_preflight",
                    {
                        "method": "source",
                        "context": {
                            "has_ica": False,
                            "has_channel_locations": False,
                        },
                        "override_reason": "Framework verification override; no source claims will be made.",
                    },
                ),
                "eeglab_method_preflight",
            )
            _assert_preflight_summary(override, "eeglab_method_preflight override")
            _require(
                override.get("summary", {}).get("gate_status") == "override_accepted",
                "override preflight should be accepted when reason is supplied",
            )
            _require(
                override.get("summary", {}).get("override_used") is True,
                "override_used should be true for accepted override",
            )

            blocked = _first_text(
                await session.call_tool(
                    "eeglab_epoch",
                    {
                        "event_types": ["boundary"],
                        "method_context": {"event_roles": ["boundary"]},
                    },
                )
            )
            _require(
                blocked.get("code") == "official_gate_blocked",
                "high-risk epoch call should be officially gated",
            )

            unconfirmed = _first_text(
                await session.call_tool(
                    "eeglab_epoch",
                    {"event_types": ["target"]},
                )
            )
            _require(
                unconfirmed.get("code") == "official_gate_blocked",
                "event_types alone should not satisfy official event semantics",
            )


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
    _check_registry_documentation_drift()
    _check_registry_handler_map()
    _check_static_structure_policy()
    eval_summary = _check_eval_registry_coverage()
    _check_tool_support_matrix()
    asyncio.run(_check_mcp())
    _check_cleanliness()
    print("framework_ok=True")
    print("eval_contract_ok=True")
    print(f"eval_count={eval_summary['eval_count']}")
    print(f"eval_category_count={eval_summary['eval_category_count']}")
    print(f"eval_gate_method_count={eval_summary['eval_gate_method_count']}")
    summary = registry_summary()
    print(f"legacy_low_level_tool_count={summary['legacy_low_level']}")
    print(f"research_workflow_tool_count={summary['research_workflow']}")
    print(f"total_exposed_tool_count={summary['total_exposed']}")
    print(f"prompt_count={len(REQUIRED_PROMPTS)}")
    print(f"resource_count={len(REQUIRED_RESOURCES)}")


if __name__ == "__main__":
    main()
