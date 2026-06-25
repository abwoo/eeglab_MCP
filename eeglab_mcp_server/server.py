"""EEGLAB MCP Server - 专业脑电分析 MCP 工具服务器

提供稳定 EEGLAB 工具、研究级规划工具和官方门控能力，支持两种 MATLAB 执行模式:
1. MATLAB Engine for Python (优先模式，需安装 matlab.engine)
2. MATLAB CLI 命令行 (回退模式，通过 matlab -batch 执行)

CLI 模式通过 .mat 文件在调用间保存/恢复 EEG 变量，解决每次新进程的问题。
Engine 模式使用 run_in_executor 避免阻塞事件循环。
"""

import asyncio
import json
import traceback
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions, ReadResourceContents
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

try:
    from .runtime import DEBUG_ERRORS, _error_response, _json_response
    from .schemas import (
        client_schema as shared_client_schema,
        json_type_matches as shared_json_type_matches,
        missing_required as shared_missing_required,
        validate_analysis_windows,
        validate_arguments as shared_validate_arguments,
        validate_tool_contracts as shared_validate_tool_contracts,
    )
    from .official_alignment import HIGH_RISK_TOOL_NAMES, evaluate_method_preflight
    from .handler_registry import TOOL_HANDLERS
    from .mcp_surfaces import PROMPT_DEFINITIONS, RESOURCE_FILES
    from .tool_definitions import build_tool_definitions
    from .tool_registry import validate_handler_map
    from .workflows import structured_payload, workflow_error
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import DEBUG_ERRORS, _error_response, _json_response
    from schemas import (
        client_schema as shared_client_schema,
        json_type_matches as shared_json_type_matches,
        missing_required as shared_missing_required,
        validate_analysis_windows,
        validate_arguments as shared_validate_arguments,
        validate_tool_contracts as shared_validate_tool_contracts,
    )
    from official_alignment import HIGH_RISK_TOOL_NAMES, evaluate_method_preflight
    from handler_registry import TOOL_HANDLERS
    from mcp_surfaces import PROMPT_DEFINITIONS, RESOURCE_FILES
    from tool_definitions import build_tool_definitions
    from tool_registry import validate_handler_map
    from workflows import structured_payload, workflow_error


def _missing_required(name: str, arguments: dict[str, Any]) -> list[str]:
    """检查 MCP input schema 中声明的必填参数。"""
    return shared_missing_required(name, arguments)


def _json_type_matches(value: Any, schema_type: str) -> bool:
    """Check a small JSON Schema type subset used by this server."""
    return shared_json_type_matches(value, schema_type)


def _validate_arguments(schema: dict[str, Any], arguments: dict[str, Any]) -> list[str]:
    """Validate the schema subset that matters before generating MATLAB code."""
    return shared_validate_arguments(schema, arguments)


def _validate_tool_contracts(name: str, arguments: dict[str, Any]) -> list[str]:
    """Validate cross-field contracts before handlers generate MATLAB code."""
    return shared_validate_tool_contracts(name, arguments)


def _normalize_tool_result(name: str, result: list[TextContent]) -> list[TextContent]:
    """把旧处理器返回的纯文本错误转换为统一 JSON。"""
    if len(result) != 1 or result[0].type != "text":
        return result

    text = result[0].text.strip()
    error_prefixes = ("错误:", "不支持的", "未知工具:")
    if text.startswith(error_prefixes):
        return _error_response(
            "tool_returned_error",
            text,
            next_step=f"检查 {name} 的参数和前置处理步骤，然后重试。",
        )
    return result


def _client_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return schema for MCP clients while keeping required checks in call_tool."""
    return shared_client_schema(schema)


def _arg_present(arguments: dict[str, Any], key: str) -> bool:
    value = arguments.get(key)
    if key not in arguments or value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _preflight_context_from_arguments(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Build official-gate context from explicit method_context plus obvious tool args."""
    context: dict[str, Any] = {}
    supplied = arguments.get("method_context")
    if isinstance(supplied, dict):
        context.update(supplied)

    if name in {"eeglab_epoch", "eeglab_erp_light_workflow"}:
        if arguments.get("event_types"):
            context.setdefault("candidate_event_types", arguments.get("event_types"))
        if arguments.get("epoch_window") or arguments.get("baseline_window"):
            context.setdefault("epoch_window", arguments.get("epoch_window"))
            context.setdefault("baseline_window", arguments.get("baseline_window"))
        if "pre_stimulus" in arguments or "post_stimulus" in arguments:
            context.setdefault(
                "epoch_window",
                [arguments.get("pre_stimulus"), arguments.get("post_stimulus")],
            )
            context.setdefault(
                "baseline_window",
                [arguments.get("baseline_start"), arguments.get("baseline_end")],
            )

    if name == "eeglab_timefreq":
        if arguments.get("baseline"):
            context.setdefault("baseline", arguments.get("baseline"))
        if arguments.get("freq_range") or arguments.get("cycles"):
            context.setdefault("freq_range", arguments.get("freq_range"))
            context.setdefault("cycles", arguments.get("cycles"))

    if name == "eeglab_clean_rawdata":
        context.setdefault(
            "thresholds_recorded",
            any(
                key in arguments
                for key in (
                    "flatline_criterion",
                    "channel_criterion",
                    "line_noise_criterion",
                    "burst_criterion",
                    "window_criterion",
                )
            ),
        )

    if name == "eeglab_clean_line_noise":
        if _arg_present(arguments, "line_freq"):
            context.setdefault("line_freq", arguments.get("line_freq"))
        if any(_arg_present(arguments, key) for key in ("bandwidth", "tau", "winsize")):
            context.setdefault("line_noise_method", "clean_line_noise")
            context.setdefault(
                "line_noise_parameters_recorded",
                bool(_arg_present(arguments, "line_freq")),
            )

    if name == "eeglab_spectral":
        if _arg_present(arguments, "freq_range"):
            context.setdefault("freq_range", arguments.get("freq_range"))
        if _arg_present(arguments, "channels"):
            context.setdefault("channels", arguments.get("channels"))
        if _arg_present(arguments, "band_power"):
            context.setdefault("parameters_recorded", True)

    if name == "eeglab_connectivity":
        if _arg_present(arguments, "freq_range"):
            context.setdefault("freq_range", arguments.get("freq_range"))
        if _arg_present(arguments, "channels"):
            context.setdefault("channels", arguments.get("channels"))
        if _arg_present(arguments, "method"):
            context.setdefault("method", arguments.get("method"))
            context.setdefault("connectivity_limits_recorded", True)

    if name == "eeglab_topoplot":
        if _arg_present(arguments, "time_point") or _arg_present(arguments, "time_window"):
            context.setdefault("parameters_recorded", True)
        if _arg_present(arguments, "channels"):
            context.setdefault("channels", arguments.get("channels"))
        if _arg_present(arguments, "output_path"):
            context.setdefault("output_path", arguments.get("output_path"))

    if name == "eeglab_edit_channels":
        if arguments.get("action") == "load_loc" and _arg_present(arguments, "loc_file"):
            context.setdefault("loc_file", arguments.get("loc_file"))
            context.setdefault("channel_location_repair_planned", True)
        if arguments.get("action") == "rename" and _arg_present(arguments, "rename_map"):
            context.setdefault("rename_map", arguments.get("rename_map"))
            context.setdefault("channel_location_repair_planned", True)
        if arguments.get("action"):
            context.setdefault("parameters_recorded", True)

    if name == "eeglab_interpolate_channels":
        if _arg_present(arguments, "ref_chanlocs"):
            context.setdefault("ref_chanlocs", arguments.get("ref_chanlocs"))
            context.setdefault("channel_location_repair_planned", True)
        if _arg_present(arguments, "method"):
            context.setdefault("parameters_recorded", True)

    if name == "eeglab_run_ica":
        context.setdefault(
            "rank_reference_reviewed",
            bool(arguments.get("pca_components") or context.get("rank_reference_reviewed")),
        )

    if name == "eeglab_remove_components":
        context.setdefault(
            "component_reviewed",
            bool(arguments.get("component_indices") or arguments.get("auto_remove_brain_threshold")),
        )

    if name in {"eeglab_source_localization", "eeglab_source_settings"}:
        context.setdefault("head_model", arguments.get("head_model"))
        context.setdefault("template", arguments.get("template"))
        if _arg_present(arguments, "chanfile"):
            context.setdefault("channel_location_repair_planned", True)
            context.setdefault("loc_file", arguments.get("chanfile"))

    if name in {"eeglab_study_create", "eeglab_import_bids"}:
        if arguments.get("bids_path"):
            context.setdefault("project_scale", "bids_study")
            context.setdefault("bids_path", arguments.get("bids_path"))
        if arguments.get("dataset_paths"):
            context.setdefault("project_scale", "multi_subject")
            context.setdefault("dataset_paths", arguments.get("dataset_paths"))
        if name == "eeglab_import_bids":
            context.setdefault(
                "plugin_eegbids_available",
                bool(
                    context.get("plugin_eegbids_available")
                    or "EEG-BIDS" in context.get("plugins_available", [])
                    or "pop_importbids" in context.get("plugins_available", [])
                ),
            )

    if name == "eeglab_study_design":
        context.setdefault("project_scale", "multi_subject")
        context.setdefault(
            "design_variables_defined",
            bool(arguments.get("variable_name") and arguments.get("variable_values")),
        )
        context.setdefault("variable_name", arguments.get("variable_name"))
        context.setdefault("variable_values", arguments.get("variable_values"))

    if name == "eeglab_study_statistics":
        context.setdefault("project_scale", "multi_subject")
        context.setdefault("study_measure_recorded", bool(arguments.get("measure")))
        context.setdefault("measure", arguments.get("measure"))
        context.setdefault(
            "parameters_recorded",
            bool(arguments.get("alpha") or arguments.get("correction")),
        )
        context.setdefault(
            "correction_policy_recorded",
            bool(arguments.get("alpha") and arguments.get("correction")),
        )

    if name in {
        "eeglab_filter",
        "eeglab_resample",
        "eeglab_reref",
        "eeglab_reject_epochs",
        "eeglab_clean_line_noise",
    }:
        context.setdefault("parameters_recorded", True)

    if name == "eeglab_pipeline":
        context.setdefault(
            "pipeline_defaults_accepted",
            bool(arguments.get("pipeline_defaults_accepted")),
        )
        context.setdefault("derivative_output_planned", bool(arguments.get("output_dir")))
        context.setdefault("output_dir", arguments.get("output_dir"))
        if arguments.get("event_types"):
            context.setdefault("candidate_event_types", arguments.get("event_types"))

    if arguments.get("output_dir") or arguments.get("output_path") or arguments.get("filepath"):
        context.setdefault(
            "derivative_output_planned",
            bool(arguments.get("output_dir") or arguments.get("output_path")),
        )
        context.setdefault("output_dir", arguments.get("output_dir"))
        context.setdefault("output_path", arguments.get("output_path"))

    return context


def _with_official_gate_metadata(result: Any, gate_result: dict[str, Any]) -> Any:
    """Attach preflight metadata to JSON text results when possible."""
    if isinstance(result, tuple):
        content, structured = result
        if isinstance(structured, dict):
            structured.setdefault("official_gate", gate_result)
            if gate_result.get("override_used"):
                structured["override_used"] = True
                structured["override_reason"] = gate_result.get("override_reason", "")
                structured["blocked_requirements_acknowledged"] = gate_result.get(
                    "blocked_requirements_acknowledged", []
                )
            content = _json_response(structured)
        return content, structured
    if not isinstance(result, list) or not result or not hasattr(result[0], "text"):
        return result
    try:
        payload = json.loads(result[0].text)
    except Exception:
        return result
    if isinstance(payload, dict):
        payload.setdefault("official_gate", gate_result)
        if gate_result.get("override_used"):
            payload["override_used"] = True
            payload["override_reason"] = gate_result.get("override_reason", "")
            payload["blocked_requirements_acknowledged"] = gate_result.get("blocked_requirements_acknowledged", [])
        return _json_response(payload)
    return result


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("eeglab-mcp-server")
try:
    from .tool_registry import RESEARCH_WORKFLOW_TOOL_NAMES as WORKFLOW_TOOL_NAMES
except ImportError:  # pragma: no cover - direct script execution support
    from tool_registry import RESEARCH_WORKFLOW_TOOL_NAMES as WORKFLOW_TOOL_NAMES


# ---------------------------------------------------------------------------
# list_tools - 返回所有工具定义
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 EEGLAB MCP 工具。"""
    tools = build_tool_definitions()
    for tool in tools:
        tool.inputSchema = _client_schema(tool.inputSchema)
    return tools


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List built-in research workflow prompts for clients that support MCP prompts."""
    return [
        Prompt(
            name=name,
            title=definition["title"],
            description=definition["description"],
            arguments=[],
        )
        for name, definition in PROMPT_DEFINITIONS.items()
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Return a built-in prompt without touching EEG data or MATLAB state."""
    if name not in PROMPT_DEFINITIONS:
        raise ValueError(f"Unknown prompt: {name}")
    definition = PROMPT_DEFINITIONS[name]
    return GetPromptResult(
        description=definition["description"],
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=definition["text"]),
            )
        ],
    )


@server.list_resources()
async def list_resources() -> list[Resource]:
    """Expose skill/reference files as read-only MCP resources."""
    resources: list[Resource] = []
    for uri, (name, path, description) in RESOURCE_FILES.items():
        size = path.stat().st_size if path.exists() else None
        resources.append(
            Resource(
                uri=uri,
                name=name,
                title=name,
                description=description,
                mimeType="text/markdown",
                size=size,
            )
        )
    return resources


@server.read_resource()
async def read_resource(uri: Any) -> list[ReadResourceContents]:
    """Read a bundled skill/reference resource without modifying local state."""
    uri_text = str(uri)
    if uri_text not in RESOURCE_FILES:
        raise ValueError(f"Unknown resource: {uri_text}")
    _, path, _ = RESOURCE_FILES[uri_text]
    if not path.exists():
        raise FileNotFoundError(f"Resource file is missing: {path}")
    return [ReadResourceContents(content=path.read_text(encoding="utf-8"), mime_type="text/markdown")]


# ---------------------------------------------------------------------------
# call_tool - 分发到处理器
# ---------------------------------------------------------------------------


def _workflow_error_payload_from_plain(name: str, payload: dict[str, Any]):
    return structured_payload(
        workflow_error(
            name,
            "validate_arguments",
            payload,
            parameters={},
            steps=[],
        )
    )


def _analysis_window_errors(name: str, arguments: dict[str, Any]) -> list[str]:
    """Validate EEG time/frequency windows that need cross-field checks."""
    if name == "eeglab_epoch":
        pre_stim = arguments.get("pre_stimulus", -0.2)
        post_stim = arguments.get("post_stimulus", 0.8)
        bl_start = arguments.get("baseline_start", -0.2)
        bl_end = arguments.get("baseline_end", 0)
        return validate_analysis_windows(
            epoch_window=[pre_stim, post_stim],
            baseline_window_ms=[bl_start * 1000, bl_end * 1000],
        )
    if name == "eeglab_erp_analysis":
        time_window = arguments.get("time_window")
        return validate_analysis_windows(time_window_ms=time_window) if time_window else []
    if name == "eeglab_pipeline":
        return validate_analysis_windows(
            epoch_window=arguments.get("epoch_window", [-0.2, 0.8]),
            baseline_window_ms=arguments.get("baseline_window", [-200, 0]),
        )
    if name == "eeglab_erp_light_workflow":
        return validate_analysis_windows(
            epoch_window=arguments.get("epoch_window", [-0.2, 0.8]),
            baseline_window_ms=arguments.get("baseline_window", [-200, 0]),
            time_window_ms=arguments.get("time_window", [250, 450]),
        )
    return []


@server.call_tool(validate_input=False)
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    """处理工具调用。"""
    handlers = TOOL_HANDLERS
    registry_errors = validate_handler_map(handlers)
    if registry_errors:
        return _error_response(
            "tool_registry_mismatch",
            "Tool registry and handler map are inconsistent.",
            next_step="Fix ToolRegistry metadata and call_tool handler coverage before running tools.",
            details={"errors": registry_errors},
        )

    handler = handlers.get(name)
    if not handler:
        return _error_response(
            "unknown_tool",
            f"未知工具: {name}",
            next_step="调用 tools/list 查看可用的 eeglab_* 工具。当前口径为 39 个 legacy low-level 工具加 9 个 research workflow 工具。",
        )

    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        payload = {
            "status": "error",
            "code": "invalid_arguments",
            "error": "工具参数必须是 JSON object。",
            "next_step": f"重新调用 {name}，并传入对象形式的 arguments。",
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)

    tools = build_tool_definitions()
    schema_by_name = {tool.name: tool.inputSchema for tool in tools}
    schema = schema_by_name.get(name, {})
    missing = _missing_required(name, arguments)
    if missing:
        payload = {
            "status": "error",
            "code": "missing_required_arguments",
            "error": f"{name} 缺少必填参数: {', '.join(missing)}",
            "next_step": "补齐缺失参数后重试。",
            "details": {"missing": missing},
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)

    validation_errors = _validate_arguments(schema, arguments)
    if validation_errors:
        payload = {
            "status": "error",
            "code": "invalid_arguments",
            "error": f"{name} 参数不符合 schema: {'; '.join(validation_errors)}",
            "next_step": "按工具 inputSchema 调整参数后重试。",
            "details": {"errors": validation_errors},
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)

    contract_errors = _validate_tool_contracts(name, arguments)
    if contract_errors:
        payload = {
            "status": "error",
            "code": "invalid_tool_contract",
            "error": f"{name} 参数组合不合法: {'; '.join(contract_errors)}",
            "next_step": "按工具说明补齐互相依赖的参数，或移除互斥参数后重试。",
            "details": {"errors": contract_errors},
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)

    window_errors = _analysis_window_errors(name, arguments)
    if window_errors:
        payload = {
            "status": "error",
            "code": "invalid_analysis_window",
            "error": f"{name} 分析窗口不合法: {'; '.join(window_errors)}",
            "next_step": "调整 epoch、baseline、time/frequency 窗口后重试。",
            "details": {"errors": window_errors},
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)

    try:
        official_gate: dict[str, Any] | None = None
        if name in HIGH_RISK_TOOL_NAMES:
            context = _preflight_context_from_arguments(name, arguments)
            official_gate = evaluate_method_preflight(
                {
                    "tool_name": name,
                    "context": context,
                    "strictness": "hard",
                    "override_reason": (arguments.get("override_reason", "") if arguments.get("override_gate") else ""),
                }
            )
            if official_gate.get("gate_status") == "blocked":
                payload = {
                    "status": "error",
                    "code": "official_gate_blocked",
                    "error": f"{name} 被官方前置条件门控阻断。",
                    "next_step": official_gate.get("safe_next_step", "补齐前置条件或提供显式 override_reason。"),
                    "details": official_gate,
                }
                if name in WORKFLOW_TOOL_NAMES:
                    return _workflow_error_payload_from_plain(name, payload)
                return _json_response(payload)
        result = _normalize_tool_result(name, await handler(arguments))
        if official_gate:
            result = _with_official_gate_metadata(result, official_gate)
        return result
    except KeyError as e:
        missing = str(e).strip("'\"")
        payload = {
            "status": "error",
            "code": "missing_required_argument",
            "error": f"{name} 缺少必填参数: {missing}",
            "next_step": "补齐缺失参数后重试。",
            "details": {"missing": [missing]},
        }
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)
    except Exception as e:
        details = {"traceback": traceback.format_exc()} if DEBUG_ERRORS else None
        payload = {
            "status": "error",
            "code": "tool_execution_error",
            "error": f"工具执行错误 [{name}]: {str(e)}",
            "next_step": "检查输入参数、MATLAB/EEGLAB 环境和当前 EEG 工作区状态后重试。",
        }
        if details:
            payload["details"] = details
        if name in WORKFLOW_TOOL_NAMES:
            return _workflow_error_payload_from_plain(name, payload)
        return _json_response(payload)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eeglab-mcp-server",
                server_version="1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_main() -> None:
    """Console-script entry point for local stdio MCP clients."""
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
