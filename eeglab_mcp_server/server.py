"""EEGLAB MCP Server - 专业脑电分析 MCP 工具服务器

提供 8 大类 37 个专业 EEGLAB 脑电分析工具，支持两种 MATLAB 执行模式:
1. MATLAB Engine for Python (优先模式，需安装 matlab.engine)
2. MATLAB CLI 命令行 (回退模式，通过 matlab -batch 执行)

CLI 模式通过 .mat 文件在调用间保存/恢复 EEG 变量，解决每次新进程的问题。
Engine 模式使用 run_in_executor 避免阻塞事件循环。
"""

import asyncio
import json
import math
import os
import subprocess
import tempfile
import traceback
from pathlib import Path
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
    from .backend import DEBUG_ERRORS as SHARED_DEBUG_ERRORS
    from .backend import cfg as SHARED_CFG
    from .backend import matlab as SHARED_MATLAB
    from .matlab_literals import (
        _arr as SHARED_ARR,
        _cell as SHARED_CELL,
        _esc as SHARED_ESC,
        _matlab_text as SHARED_MATLAB_TEXT,
        matlab_cell as SHARED_MATLAB_CELL,
        matlab_numeric_array as SHARED_MATLAB_NUMERIC_ARRAY,
        matlab_string as SHARED_MATLAB_STRING,
    )
    from .schemas import (
        REQUIRED_ARGUMENTS as SHARED_REQUIRED_ARGUMENTS,
        annotate_tools,
        client_schema as shared_client_schema,
        json_type_matches as shared_json_type_matches,
        missing_required as shared_missing_required,
        validate_analysis_windows,
        validate_arguments as shared_validate_arguments,
        validate_tool_contracts as shared_validate_tool_contracts,
        workflow_tools,
    )
    from .workflows import (
        light_erp_parameters,
        parse_tool_result,
        qc_report_from_payloads,
        recommend_workflow,
        structured_payload,
        workflow_error,
        workflow_success,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from backend import DEBUG_ERRORS as SHARED_DEBUG_ERRORS
    from backend import cfg as SHARED_CFG
    from backend import matlab as SHARED_MATLAB
    from matlab_literals import (
        _arr as SHARED_ARR,
        _cell as SHARED_CELL,
        _esc as SHARED_ESC,
        _matlab_text as SHARED_MATLAB_TEXT,
        matlab_cell as SHARED_MATLAB_CELL,
        matlab_numeric_array as SHARED_MATLAB_NUMERIC_ARRAY,
        matlab_string as SHARED_MATLAB_STRING,
    )
    from schemas import (
        REQUIRED_ARGUMENTS as SHARED_REQUIRED_ARGUMENTS,
        annotate_tools,
        client_schema as shared_client_schema,
        json_type_matches as shared_json_type_matches,
        missing_required as shared_missing_required,
        validate_analysis_windows,
        validate_arguments as shared_validate_arguments,
        validate_tool_contracts as shared_validate_tool_contracts,
        workflow_tools,
    )
    from workflows import (
        light_erp_parameters,
        parse_tool_result,
        qc_report_from_payloads,
        recommend_workflow,
        structured_payload,
        workflow_error,
        workflow_success,
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class Config:
    """从环境变量读取配置。"""
    EEGLAB_PATH: str = os.environ.get("EEGLAB_PATH", "")
    MATLAB_ROOT: str = os.environ.get("MATLAB_ROOT", "")
    EEGLAB_WORK_DIR: str = os.environ.get(
        "EEGLAB_WORK_DIR",
        str(Path.home() / "Desktop" / "eeglabmcp")
    )
    MATLAB_EXEC: str = os.environ.get("MATLAB_EXEC", "matlab")
    MATLAB_TIMEOUT: int = int(os.environ.get("MATLAB_TIMEOUT", "300"))


cfg = SHARED_CFG
DEBUG_ERRORS = SHARED_DEBUG_ERRORS

# ---------------------------------------------------------------------------
# MATLAB Execution Backend
# ---------------------------------------------------------------------------

class MatlabBackend:
    """MATLAB 执行后端，支持 Engine API 和 CLI 两种模式。

    Engine 模式: 使用 run_in_executor 避免阻塞事件循环。
    CLI 模式: 通过 .mat 文件在调用间保存/恢复 EEG 变量。
    """

    def __init__(self):
        self._engine = None
        self._mode: str | None = None  # 'engine' | 'cli' | 'none'
        self._eeglab_initialized = False
        self._work_dir: str = cfg.EEGLAB_WORK_DIR
        self._eeg_state_file: str = ""

    # ---- mode detection ----

    def _detect_mode(self) -> str:
        """检测可用的 MATLAB 执行模式。"""
        try:
            import matlab.engine  # noqa: F401
            return "engine"
        except ImportError:
            pass

        try:
            result = subprocess.run(
                [cfg.MATLAB_EXEC, "-batch", "disp('ok')"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return "cli"
        except Exception:
            pass

        return "none"

    # ---- public API ----

    async def execute(self, code: str, project_path: str = "") -> dict:
        """执行 MATLAB 代码并返回结构化结果。

        Args:
            code: MATLAB 代码字符串
            project_path: 工作目录

        Returns:
            dict: {"status": "success"/"error", "output": str, ...}
        """
        if self._mode is None:
            self._mode = self._detect_mode()

        if self._mode == "engine":
            result = await self._execute_engine(code, project_path)
        elif self._mode == "cli":
            result = await self._execute_cli(code, project_path)
        else:
            result = {
                "status": "error",
                "error": "MATLAB 不可用。请安装 MATLAB Engine for Python 或确保 matlab 命令在 PATH 中。",
                "hint": "Engine: cd 'MATLAB_PATH/extern/engines/python' && python setup.py install\n"
                        "CLI: 确保 matlab 在系统 PATH 中",
            }
        if "eeglab nogui" in code:
            self._eeglab_initialized = self._mode == "engine" and result.get("status") == "success"
        return result

    @property
    def eeglab_initialized(self) -> bool:
        return self._eeglab_initialized

    @eeglab_initialized.setter
    def eeglab_initialized(self, value: bool):
        self._eeglab_initialized = value

    # ---- Engine mode ----

    async def _execute_engine(self, code: str, project_path: str) -> dict:
        """通过 MATLAB Engine for Python 执行（使用 run_in_executor 避免阻塞）。"""
        try:
            import matlab.engine
        except ImportError:
            self._mode = None
            return await self.execute(code, project_path)

        if self._engine is None:
            try:
                self._engine = matlab.engine.start_matlab()
            except Exception as e:
                return {"status": "error", "error": f"启动 MATLAB 引擎失败: {e}"}

        try:
            if project_path:
                self._engine.eval(f"cd({matlab_string(project_path)});", nargout=0)

            fd, result_file = tempfile.mkstemp(suffix='.json')
            os.close(fd)

            wrapped = f"""
result = struct();
try
{code}
    if ~exist('result', 'var') || ~isstruct(result)
        result = struct();
    end
    if ~isfield(result, 'status')
        result.status = 'success';
    end
catch ME
    result = struct();
    result.status = 'error';
    result.error = ME.message;
    result.identifier = ME.identifier;
end
jsonStr = jsonencode(result);
fid = fopen({matlab_string(result_file)}, 'w');
fprintf(fid, '%s', jsonStr);
fclose(fid);
"""
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._engine.eval(wrapped, nargout=0))

            if os.path.exists(result_file):
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                try:
                    os.unlink(result_file)
                except Exception:
                    pass
                return data
            return {"status": "error", "error": "无法读取结果文件"}

        except Exception as e:
            self._engine = None
            self._eeglab_initialized = False
            return {"status": "error", "error": f"Engine 执行错误: {e}"}

    # ---- CLI mode ----

    async def _execute_cli(self, code: str, project_path: str) -> dict:
        """通过 MATLAB CLI 子进程执行，支持 EEG 状态持久化。"""
        # 确保工作目录存在
        os.makedirs(self._work_dir, exist_ok=True)

        # 确定状态文件路径
        if not self._eeg_state_file:
            fd, self._eeg_state_file = tempfile.mkstemp(
                suffix='.mat', prefix='eeg_state_', dir=self._work_dir
            )
            os.close(fd)

        # 构建加载/保存 EEG 状态的代码
        load_code = ""
        save_code = ""
        if os.path.exists(self._eeg_state_file) and os.path.getsize(self._eeg_state_file) > 0:
            state_file = matlab_string(self._eeg_state_file)
            load_code = f"try; EEG = load({state_file}, 'EEG'); EEG = EEG.EEG; catch; end\n"

        # 在代码末尾保存 EEG 状态
        save_code = f"""
if exist('EEG', 'var') && isstruct(EEG)
    try; save({matlab_string(self._eeg_state_file)}, 'EEG', '-v7'); catch; end
end
"""

        fd, result_file = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        result_literal = matlab_string(result_file)

        cd_code = f"cd({matlab_string(project_path)}); " if project_path else ""

        wrapped = f"""
{cd_code}
{load_code}
result = struct();
try
{code}
{save_code}
    if ~exist('result', 'var') || ~isstruct(result)
        result = struct();
    end
    if ~isfield(result, 'status')
        result.status = 'success';
    end
catch ME
{save_code}
    result = struct();
    result.status = 'error';
    result.error = ME.message;
    result.identifier = ME.identifier;
end
jsonStr = jsonencode(result);
fid = fopen({result_literal}, 'w');
fprintf(fid, '%s', jsonStr);
fclose(fid);
exit;
"""

        # 写入临时 .m 文件
        fd, script_path = tempfile.mkstemp(suffix='.m')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(wrapped)

        try:
            loop = asyncio.get_event_loop()
            proc_result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [cfg.MATLAB_EXEC, "-batch", f"run({matlab_string(script_path)})"],
                    capture_output=True, text=True, timeout=cfg.MATLAB_TIMEOUT,
                ),
            )

            if os.path.exists(result_file):
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                try:
                    os.unlink(result_file)
                except Exception:
                    pass
                return data
            else:
                return {
                    "status": "error",
                    "error": f"MATLAB 执行失败 (exit code: {proc_result.returncode})",
                    "stdout": proc_result.stdout[-500:] if proc_result.stdout else "",
                    "stderr": proc_result.stderr[-500:] if proc_result.stderr else "",
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": f"MATLAB 执行超时 ({cfg.MATLAB_TIMEOUT}秒)"}
        except Exception as e:
            return {"status": "error", "error": f"CLI 执行错误: {e}"}
        finally:
            try:
                os.unlink(script_path)
            except Exception:
                pass
            try:
                if os.path.exists(result_file):
                    os.unlink(result_file)
            except Exception:
                pass

    # ---- EEG state persistence (CLI mode) ----

    def _save_eeg_state(self) -> str:
        """生成保存 EEG 到 .mat 文件的 MATLAB 代码。"""
        if self._mode == "cli" and self._eeg_state_file:
            return f"if exist('EEG','var') && isstruct(EEG); save({matlab_string(self._eeg_state_file)},'EEG','-v7'); end\n"
        return ""

    def _load_eeg_state(self) -> str:
        """生成从 .mat 文件加载 EEG 的 MATLAB 代码。"""
        if self._mode == "cli" and self._eeg_state_file:
            return f"try; tmp=load({matlab_string(self._eeg_state_file)},'EEG'); EEG=tmp.EEG; catch; end\n"
        return ""


# 全局后端实例。MatlabBackend 的旧类保留给历史兼容，运行时使用模块化后端。
matlab = SHARED_MATLAB

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

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


def _esc(path: Any) -> str:
    """Compatibility helper for legacy code that still wraps values in quotes."""
    return _matlab_text(path)


def _eeglab_init_code() -> str:
    """生成 EEGLAB 初始化代码（仅首次调用时初始化）。"""
    code = ""
    if cfg.EEGLAB_PATH:
        code += f"addpath(genpath({matlab_string(cfg.EEGLAB_PATH)})); "
    code += "eeglab nogui; "
    return code


def _maybe_init() -> str:
    """如果 EEGLAB 尚未初始化，则生成初始化代码。"""
    if matlab._mode == "cli":
        return _eeglab_init_code()
    if matlab.eeglab_initialized:
        return ""
    return _eeglab_init_code()


def _cell(items: list) -> str:
    """将 Python 列表转为 MATLAB cell 数组字符串。"""
    return matlab_cell(items)


def _arr(items: list) -> str:
    """将 Python 列表转为 MATLAB 数组字符串。"""
    return matlab_numeric_array(items)


# Route literal helpers through the shared module; legacy names stay available
# for the 37 existing handlers.
_matlab_text = SHARED_MATLAB_TEXT
matlab_string = SHARED_MATLAB_STRING
matlab_cell = SHARED_MATLAB_CELL
matlab_numeric_array = SHARED_MATLAB_NUMERIC_ARRAY
_esc = SHARED_ESC
_cell = SHARED_CELL
_arr = SHARED_ARR


def _json_response(payload: dict[str, Any]) -> list[TextContent]:
    """返回 MCP text content，内容始终是 JSON。"""
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _error_response(
    code: str,
    message: str,
    *,
    next_step: str = "",
    details: dict[str, Any] | None = None,
) -> list[TextContent]:
    """生成统一的工具错误响应。"""
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


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("eeglab-mcp-server")
ROOT_DIR = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT_DIR / "skills" / "eeglab-analysis"

PROMPT_DEFINITIONS: dict[str, dict[str, str]] = {
    "eeglab_project_intake": {
        "title": "EEGLAB Project Intake",
        "description": "Start a strict EEG research project by gathering goal, scale, data shape, events, montage, outputs, and constraints.",
        "text": (
            "Use this intake before running EEG processing. Ask for or infer: research goal/hypothesis, "
            "project scale, subject/session structure, EEG file format, sampling rate, event labels, "
            "montage/reference/channel-location status, required outputs, and whether group/STUDY analysis is needed. "
            "Then call eeglab_workflow_recommend with all known facts and use its qc_gates before destructive steps."
        ),
    },
    "eeglab_strict_qc_protocol": {
        "title": "EEGLAB Strict QC Protocol",
        "description": "Inspect recording/provenance metadata before preprocessing or analysis.",
        "text": (
            "Run eeglab_init, eeglab_load_data, eeglab_qc_report, eeglab_info, eeglab_get_events, and eeglab_history. "
            "Report source path, sampling rate, duration, data shape, channel count, channel-location coverage, reference/montage, "
            "event labels/counts/latencies, processing-history availability, plugin limitations, and raw-preservation strategy. "
            "Do not make clinical claims."
        ),
    },
    "eeglab_dual_mcp_routing": {
        "title": "EEGLAB + MATLAB MCP Routing",
        "description": "Route work when both eeglab and general matlab MCP servers are available.",
        "text": (
            "Use eeglab first for EEG/EEGLAB data loading, QC, event audit, preprocessing, ICA, ERP, spectral/time-frequency, "
            "source, STUDY, and EEGLAB figures. Use matlab MCP for generic MATLAB scripts, custom matrix/statistical code, "
            "or non-EEGLAB toolboxes. Treat the servers as workspace-isolated sessions; use file handoff via .set/.fdt, "
            ".mat, .csv, .png, or reports. Never assume EEG variables are shared across MCP servers."
        ),
    },
    "eeglab_report_template": {
        "title": "EEGLAB Research Report Template",
        "description": "Structure a concise reproducible EEG processing report.",
        "text": (
            "Report in this order: recording/provenance facts, user goal and assumptions, QC gates, processing steps, "
            "exact parameters, outputs/files, failures/recovery, limitations, and next recommended analysis. Include filter cutoffs, "
            "line-noise handling, rereference, bad-channel handling, ICA/ICLabel decisions, epoch/baseline windows, frequency ranges, "
            "rejected data/components, and software/plugin limitations."
        ),
    },
}

RESOURCE_FILES: dict[str, tuple[str, Path, str]] = {
    "eeglab://skill/SKILL.md": (
        "EEGLAB Analysis Skill",
        SKILL_DIR / "SKILL.md",
        "Primary EEG research workflow skill used by clients that support skills.",
    ),
    "eeglab://references/workflows.md": (
        "EEGLAB Workflow Reference",
        SKILL_DIR / "references" / "workflows.md",
        "Workflow recipes for inspection, preprocessing, ERP, time-frequency, ICA, STUDY, and source workflows.",
    ),
    "eeglab://references/tools.md": (
        "EEGLAB Tool Reference",
        SKILL_DIR / "references" / "tools.md",
        "Tool groups, routing rules, common parameters, and project-scale guardrails.",
    ),
    "eeglab://references/setup.md": (
        "EEGLAB Setup Reference",
        SKILL_DIR / "references" / "setup.md",
        "MCP and skill setup guidance, including MATLAB MCP pairing and verification.",
    ),
}

REQUIRED_ARGUMENTS: dict[str, list[str]] = {
    "eeglab_load_data": ["filepath"],
    "eeglab_save_data": ["filepath"],
    "eeglab_import_bids": ["bids_path"],
    "eeglab_filter": ["filter_type"],
    "eeglab_resample": ["new_srate"],
    "eeglab_reref": ["ref_type"],
    "eeglab_edit_channels": ["action"],
    "eeglab_sort_epochs": ["sort_by"],
    "eeglab_topoplot": ["output_path"],
    "eeglab_plot_erp": ["channels", "output_path"],
    "eeglab_plot_timefreq": ["channel", "output_path"],
    "eeglab_plot_components": ["output_path"],
    "eeglab_pipeline": ["pipeline_type", "data_path"],
}
REQUIRED_ARGUMENTS = SHARED_REQUIRED_ARGUMENTS
WORKFLOW_TOOL_NAMES = {"eeglab_qc_report", "eeglab_erp_light_workflow", "eeglab_workflow_recommend"}


# ---------------------------------------------------------------------------
# list_tools - 返回所有工具定义
# ---------------------------------------------------------------------------

def _tool_definitions() -> list[Tool]:
    """Build raw tool definitions with complete schemas for internal validation."""
    tools = [
        # ===== 第 1 类：数据管理 =====
        Tool(
            name="eeglab_init",
            description="初始化 EEGLAB 环境。在执行任何 EEGLAB 操作前必须先调用此工具。"
                        "会启动 MATLAB 并加载 EEGLAB（无界面模式）。"
                        "可选指定 EEGLAB 安装路径，否则使用环境变量 EEGLAB_PATH。",
            inputSchema={
                "type": "object",
                "properties": {
                    "eeglab_path": {
                        "type": "string",
                        "description": "EEGLAB 安装目录的绝对路径。例如: C:/eeglab2024.0 或 /home/user/eeglab"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_load_data",
            description="加载 EEG 数据文件。支持 EEGLAB 原生格式(.set/.fdt)、BrainVision(.vhdr)、"
                        "EDF/EDF+(.edf)、BioSemi(.bdf)、Neuroscan(.cnt) 等格式。"
                        "加载后数据存储在 MATLAB 工作区的 EEG 变量中，可供后续分析工具使用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "EEG 数据文件的绝对路径。例如: C:/data/subject01.set"
                    },
                    "filename": {
                        "type": "string",
                        "description": "文件名（当 filepath 仅指定目录时需要）。例如: subject01.set"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="eeglab_save_data",
            description="保存当前 EEG 数据到文件（.set 格式）。"
                        "在执行破坏性操作（如滤波、ICA 去伪迹）后建议保存数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "保存文件的绝对路径。例如: C:/data/subject01_filtered.set"
                    },
                    "filename": {
                        "type": "string",
                        "description": "保存的文件名。例如: subject01_filtered.set"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="eeglab_import_bids",
            description="导入 BIDS 格式数据集。BIDS (Brain Imaging Data Structure) 是神经科学数据组织的标准格式。"
                        "导入后自动创建 STUDY 和 ALLEEG，可进行组级别分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "BIDS 数据集根目录的绝对路径"
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY 名称"
                    }
                },
                "required": ["bids_path"]
            }
        ),
        Tool(
            name="eeglab_info",
            description="获取当前 EEG 数据集的详细信息。包括通道数、采样率、数据点数、试次数、"
                        "时间窗口、通道标签、事件类型、ICA 状态等。用于了解数据概况和验证处理结果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_channels": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含通道标签列表"
                    },
                    "include_events": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含事件类型列表"
                    },
                    "include_ica": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含 ICA 信息"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_history",
            description="获取当前 EEG 数据集的操作历史记录。记录了从加载数据以来执行的所有 EEGLAB 操作。"
                        "可用于追踪分析流程、验证处理步骤、复现分析过程。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # ===== 第 2 类：预处理 =====
        Tool(
            name="eeglab_filter",
            description="对 EEG 数据进行滤波处理。支持带通(bandpass)、高通(highpass)、低通(lowpass)和陷波(notch)滤波。"
                        "使用 EEGLAB 推荐的 pop_eegfiltnew (FIR Hamming 窗) 和 pop_cleanline (陷波)。"
                        "专业建议: ERP研究用 0.1-40Hz 带通; 时频研究用 0.5-80Hz 带通; "
                        "50Hz(中国/欧洲)或60Hz(美国)陷波去工频; ICA 前建议高通 1Hz 滤波。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["bandpass", "highpass", "lowpass", "notch"],
                        "description": "滤波类型: bandpass(带通), highpass(高通), lowpass(低通), notch(陷波)"
                    },
                    "low_cutoff": {
                        "type": "number",
                        "description": "低截止频率(Hz)。带通/高通时必填。常用值: 0.1(去漂移), 0.5, 1(ICA前推荐)"
                    },
                    "high_cutoff": {
                        "type": "number",
                        "description": "高截止频率(Hz)。带通/低通时必填。常用值: 30, 40, 80, 100"
                    },
                    "notch_freq": {
                        "type": "number",
                        "description": "陷波频率(Hz)。notch 类型时必填。50(中国/欧洲)或60(美国)"
                    },
                    "notch_harmonics": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否同时去除陷波频率的谐波(如100Hz, 150Hz)"
                    }
                },
                "required": ["filter_type"]
            }
        ),
        Tool(
            name="eeglab_resample",
            description="对 EEG 数据进行重采样。降低采样率可减少数据量和计算时间。"
                        "专业建议: 降采样前应先加低通抗混叠滤波; 常用目标采样率: 250Hz(ERP), 500Hz(时频)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "new_srate": {
                        "type": "number",
                        "description": "目标采样率(Hz)。例如: 250, 500"
                    }
                },
                "required": ["new_srate"]
            }
        ),
        Tool(
            name="eeglab_reref",
            description="对 EEG 数据进行重参考。支持平均参考(所有通道均值)、单通道参考(如 Cz, 乳突)和 REST 参考。"
                        "专业建议: 平均参考是最常用的参考方式，适用于大多数研究场景; "
                        "平均参考会使数据秩减 1，ICA 时需设置 pca=nchan-1; "
                        "ICA 通常在重参考前运行，或使用平均参考。",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref_type": {
                        "type": "string",
                        "enum": ["average", "channel", "rest"],
                        "description": "参考类型: average(平均参考), channel(单通道参考), rest(REST参考)"
                    },
                    "ref_channel": {
                        "type": "string",
                        "description": "参考通道标签。ref_type 为 channel 时必填。例如: 'Cz', 'M1', 'A1'"
                    }
                },
                "required": ["ref_type"]
            }
        ),
        Tool(
            name="eeglab_select_channels",
            description="选择或排除特定通道。用于去除坏通道或只保留感兴趣的区域。"
                        "专业建议: ICA 前应去除明显坏通道，但保留足够通道数; "
                        "去除通道后再做 ICA 会降低成分数。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要保留的通道标签列表。例如: ['Fz','Cz','Pz']。与 exclude_channels 二选一"
                    },
                    "exclude_channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要排除的通道标签列表。例如: ['EOG1','EOG2','EMG']。与 channels 二选一"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_interpolate_channels",
            description="通道插值。使用球面样条插值法从周围通道估计坏通道的信号。"
                        "专业建议: 应在 ICA 去伪迹后使用，而非之前; "
                        "可使用 urchanlocs 恢复之前删除的通道。",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref_chanlocs": {
                        "type": "string",
                        "description": "参考通道位置。'urchanlocs' 恢复原始通道，或指定 .loc 文件路径。留空则使用当前通道位置"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["spherical", "v4"],
                        "default": "spherical",
                        "description": "插值方法: spherical(球面样条,推荐) 或 v4(双调和样条)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_edit_channels",
            description="编辑通道信息。加载 .loc 位置文件、重命名通道等。"
                        "专业建议: 加载数据后应检查通道位置是否正确，否则地形图和源定位结果会出错。",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["load_loc", "rename"],
                        "description": "操作类型: load_loc(加载位置文件), rename(重命名通道)"
                    },
                    "loc_file": {
                        "type": "string",
                        "description": "通道位置文件路径(.loc/.ced)。action 为 load_loc 时必填"
                    },
                    "rename_map": {
                        "type": "object",
                        "description": "重命名映射，键为旧名称，值为新名称。action 为 rename 时必填。例如: {\"Fp1\":\"E1\", \"Fp2\":\"E2\"}"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="eeglab_clean_line_noise",
            description="专用工频噪声去除工具。使用 clean_rawdata 插件的 pop_cleanline 函数。"
                        "比简单陷波滤波更精确，可自适应估计和去除工频及其谐波。"
                        "需要 clean_rawdata 插件。专业建议: 如果数据有明显的 50/60Hz 工频干扰，优先使用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "line_freq": {
                        "type": "number",
                        "default": 50,
                        "description": "工频频率(Hz)。50(中国/欧洲)或60(美国)"
                    },
                    "bandwidth": {
                        "type": "number",
                        "default": 2,
                        "description": "陷波带宽(Hz)"
                    },
                    "tau": {
                        "type": "number",
                        "default": 100,
                        "description": "平滑参数 tau"
                    },
                    "winsize": {
                        "type": "number",
                        "default": 4,
                        "description": "窗口大小(秒)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_clean_rawdata",
            description="ASR (Artifact Subspace Reconstruction) 伪迹去除。使用 clean_rawdata 插件。"
                        "可自动检测和修复坏通道、去除高幅伪迹。"
                        "专业建议: 在连续数据上运行（分段前）; ICA 前使用可提高 ICA 质量; "
                        "burst_criterion: 5=激进, 20=保守, 40=温和。需要 clean_rawdata 插件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "flatline_criterion": {
                        "type": "number",
                        "default": 5,
                        "description": "平线检测阈值(秒)。通道信号标准差接近0超过此时长则标记为坏通道"
                    },
                    "channel_criterion": {
                        "type": "number",
                        "default": 0.8,
                        "description": "坏通道检测阈值(相关系数)。低于此值的通道被标记为坏通道"
                    },
                    "line_noise_criterion": {
                        "type": "number",
                        "default": 4,
                        "description": "工频噪声检测阈值(Z分数)"
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "突发伪迹检测阈值(Z分数)。5=激进, 20=保守, 40=温和"
                    },
                    "window_criterion": {
                        "type": "number",
                        "default": 0.25,
                        "description": "坏时间段检测阈值(比例)。超过此比例的窗口被标记为坏段"
                    }
                },
                "required": []
            }
        ),

        # ===== 第 3 类：ICA 与伪迹处理 =====
        Tool(
            name="eeglab_run_ica",
            description="对 EEG 数据运行 ICA（独立成分分析）分解。ICA 用于分离脑源信号和伪迹成分（眼电、肌电、心电等）。"
                        "专业建议: ICA 前建议高通 1Hz 滤波; 不要在 ICA 前做基线校正; "
                        "平均参考会使秩减 1，需设置 pca=nchan-1; "
                        "runica 和 picard 是 EEGLAB 内置算法; fastica 需要单独插件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "runica",
                        "description": "ICA 算法: runica(Infomax,默认稳定), picard(速度与精度平衡,推荐)"
                    },
                    "pca_components": {
                        "type": "integer",
                        "description": "PCA 降维后的成分数。不填则等于通道数。平均参考后建议设为 nchan-1"
                    },
                    "extended": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否使用扩展 Infomax(可分离超高斯和亚高斯分布)。推荐开启以更好地分离肌电伪迹"
                    },
                    "max_steps": {
                        "type": "integer",
                        "default": 512,
                        "description": "最大迭代步数。默认512，大数据集可增加到1000-2000"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_classify_ica",
            description="使用 ICLabel 自动分类 ICA 成分。ICLabel 是基于深度学习的自动分类工具，"
                        "将每个 IC 成分分为: Brain(脑源), Muscle(肌电), Eye(眼电), Heart(心电), "
                        "Line_Noise(工频), Channel_Noise(通道噪声), Other(其他) 七类。"
                        "分类结果包含每个成分属于各类别的概率。需先运行 ICA 分解。需要 ICLabel 插件。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="eeglab_flag_components",
            description="根据 ICLabel 分类概率标记 ICA 成分。可设置各类别的概率阈值来决定哪些成分应被标记为伪迹。"
                        "专业建议: 常用策略是标记 Brain 概率低于 0.2 的成分，或标记 Muscle/Eye 概率高于 0.8 的成分。",
            inputSchema={
                "type": "object",
                "properties": {
                    "brain_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Brain 类别概率范围 [min, max]，超出此范围标记。例如: [0, 0.2] 标记 Brain<20% 的"
                    },
                    "muscle_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Muscle 类别概率范围 [min, max]，在此范围内标记。例如: [0.8, 1] 标记 Muscle>80%"
                    },
                    "eye_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Eye 类别概率范围 [min, max]。例如: [0.8, 1]"
                    },
                    "heart_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Heart 类别概率范围 [min, max]。例如: [0.8, 1]"
                    },
                    "line_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Line_Noise 类别概率范围 [min, max]"
                    },
                    "channel_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Channel_Noise 类别概率范围 [min, max]"
                    },
                    "other_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "Other 类别概率范围 [min, max]"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_remove_components",
            description="移除指定的 ICA 伪迹成分并重建 EEG 数据。根据 ICLabel 分类结果或手动选择，"
                        "移除非脑源成分（如眼电、肌电、心电、工频噪声等）。"
                        "这是 ICA 去伪迹的核心步骤。建议先运行 eeglab_classify_ica 查看分类结果再决定移除哪些成分。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要移除的 IC 成分索引列表(从1开始)。例如: [2, 5, 7, 10]"
                    },
                    "auto_remove_brain_threshold": {
                        "type": "number",
                        "description": "自动移除模式: Brain 类别概率低于此阈值的成分将被移除。例如: 0.3 表示保留 Brain 概率>=30% 的成分。不填则使用手动 component_indices"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_reject_epochs",
            description="试次拒绝。根据阈值或联合概率方法拒绝包含伪迹的试次。"
                        "专业建议: 分段后使用; 阈值应根据数据幅度设置（通常 ±100μV）; "
                        "联合概率方法可检测多通道联合异常。",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["threshold", "joint_probability"],
                        "default": "threshold",
                        "description": "拒绝方法: threshold(阈值), joint_probability(联合概率)"
                    },
                    "threshold": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [-100, 100],
                        "description": "阈值范围[下限μV, 上限μV]。method 为 threshold 时使用"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "检测的通道列表。留空则使用所有通道"
                    },
                    "jp_threshold": {
                        "type": "number",
                        "default": 3,
                        "description": "联合概率的 Z 分数阈值。method 为 joint_probability 时使用"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_get_events",
            description="获取当前 EEG 数据集的事件信息。查看可用事件类型和数量。"
                        "用于了解数据中有哪些标记事件，以便后续分段和分析。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # ===== 第 4 类：分段与 ERP =====
        Tool(
            name="eeglab_epoch",
            description="对连续 EEG 数据进行分段和基线校正。根据事件类型将数据切分为试次。"
                        "分段是 ERP 分析的必要步骤。专业建议: 常用时间窗 [-200, 800]ms (P300), "
                        "[-200, 500]ms (N170); 基线校正使用刺激前时间段消除直流偏移; "
                        "基线窗口通常与刺激前窗口相同。",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "用于分段的事件类型列表。例如: ['target', 'standard']。留空则使用所有事件"
                    },
                    "pre_stimulus": {
                        "type": "number",
                        "default": -0.2,
                        "description": "刺激前时间窗口(秒)。例如: -0.2 表示刺激前200ms"
                    },
                    "post_stimulus": {
                        "type": "number",
                        "default": 0.8,
                        "description": "刺激后时间窗口(秒)。例如: 0.8 表示刺激后800ms"
                    },
                    "baseline_start": {
                        "type": "number",
                        "default": -0.2,
                        "description": "基线校正起始时间(秒)。通常与 pre_stimulus 相同"
                    },
                    "baseline_end": {
                        "type": "number",
                        "default": 0,
                        "description": "基线校正结束时间(秒)。通常为0(刺激 onset)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_erp_analysis",
            description="ERP（事件相关电位）分析。计算各条件的平均 ERP 波形，支持按条件分组、"
                        "选择通道、指定时间窗口。输出各条件在各通道的 ERP 均值、峰值及潜伏期。"
                        "专业建议: 常用 ERP 成分: N1(80-150ms), P2(150-280ms), "
                        "N170(140-200ms,颞枕区), P300(250-500ms,中央顶区), N400(300-500ms,中央区)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Fz', 'Cz', 'Pz']。留空则分析所有通道"
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "分析的时间窗口[起始ms, 结束ms]。例如: [250, 500] 分析 P300 成分"
                    },
                    "peak_detection": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否在指定时间窗口内检测峰值(最大正波和最大负波)"
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组分析。留空则分析所有试次的平均"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_sort_epochs",
            description="按条件排序试次。将试次按事件类型分组排序，便于后续分组分析。"
                        "专业建议: 分段后使用; 排序后可用 eeglab_erp_analysis 按条件分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "description": "排序依据的事件类型字段名。例如: 'type'"
                    }
                },
                "required": ["sort_by"]
            }
        ),
        Tool(
            name="eeglab_average_erp",
            description="ERP 平均。按条件分组计算 ERP 平均波形。"
                        "专业建议: 通常在分段和基线校正后使用; "
                        "可按事件类型分组计算各条件的平均 ERP。",
            inputSchema={
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组。留空则计算所有试次的总体平均"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "计算的通道列表。留空则计算所有通道"
                    }
                },
                "required": []
            }
        ),

        # ===== 第 5 类：频域与时频 =====
        Tool(
            name="eeglab_spectral",
            description="频谱/功率谱密度(PSD)分析。使用 Welch 方法计算各通道的功率谱密度。"
                        "输出各频段(Delta/Theta/Alpha/Beta/Gamma)的绝对功率和相对功率。"
                        "专业建议: 频段定义: Delta(0.5-4Hz), Theta(4-8Hz), Alpha(8-13Hz), "
                        "Beta(13-30Hz), Gamma(30-80Hz); 静息态分析常用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Oz', 'Pz']。留空则分析所有通道"
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [0.5, 100],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [0.5, 100]"
                    },
                    "band_power": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否计算各频段(Delta/Theta/Alpha/Beta/Gamma)的功率"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_timefreq",
            description="时频分析。计算 EEG 信号的事件相关谱扰动(ERSP)和跨试次相干性(ITC)。"
                        "支持 Morlet 小波变换。"
                        "ERSP 反映各频段能量随时间的变化; ITC 反映各频段相位锁定程度。"
                        "专业建议: 频率范围 3-80Hz; 周期数 3-10(低频到高频线性增长); "
                        "需要分段数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Cz', 'Pz']。留空则分析所有通道"
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [3, 80],
                        "description": "频率范围[最低Hz, 最高Hz]。例如: [3, 80]"
                    },
                    "cycles": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 3,
                        "default": [3, 10],
                        "description": "小波周期数。2个值: [起始, 结束]; 3个值: [起始, 增长率, 结束]。默认: [3, 10]"
                    },
                    "baseline": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [-200, 0],
                        "description": "基线窗口[起始ms, 结束ms]。默认: [-200, 0] 刺激前200ms"
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["ersp", "itc", "both"],
                        "default": "both",
                        "description": "输出类型: ersp(仅功率), itc(仅相位一致性), both(两者)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_connectivity",
            description="功能连接分析。计算通道间的相干性(Coherence)和相位锁定值(PLV)。"
                        "专业建议: 相干性反映两个信号在不同频率上的线性关系; "
                        "PLV 反映相位同步程度; 常用于静息态脑网络分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。留空则分析所有通道"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["coherence", "plv"],
                        "default": "coherence",
                        "description": "连接性度量: coherence(相干性), plv(相位锁定值)"
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [8, 13],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [8, 13] Alpha 频段"
                    }
                },
                "required": []
            }
        ),

        # ===== 第 6 类：可视化 =====
        Tool(
            name="eeglab_topoplot",
            description="绘制头皮地形图(Topography)。将 EEG 信号在头皮上的分布以等高线图形式展示。"
                        "支持绘制特定时间点或时间窗的平均电位分布。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_point": {
                        "type": "number",
                        "description": "绘制的时间点(ms)。例如: 300 表示刺激后300ms。与 time_window 二选一"
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "description": "绘制的时间窗平均值[起始ms, 结束ms]。例如: [250, 350] 表示 P300 时间窗。与 time_point 二选一"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "绘制的通道列表。留空则使用所有通道"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径。例如: C:/results/topo_300ms.png"
                    },
                    "title": {
                        "type": "string",
                        "description": "图形标题"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="eeglab_plot_erp",
            description="绘制 ERP 波形图。显示指定通道的 ERP 平均波形。"
                        "支持按条件分组绘制、添加置信区间。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "绘制的通道列表。例如: ['Fz', 'Cz', 'Pz']"
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组绘制。留空则绘制所有试次平均"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径"
                    },
                    "title": {
                        "type": "string",
                        "description": "图形标题"
                    }
                },
                "required": ["channels", "output_path"]
            }
        ),
        Tool(
            name="eeglab_plot_timefreq",
            description="绘制时频图。显示指定通道的 ERSP 和/或 ITC 时频图。"
                        "需要先运行 eeglab_timefreq 获取时频数据。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "绘制的通道标签。例如: 'Cz'"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径"
                    },
                    "plot_ersp": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否绘制 ERSP 图"
                    },
                    "plot_itc": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否绘制 ITC 图"
                    },
                    "title": {
                        "type": "string",
                        "description": "图形标题"
                    }
                },
                "required": ["channel", "output_path"]
            }
        ),
        Tool(
            name="eeglab_plot_components",
            description="绘制 ICA 成分图。显示每个 IC 成分的头皮拓扑图和功率谱。"
                        "用于人工检查和判断 ICA 成分性质。图形保存为 PNG 文件。"
                        "专业建议: 需先运行 ICA 分解; 可结合 ICLabel 分类结果判断成分性质。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要绘制的 IC 成分索引列表(从1开始)。留空则绘制前 10 个"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径"
                    },
                    "title": {
                        "type": "string",
                        "description": "图形标题"
                    }
                },
                "required": ["output_path"]
            }
        ),

        # ===== 第 7 类：源定位 =====
        Tool(
            name="eeglab_source_localization",
            description="源定位分析（偶极子拟合）。使用 EEGLAB 内置的 Dipfit 工具对 ICA 成分进行偶极子拟合，"
                        "估计脑内信号源的位置。需要先运行 ICA 分解。"
                        "输出偶极子的 MNI 坐标、残差方差等。专业建议: 拟合前需确保通道位置正确; "
                        "残差方差 < 15% 表示拟合良好。需要 Dipfit 插件（EEGLAB 内置）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要拟合的 IC 成分索引列表。留空则拟合所有成分"
                    },
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "头模型类型: bem(边界元模型,推荐) 或 spherical(球模型,快速)"
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "模板脑: mni(MNI305,默认) 或 colin27(Colin27 高分辨率)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_source_settings",
            description="Dipfit 模型设置。配置头模型、模板脑、通道位置文件等参数。"
                        "专业建议: 在运行源定位前应先设置正确的参数; "
                        "BEM 模型更精确但计算更慢; 球模型快速但精度较低。",
            inputSchema={
                "type": "object",
                "properties": {
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "头模型类型: bem(边界元模型) 或 spherical(球模型)"
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "模板脑: mni(MNI305) 或 colin27(Colin27)"
                    },
                    "chanfile": {
                        "type": "string",
                        "description": "通道位置文件路径。留空使用默认"
                    },
                    "mrifile": {
                        "type": "string",
                        "description": "MRI 模板文件路径。留空使用默认"
                    }
                },
                "required": []
            }
        ),

        # ===== 第 8 类：组分析与 Pipeline =====
        Tool(
            name="eeglab_study_create",
            description="创建 EEGLAB STUDY 用于组级别分析。可从 BIDS 目录或多个 .set 文件创建。"
                        "专业建议: STUDY 是 EEGLAB 进行组级别分析的基础; "
                        "创建后需定义实验设计才能进行统计检验。",
            inputSchema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "BIDS 数据集根目录路径。与 dataset_paths 二选一"
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY 名称"
                    },
                    "dataset_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "EEG 数据文件路径列表。与 bids_path 二选一"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_study_design",
            description="定义 STUDY 实验设计。设置自变量及其水平，用于后续统计检验。"
                        "专业建议: 必须在统计检验前定义设计; "
                        "可定义多个自变量（如组别×条件）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "design_name": {
                        "type": "string",
                        "default": "Design1",
                        "description": "设计名称"
                    },
                    "variable_name": {
                        "type": "string",
                        "default": "condition",
                        "description": "自变量名称。例如: 'condition', 'group'"
                    },
                    "variable_values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["target", "standard"],
                        "description": "自变量水平。例如: ['control', 'patient'] 或 ['target', 'standard']"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_study_statistics",
            description="STUDY 统计检验。使用聚类置换检验进行组级别统计推断。"
                        "专业建议: 聚类置换检验可有效控制多重比较; "
                        "常用阈值: p < 0.05, 聚类阈值 FDR 或 FWE 校正。",
            inputSchema={
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "enum": ["erp", "spectrum", "ersp"],
                        "default": "erp",
                        "description": "统计检验的测量类型: erp(ERP波形), spectrum(频谱), ersp(时频)"
                    },
                    "alpha": {
                        "type": "number",
                        "default": 0.05,
                        "description": "显著性水平。默认: 0.05"
                    },
                    "correction": {
                        "type": "string",
                        "enum": ["fdr", "bonferroni", "cluster", "none"],
                        "default": "fdr",
                        "description": "多重比较校正方法: fdr(FDR), bonferroni(Bonferroni), cluster(聚类), none(无校正)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="eeglab_pipeline",
            description="一键流程生成。根据分析类型自动生成完整的预处理和分析流程。"
                        "支持 ERP 分析流程、静息态分析流程和时频分析流程。"
                        "专业建议: ERP 流程: 滤波→ASR→重参考→ICA→ICLabel→去伪迹→插值→分段→基线→保存; "
                        "静息态流程: 滤波→ASR→重参考→ICA→ICLabel→去伪迹→频谱分析→保存。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["erp", "resting", "timefreq"],
                        "description": "流程类型: erp(ERP分析), resting(静息态), timefreq(时频分析)"
                    },
                    "data_path": {
                        "type": "string",
                        "description": "输入数据文件路径"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录路径。留空则使用工作目录"
                    },
                    "highpass": {
                        "type": "number",
                        "default": 1.0,
                        "description": "高通滤波截止频率(Hz)。默认: 1.0 (ICA 前推荐)"
                    },
                    "lowpass": {
                        "type": "number",
                        "default": 40.0,
                        "description": "低通滤波截止频率(Hz)。默认: 40.0"
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分段用的事件类型。pipeline_type 为 erp 或 timefreq 时使用"
                    },
                    "epoch_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [-0.2, 0.8],
                        "description": "分段时间窗[起始秒, 结束秒]。默认: [-0.2, 0.8]"
                    },
                    "baseline_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2, "maxItems": 2,
                        "default": [-200, 0],
                        "description": "基线校正窗口[起始ms, 结束ms]。默认: [-200, 0]"
                    },
                    "ica_algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "picard",
                        "description": "ICA 算法。默认: picard"
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "ASR 突发伪迹检测阈值。5=激进, 20=保守, 40=温和"
                    }
                },
                "required": ["pipeline_type", "data_path"]
            }
        ),
    ]
    return annotate_tools(tools + workflow_tools())


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 EEGLAB MCP 工具。"""
    tools = _tool_definitions()
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
    handlers = {
        # 第 1 类：数据管理
        "eeglab_init": _eeglab_init,
        "eeglab_load_data": _eeglab_load_data,
        "eeglab_save_data": _eeglab_save_data,
        "eeglab_import_bids": _eeglab_import_bids,
        "eeglab_info": _eeglab_info,
        "eeglab_history": _eeglab_history,
        # 第 2 类：预处理
        "eeglab_filter": _eeglab_filter,
        "eeglab_resample": _eeglab_resample,
        "eeglab_reref": _eeglab_reref,
        "eeglab_select_channels": _eeglab_select_channels,
        "eeglab_interpolate_channels": _eeglab_interpolate_channels,
        "eeglab_edit_channels": _eeglab_edit_channels,
        "eeglab_clean_line_noise": _eeglab_clean_line_noise,
        "eeglab_clean_rawdata": _eeglab_clean_rawdata,
        # 第 3 类：ICA 与伪迹处理
        "eeglab_run_ica": _eeglab_run_ica,
        "eeglab_classify_ica": _eeglab_classify_ica,
        "eeglab_flag_components": _eeglab_flag_components,
        "eeglab_remove_components": _eeglab_remove_components,
        "eeglab_reject_epochs": _eeglab_reject_epochs,
        "eeglab_get_events": _eeglab_get_events,
        # 第 4 类：分段与 ERP
        "eeglab_epoch": _eeglab_epoch,
        "eeglab_erp_analysis": _eeglab_erp_analysis,
        "eeglab_sort_epochs": _eeglab_sort_epochs,
        "eeglab_average_erp": _eeglab_average_erp,
        # 第 5 类：频域与时频
        "eeglab_spectral": _eeglab_spectral,
        "eeglab_timefreq": _eeglab_timefreq,
        "eeglab_connectivity": _eeglab_connectivity,
        # 第 6 类：可视化
        "eeglab_topoplot": _eeglab_topoplot,
        "eeglab_plot_erp": _eeglab_plot_erp,
        "eeglab_plot_timefreq": _eeglab_plot_timefreq,
        "eeglab_plot_components": _eeglab_plot_components,
        # 第 7 类：源定位
        "eeglab_source_localization": _eeglab_source_localization,
        "eeglab_source_settings": _eeglab_source_settings,
        # 第 8 类：组分析与 Pipeline
        "eeglab_study_create": _eeglab_study_create,
        "eeglab_study_design": _eeglab_study_design,
        "eeglab_study_statistics": _eeglab_study_statistics,
        "eeglab_pipeline": _eeglab_pipeline,
        # 高层科研工作流
        "eeglab_qc_report": _eeglab_qc_report,
        "eeglab_erp_light_workflow": _eeglab_erp_light_workflow,
        "eeglab_workflow_recommend": _eeglab_workflow_recommend,
    }

    handler = handlers.get(name)
    if not handler:
        return _error_response(
            "unknown_tool",
            f"未知工具: {name}",
            next_step="调用 tools/list 查看可用的 40 个 eeglab_* 工具。",
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

    tools = _tool_definitions()
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
        return _normalize_tool_result(name, await handler(arguments))
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


# ===========================================================================
# 工具实现函数
# ===========================================================================

# ---------------------------------------------------------------------------
# 第 1 类：数据管理
# ---------------------------------------------------------------------------

async def _eeglab_init(args: dict) -> list[TextContent]:
    """初始化 EEGLAB 环境。"""
    eeglab_path = args.get("eeglab_path", "")
    if eeglab_path:
        cfg.EEGLAB_PATH = eeglab_path
        os.environ["EEGLAB_PATH"] = eeglab_path
        matlab.eeglab_initialized = False

    init_code = _eeglab_init_code()
    code = f"""
{init_code}
try
    v = eeg_getversion;
    result.version = v;
    result.eeglabpath = which('eeglab');
catch
    result.version = 'unknown';
    result.eeglabpath = 'not found';
end
"""

    result = await matlab.execute(code)
    is_success = result.get("status") == "success"
    matlab.eeglab_initialized = is_success

    output = {
        "status": result.get("status", "unknown"),
        "message": "EEGLAB 初始化成功" if is_success else "EEGLAB 初始化失败",
        "eeglab_version": result.get("version", "unknown"),
        "eeglab_path": result.get("eeglabpath", "unknown"),
        "custom_path": eeglab_path or cfg.EEGLAB_PATH or "未设置",
    }
    if result.get("status") == "error":
        output["error"] = result.get("error", "")

    return [TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]


async def _eeglab_load_data(args: dict) -> list[TextContent]:
    """加载 EEG 数据文件。"""
    filepath = args["filepath"]
    filename = args.get("filename", "")
    filepath_lit = matlab_string(filepath)
    filename_lit = matlab_string(filename)

    if filename:
        load_code = f"""
[fpath, ~, ~] = fileparts({filepath_lit});
EEG = pop_loadset('filename', {filename_lit}, 'filepath', fpath);
"""
    else:
        load_code = f"""
[fpath, fname, fext] = fileparts({filepath_lit});
if strcmp(fext, '.edf') || strcmp(fext, '.bdf')
    EEG = pop_biosig({filepath_lit});
elseif strcmp(fext, '.vhdr')
    EEG = pop_loadbv(fpath, [fname fext]);
elseif strcmp(fext, '.cnt')
    EEG = pop_loadcnt({filepath_lit});
else
    EEG = pop_loadset('filename', [fname fext], 'filepath', fpath);
end
"""

    code = f"""
{_maybe_init()}
{load_code}
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
result.xmin = EEG.xmin;
result.xmax = EEG.xmax;
result.duration_sec = EEG.pnts / EEG.srate;
result.setname = EEG.setname;
result.channel_labels = {{EEG.chanlocs.labels}};
if isfield(EEG, 'event') && ~isempty(EEG.event)
    event_types = unique({{EEG.event.type}});
    result.event_types = event_types;
    result.num_events = length(EEG.event);
else
    result.event_types = {{}};
    result.num_events = 0;
end
"""

    result = await matlab.execute(code)
    is_error = result.get("status") == "error"
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_save_data(args: dict) -> list[TextContent]:
    """保存 EEG 数据到文件。"""
    filepath = args["filepath"]
    filename = args.get("filename", "")
    filepath_lit = matlab_string(filepath)
    filename_lit = matlab_string(filename)

    if filename:
        save_code = f"""
[fpath, ~, ~] = fileparts({filepath_lit});
EEG = pop_saveset(EEG, 'filename', {filename_lit}, 'filepath', fpath);
result.saved_path = fullfile(fpath, {filename_lit});
"""
    else:
        save_code = f"""
[fpath, fname, fext] = fileparts({filepath_lit});
EEG = pop_saveset(EEG, 'filename', [fname fext], 'filepath', fpath);
result.saved_path = {filepath_lit};
"""

    code = f"""
{_maybe_init()}
{save_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_import_bids(args: dict) -> list[TextContent]:
    """导入 BIDS 格式数据集。"""
    bids_path = args["bids_path"]
    study_name = args.get("study_name", "MyStudy")
    bids_path_lit = matlab_string(bids_path)
    study_name_lit = matlab_string(study_name)

    code = f"""
{_maybe_init()}
[STUDY, ALLEEG] = pop_importbids({bids_path_lit}, 'studyName', {study_name_lit}, 'bidsevent', 'on', 'bidschanloc', 'on');
result.study_name = {study_name_lit};
result.num_datasets = length(ALLEEG);
result.subjects = {{STUDY.subject}};
EEG = ALLEEG(1);
result.first_dataset.nbchan = EEG.nbchan;
result.first_dataset.srate = EEG.srate;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_info(args: dict) -> list[TextContent]:
    """获取当前 EEG 数据集的详细信息。"""
    include_ch = args.get("include_channels", True)
    include_ev = args.get("include_events", True)
    include_ica = args.get("include_ica", True)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG)
    result.status = 'error';
    result.error = '当前没有加载 EEG 数据，请先调用 eeglab_load_data';
else
    result.nbchan = EEG.nbchan;
    result.srate = EEG.srate;
    result.pnts = EEG.pnts;
    result.trials = EEG.trials;
    result.xmin = EEG.xmin;
    result.xmax = EEG.xmax;
    result.duration_sec = EEG.pnts / EEG.srate;
    result.total_duration_min = EEG.pnts / EEG.srate / 60;
    result.setname = EEG.setname;
    result.filename = EEG.filename;
    result.filepath = EEG.filepath;
    result.saved = EEG.saved;
    result.recording = struct();
    result.recording.sampling_rate_hz = EEG.srate;
    result.recording.channel_count = EEG.nbchan;
    result.recording.points_per_epoch = EEG.pnts;
    result.recording.trials = EEG.trials;
    result.recording.xmin_sec = EEG.xmin;
    result.recording.xmax_sec = EEG.xmax;
    result.recording.epoch_duration_sec = EEG.pnts / EEG.srate;
    result.recording.total_data_duration_sec = EEG.pnts * max(1, EEG.trials) / EEG.srate;
    if EEG.trials > 1
        result.recording.data_shape = 'epoched';
    else
        result.recording.data_shape = 'continuous_or_single_trial';
    end
    result.recording.setname = EEG.setname;
    result.recording.filename = EEG.filename;
    result.recording.filepath = EEG.filepath;
    result.recording.saved_state = EEG.saved;
    if isfield(EEG, 'comments') && ~isempty(EEG.comments)
        result.recording.comments = EEG.comments;
        result.recording.has_comments = true;
    else
        result.recording.comments = '';
        result.recording.has_comments = false;
    end
    if isfield(EEG, 'ref') && ~isempty(EEG.ref)
        result.recording.reference = EEG.ref;
    end
    if isfield(EEG, 'etc') && ~isempty(EEG.etc)
        result.recording.has_etc_metadata = true;
    else
        result.recording.has_etc_metadata = false;
    end
    result.processing_history_available = isfield(EEG, 'history') && ~isempty(EEG.history);
"""

    if include_ch:
        code += """
    if isfield(EEG, 'chanlocs') && ~isempty(EEG.chanlocs)
        if isfield(EEG.chanlocs, 'labels')
            result.channel_labels = {EEG.chanlocs.labels};
        else
            result.channel_labels = {};
        end
        located = false(1, length(EEG.chanlocs));
        for ci = 1:length(EEG.chanlocs)
            has_xyz = isfield(EEG.chanlocs, 'X') && ~isempty(EEG.chanlocs(ci).X) && ...
                isfield(EEG.chanlocs, 'Y') && ~isempty(EEG.chanlocs(ci).Y) && ...
                isfield(EEG.chanlocs, 'Z') && ~isempty(EEG.chanlocs(ci).Z);
            has_polar = isfield(EEG.chanlocs, 'theta') && ~isempty(EEG.chanlocs(ci).theta) && ...
                isfield(EEG.chanlocs, 'radius') && ~isempty(EEG.chanlocs(ci).radius);
            located(ci) = has_xyz || has_polar;
        end
        result.channels_with_locations = sum(located);
        result.channels_missing_locations = max(0, EEG.nbchan - sum(located));
        result.has_channel_locations = sum(located) == EEG.nbchan && EEG.nbchan > 0;
        result.channel_location_coverage = sum(located) / max(1, EEG.nbchan);
        if isfield(EEG.chanlocs, 'ref')
            refs = unique({EEG.chanlocs.ref});
            result.reference = refs;
        end
    else
        result.channel_labels = {};
        result.channels_with_locations = 0;
        result.channels_missing_locations = EEG.nbchan;
        result.has_channel_locations = false;
        result.channel_location_coverage = 0;
    end
"""

    if include_ev:
        code += """
    if isfield(EEG, 'event') && ~isempty(EEG.event)
        event_types = unique({EEG.event.type});
        result.event_types = event_types;
        result.num_events = length(EEG.event);
        if isfield(EEG.event, 'latency')
            latencies = [EEG.event.latency];
            result.event_latency_range_samples = [min(latencies), max(latencies)];
            result.event_latency_range_sec = [min(latencies) / EEG.srate, max(latencies) / EEG.srate];
        end
        result.has_urevent_links = isfield(EEG.event, 'urevent');
        if isfield(EEG, 'urevent') && ~isempty(EEG.urevent)
            result.num_urevents = length(EEG.urevent);
        else
            result.num_urevents = 0;
        end
        for i = 1:length(event_types)
            cnt = sum(strcmp({EEG.event.type}, event_types{i}));
            result.event_counts.(event_types{i}) = cnt;
        end
    else
        result.event_types = {};
        result.num_events = 0;
        result.num_urevents = 0;
        result.has_urevent_links = false;
    end
"""

    if include_ica:
        code += """
    if isfield(EEG, 'icaweights') && ~isempty(EEG.icaweights)
        result.ica_computed = true;
        result.ica_ncomponents = size(EEG.icaweights, 1);
        if isfield(EEG, 'etc') && isfield(EEG.etc, 'ic_classification') && isfield(EEG.etc.ic_classification, 'ICLabel')
            result.ica_classified = true;
            classifications = EEG.etc.ic_classification.ICLabel.classifications;
            labels = {'Brain', 'Muscle', 'Eye', 'Heart', 'Line_Noise', 'Channel_Noise', 'Other'};
            [~, max_idx] = max(classifications, [], 2);
            result.ica_classification_summary = struct();
            for i = 1:length(labels)
                cnt = sum(max_idx == i);
                result.ica_classification_summary.(labels{i}) = cnt;
            end
        else
            result.ica_classified = false;
        end
    else
        result.ica_computed = false;
        result.ica_ncomponents = 0;
        result.ica_classified = false;
    end
"""

    code += "end\n"

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_history(args: dict) -> list[TextContent]:
    """获取操作历史记录。"""
    code = f"""
{_maybe_init()}
if exist('EEG', 'var') && isstruct(EEG) && isfield(EEG, 'history') && ~isempty(EEG.history)
    result.history = EEG.history;
else
    result.history = '无操作历史记录';
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_qc_report(args: dict) -> Any:
    """Generate a workflow-shaped QC report from the current EEG dataset."""
    steps: list[dict[str, Any]] = []

    info = parse_tool_result(await _eeglab_info({}))
    steps.append({"name": "eeglab_info", "status": info.get("status", "success"), "code": info.get("code")})
    if info.get("status") == "error":
        return structured_payload(
            workflow_error(
                "eeglab_qc_report",
                "eeglab_info",
                info,
                parameters={},
                steps=steps,
            )
        )

    events = parse_tool_result(await _eeglab_get_events({}))
    steps.append({"name": "eeglab_get_events", "status": events.get("status", "success"), "code": events.get("code")})

    history = parse_tool_result(await _eeglab_history({}))
    steps.append({"name": "eeglab_history", "status": history.get("status", "success"), "code": history.get("code")})

    payload = qc_report_from_payloads(info, events, history)
    payload["steps"] = steps
    return structured_payload(payload)


async def _eeglab_workflow_recommend(args: dict) -> Any:
    """Recommend an EEG workflow without changing MATLAB state."""
    return structured_payload(recommend_workflow(args))


async def _eeglab_erp_light_workflow(args: dict) -> Any:
    """Run a lightweight ERP workflow and return structured progress/results."""
    steps: list[dict[str, Any]] = []
    try:
        parameters = light_erp_parameters(args)
    except ValueError as exc:
        payload = {
            "status": "error",
            "code": "invalid_output_path",
            "error": str(exc),
            "next_step": "Use output_dir for directories and output_filename for a simple .set filename.",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters={},
                steps=steps,
            )
        )

    data_path = Path(parameters["data_path"])
    output_path = Path(parameters["output_path"])
    if not data_path.exists():
        payload = {
            "status": "error",
            "code": "dataset_not_found",
            "error": f"数据文件不存在: {data_path}",
            "next_step": "传入存在的本地 EEG 数据文件绝对路径。",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters=parameters,
                steps=steps,
            )
        )
    if data_path.resolve() == output_path.resolve():
        payload = {
            "status": "error",
            "code": "refuse_overwrite_input",
            "error": "轻量 ERP workflow 不允许覆盖原始输入数据。",
            "next_step": "把 output_dir 或 output_filename 指向新的临时/结果路径。",
        }
        return structured_payload(
            workflow_error(
                "eeglab_erp_light_workflow",
                "preflight",
                payload,
                parameters=parameters,
                steps=steps,
            )
        )

    os.makedirs(parameters["output_dir"], exist_ok=True)

    async def run_step(step_name: str, fn: Any, step_args: dict[str, Any]) -> dict[str, Any]:
        result = parse_tool_result(await fn(step_args))
        steps.append({"name": step_name, "status": result.get("status", "success"), "code": result.get("code")})
        return result

    results: dict[str, dict[str, Any]] = {}
    preflight_steps = [
        ("eeglab_init", _eeglab_init, {}),
        ("eeglab_load_data", _eeglab_load_data, {"filepath": parameters["data_path"]}),
        ("eeglab_info", _eeglab_info, {}),
        ("eeglab_get_events", _eeglab_get_events, {}),
    ]

    for step_name, fn, step_args in preflight_steps:
        result = await run_step(step_name, fn, step_args)
        results[step_name] = result
        if result.get("status") == "error":
            return structured_payload(
                workflow_error(
                    "eeglab_erp_light_workflow",
                    step_name,
                    result,
                    parameters=parameters,
                    steps=steps,
                )
            )

    info_payload = results.get("eeglab_info", {})
    requested_channels = parameters.get("channels", [])
    available_channels = info_payload.get("channel_labels") or []
    if requested_channels and available_channels:
        effective_channels = [channel for channel in requested_channels if channel in available_channels]
        missing_channels = [channel for channel in requested_channels if channel not in available_channels]
        if not effective_channels:
            effective_channels = [available_channels[0]]
            parameters["channel_fallback"] = {
                "requested_channels": requested_channels,
                "effective_channels": effective_channels,
                "missing_channels": missing_channels,
                "reason": "requested channels were not present in the dataset; using the first available channel for smoke-test ERP summary",
            }
    else:
        effective_channels = requested_channels
        missing_channels = []
    parameters["effective_channels"] = effective_channels
    if missing_channels and "channel_fallback" not in parameters:
        parameters["channel_fallback"] = {
            "requested_channels": requested_channels,
            "effective_channels": effective_channels,
            "missing_channels": missing_channels,
            "reason": "some requested channels were not present and were skipped",
        }

    analysis_steps = [
        (
            "eeglab_filter",
            _eeglab_filter,
            {
                "filter_type": "bandpass",
                "low_cutoff": parameters["low_cutoff"],
                "high_cutoff": parameters["high_cutoff"],
            },
        ),
        (
            "eeglab_epoch",
            _eeglab_epoch,
            {
                "event_types": parameters["event_types"],
                "pre_stimulus": parameters["epoch_window"][0],
                "post_stimulus": parameters["epoch_window"][1],
                "baseline_start": parameters["baseline_window"][0] / 1000,
                "baseline_end": parameters["baseline_window"][1] / 1000,
            },
        ),
        (
            "eeglab_erp_analysis",
            _eeglab_erp_analysis,
            {
                "channels": effective_channels,
                "time_window": parameters["time_window"],
                "peak_detection": True,
                "conditions": parameters["event_types"],
            },
        ),
        ("eeglab_save_data", _eeglab_save_data, {"filepath": parameters["output_path"]}),
    ]

    for step_name, fn, step_args in analysis_steps:
        result = await run_step(step_name, fn, step_args)
        results[step_name] = result
        if result.get("status") == "error":
            return structured_payload(
                workflow_error(
                    "eeglab_erp_light_workflow",
                    step_name,
                    result,
                    parameters=parameters,
                    steps=steps,
                )
            )

    save_payload = results.get("eeglab_save_data", {})
    erp_payload = results.get("eeglab_erp_analysis", {})
    events_payload = results.get("eeglab_get_events", {})
    epoch_payload = results.get("eeglab_epoch", {})

    payload = workflow_success(
        "eeglab_erp_light_workflow",
        steps=steps,
        parameters=parameters,
        outputs={
            "processed_set": save_payload.get("saved_path", parameters["output_path"]),
            "processed_fdt": parameters["output_fdt_path"],
            "output_dir": parameters["output_dir"],
            "input_preserved": str(data_path.resolve()) != str(output_path.resolve()),
            "processed_set_exists": output_path.exists(),
            "processed_fdt_exists": Path(parameters["output_fdt_path"]).exists(),
        },
        summary={
            "nbchan": info_payload.get("nbchan"),
            "srate": info_payload.get("srate"),
            "pnts": info_payload.get("pnts"),
            "original_trials": info_payload.get("trials"),
            "num_events": events_payload.get("num_events"),
            "event_types": events_payload.get("event_types"),
            "epoched_trials": epoch_payload.get("trials"),
            "epoch_window_sec": parameters["epoch_window"],
            "baseline_window_ms": parameters["baseline_window"],
            "erp": erp_payload,
        },
    )
    return structured_payload(payload)


# ---------------------------------------------------------------------------
# 第 2 类：预处理
# ---------------------------------------------------------------------------

async def _eeglab_filter(args: dict) -> list[TextContent]:
    """滤波处理。"""
    filter_type = args["filter_type"]
    low_cutoff = args.get("low_cutoff")
    high_cutoff = args.get("high_cutoff")
    notch_freq = args.get("notch_freq")
    notch_harmonics = args.get("notch_harmonics", True)

    if filter_type == "notch":
        if not notch_freq:
            return _error_response(
                "missing_required_argument",
                "陷波滤波需要指定 notch_freq 参数",
                next_step="调用 eeglab_filter 时传入 notch_freq，例如 50 或 60。",
                details={"missing": ["notch_freq"]},
            )
        freqs = [notch_freq]
        if notch_harmonics:
            for h in range(2, 5):
                hf = notch_freq * h
                if hf < cfg.MATLAB_TIMEOUT:  # reasonable upper bound
                    freqs.append(hf)
        freqs_str = _arr(freqs)
        filter_code = f"""
EEG = pop_cleanline(EEG, 'linefreqs', {freqs_str}, 'bandwidth', 2, 'tau', 100, 'winsize', 4);
result.filter_type = 'notch';
result.notch_freqs = {freqs_str};
"""
    else:
        if filter_type == "bandpass" and (low_cutoff is None or high_cutoff is None):
            return _error_response("missing_required_argument", "带通滤波需要同时指定 low_cutoff 和 high_cutoff", next_step="补齐 low_cutoff 和 high_cutoff 后重试。")
        if filter_type == "highpass" and low_cutoff is None:
            return _error_response("missing_required_argument", "高通滤波需要指定 low_cutoff", next_step="补齐 low_cutoff 后重试。")
        if filter_type == "lowpass" and high_cutoff is None:
            return _error_response("missing_required_argument", "低通滤波需要指定 high_cutoff", next_step="补齐 high_cutoff 后重试。")

        # pop_eegfiltnew in current EEGLAB/firfilt uses locutoff/hicutoff.
        lo = low_cutoff if low_cutoff else "[]"
        hi = high_cutoff if high_cutoff else "[]"
        filter_code = f"""
EEG = pop_eegfiltnew(EEG, 'locutoff', {lo}, 'hicutoff', {hi});
result.filter_type = '{filter_type}';
result.low_cutoff = {lo};
result.high_cutoff = {hi};
"""

    code = f"""
{_maybe_init()}
{filter_code}
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_resample(args: dict) -> list[TextContent]:
    """重采样。"""
    new_srate = args["new_srate"]

    code = f"""
{_maybe_init()}
EEG = pop_resample(EEG, {new_srate});
result.new_srate = EEG.srate;
result.nbchan = EEG.nbchan;
result.pnts = EEG.pnts;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_reref(args: dict) -> list[TextContent]:
    """重参考。"""
    ref_type = args["ref_type"]
    ref_channel = args.get("ref_channel", "")
    ref_channel_lit = matlab_string(ref_channel)

    if ref_type == "average":
        reref_code = """
EEG = pop_reref(EEG, []);
result.ref_type = 'average';
result.ref_description = '所有通道平均参考（注意: 会使数据秩减1，ICA时需设pca=nchan-1）';
"""
    elif ref_type == "channel":
        if not ref_channel:
            return _error_response(
                "missing_required_argument",
                "单通道参考需要指定 ref_channel 参数",
                next_step="调用 eeglab_reref 时传入 ref_channel，例如 Cz。",
                details={"missing": ["ref_channel"]},
            )
        reref_code = f"""
EEG = pop_reref(EEG, {ref_channel_lit});
result.ref_type = 'channel';
result.ref_channel = {ref_channel_lit};
"""
    elif ref_type == "rest":
        reref_code = """
EEG = pop_reref(EEG, [], 'keepref', 'on');
result.ref_type = 'rest';
result.ref_description = 'REST 参考';
"""
    else:
        return _error_response("invalid_arguments", f"不支持的参考类型: {ref_type}", next_step="ref_type 只能是 average、channel 或 rest。")

    code = f"""
{_maybe_init()}
{reref_code}
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_select_channels(args: dict) -> list[TextContent]:
    """选择/排除通道。"""
    channels = args.get("channels", [])
    exclude_channels = args.get("exclude_channels", [])

    if channels:
        chan_str = _cell(channels)
        select_code = f"""
EEG = pop_select(EEG, 'channel', {chan_str});
result.action = 'select';
result.selected_channels = {chan_str};
"""
    elif exclude_channels:
        excl_str = _cell(exclude_channels)
        select_code = f"""
EEG = pop_select(EEG, 'nochannel', {excl_str});
result.action = 'exclude';
result.excluded_channels = {excl_str};
"""
    else:
        return _error_response("missing_required_argument", "请指定 channels 或 exclude_channels", next_step="传入要保留或排除的通道列表后重试。")

    code = f"""
{_maybe_init()}
{select_code}
result.nbchan = EEG.nbchan;
result.channel_labels = {{EEG.chanlocs.labels}};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_interpolate_channels(args: dict) -> list[TextContent]:
    """通道插值。"""
    ref_chanlocs = args.get("ref_chanlocs", "")
    method = args.get("method", "spherical")
    ref_chanlocs_lit = matlab_string(ref_chanlocs)
    method_lit = matlab_string(method)

    if ref_chanlocs == "urchanlocs":
        interp_code = f"""
EEG = pop_interp(EEG, EEG.urchanlocs, {method_lit});
result.action = 'interpolate_urchanlocs';
"""
    elif ref_chanlocs:
        interp_code = f"""
EEG = pop_interp(EEG, {ref_chanlocs_lit}, {method_lit});
result.action = 'interpolate_from_file';
result.ref_chanlocs = {ref_chanlocs_lit};
"""
    else:
        interp_code = f"""
EEG = pop_interp(EEG, [], {method_lit});
result.action = 'interpolate_current';
"""

    code = f"""
{_maybe_init()}
{interp_code}
result.method = {method_lit};
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_edit_channels(args: dict) -> list[TextContent]:
    """编辑通道信息。"""
    action = args["action"]

    if action == "load_loc":
        loc_file = args.get("loc_file", "")
        if not loc_file:
            return _error_response(
                "missing_required_argument",
                "load_loc 操作需要指定 loc_file 参数",
                next_step="传入 .loc/.ced 通道位置文件路径后重试。",
                details={"missing": ["loc_file"]},
            )
        loc_file_lit = matlab_string(loc_file)
        edit_code = f"""
EEG = pop_chanedit(EEG, 'load', {{{loc_file_lit}}});
result.action = 'load_loc';
result.loc_file = {loc_file_lit};
"""
    elif action == "rename":
        rename_map = args.get("rename_map", {})
        if not rename_map:
            return _error_response(
                "missing_required_argument",
                "rename 操作需要指定 rename_map 参数",
                next_step="传入旧通道名到新通道名的对象映射后重试。",
                details={"missing": ["rename_map"]},
            )
        rename_cmds = ""
        for old_name, new_name in rename_map.items():
            rename_cmds += f"EEG = pop_chanedit(EEG, 'changename', {{{matlab_string(old_name)}, {matlab_string(new_name)}}});\n"
        edit_code = f"""
{rename_cmds}
result.action = 'rename';
result.rename_map = struct();
"""
        for old_name, new_name in rename_map.items():
            edit_code += f"result.rename_map.({matlab_string(old_name)}) = {matlab_string(new_name)};\n"
    else:
        return _error_response("invalid_arguments", f"不支持的操作: {action}", next_step="action 只能是 load_loc 或 rename。")

    code = f"""
{_maybe_init()}
{edit_code}
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_clean_line_noise(args: dict) -> list[TextContent]:
    """专用工频噪声去除。"""
    line_freq = args.get("line_freq", 50)
    bandwidth = args.get("bandwidth", 2)
    tau = args.get("tau", 100)
    winsize = args.get("winsize", 4)

    code = f"""
{_maybe_init()}
EEG = pop_cleanline(EEG, 'linefreqs', [{line_freq}], 'bandwidth', {bandwidth}, 'tau', {tau}, 'winsize', {winsize});
result.line_freq = {line_freq};
result.bandwidth = {bandwidth};
result.tau = {tau};
result.winsize = {winsize};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_clean_rawdata(args: dict) -> list[TextContent]:
    """ASR 伪迹去除。"""
    flatline = args.get("flatline_criterion", 5)
    channel_crit = args.get("channel_criterion", 0.8)
    line_noise_crit = args.get("line_noise_criterion", 4)
    burst_crit = args.get("burst_criterion", 20)
    window_crit = args.get("window_criterion", 0.25)

    code = f"""
{_maybe_init()}
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion', {flatline}, 'ChannelCriterion', {channel_crit}, 'LineNoiseCriterion', {line_noise_crit}, 'Highpass', [0.25 0.75], 'BurstCriterion', {burst_crit}, 'BurstRejection', 'on', 'WindowCriterion', {window_crit}, 'Distance', 'Euclidian', 'WindowCriterionTolerances', [-Inf 7]);
result.flatline_criterion = {flatline};
result.channel_criterion = {channel_crit};
result.line_noise_criterion = {line_noise_crit};
result.burst_criterion = {burst_crit};
result.window_criterion = {window_crit};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 3 类：ICA 与伪迹处理
# ---------------------------------------------------------------------------

async def _eeglab_run_ica(args: dict) -> list[TextContent]:
    """运行 ICA 分解。"""
    algorithm = args.get("algorithm", "runica")
    pca = args.get("pca_components")
    extended = args.get("extended", True)
    max_steps = args.get("max_steps", 512)

    pca_str = f", 'pca', {pca}" if pca else ""
    ext_val = 1 if extended else 0

    ica_algorithms = {
        "runica": f"EEG = pop_runica(EEG, 'extended', {ext_val}, 'maxsteps', {max_steps}{pca_str});",
        "picard": f"EEG = pop_runica(EEG, 'icatype', 'picard', 'extended', {ext_val}, 'maxsteps', {max_steps}{pca_str});",
    }

    ica_code = ica_algorithms.get(algorithm)
    if not ica_code:
        return _error_response("invalid_arguments", f"不支持的 ICA 算法: {algorithm}。仅支持 runica 和 picard", next_step="algorithm 只能是 runica 或 picard。")

    code = f"""
{_maybe_init()}
{ica_code}
result.algorithm = '{algorithm}';
result.ncomponents = size(EEG.icaweights, 1);
result.extended = {str(extended).lower()};
result.max_steps = {max_steps};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_classify_ica(args: dict) -> list[TextContent]:
    """ICLabel 自动分类。"""
    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    EEG = pop_iclabel(EEG);
    classifications = EEG.etc.ic_classification.ICLabel.classifications;
    labels = {{'Brain', 'Muscle', 'Eye', 'Heart', 'Line_Noise', 'Channel_Noise', 'Other'}};
    n_components = size(classifications, 1);
    result.n_components = n_components;
    result.labels = labels;
    result.classifications = struct();
    for i = 1:n_components
        probs = classifications(i,:);
        [max_prob, max_idx] = max(probs);
        comp_name = ['comp_' num2str(i)];
        result.classifications.(comp_name).predicted_class = labels{{max_idx}};
        result.classifications.(comp_name).max_probability = max_prob;
        for j = 1:length(labels)
            result.classifications.(comp_name).(labels{{j}}) = probs(j);
        end
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_flag_components(args: dict) -> list[TextContent]:
    """标记 ICA 成分。"""
    # 7 个类别: Brain, Muscle, Eye, Heart, Line_Noise, Channel_Noise, Other
    categories = ["brain", "muscle", "eye", "heart", "line_noise", "channel_noise", "other"]
    param_names = ["brain_range", "muscle_range", "eye_range", "heart_range",
                   "line_noise_range", "channel_noise_range", "other_range"]

    rows = []
    for param in param_names:
        r = args.get(param)
        if r and len(r) == 2:
            rows.append(f"{r[0]} {r[1]}")
        else:
            rows.append("NaN NaN")

    matrix_str = "; ".join(rows)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    if ~isfield(EEG, 'etc') || ~isfield(EEG.etc, 'ic_classification') || ~isfield(EEG.etc.ic_classification, 'ICLabel')
        EEG = pop_iclabel(EEG);
    end
    EEG = pop_icflag(EEG, [{matrix_str}]);
    result.flag_thresholds = [{matrix_str}];
    if isfield(EEG, 'reject') && isfield(EEG.reject, 'gcompreject')
        flagged = find(EEG.reject.gcompreject);
        result.flagged_components = flagged';
        result.num_flagged = length(flagged);
    else
        result.flagged_components = [];
        result.num_flagged = 0;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_remove_components(args: dict) -> list[TextContent]:
    """移除 ICA 成分。"""
    component_indices = args.get("component_indices", [])
    auto_threshold = args.get("auto_remove_brain_threshold")

    if auto_threshold is not None:
        remove_code = f"""
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
elseif ~isfield(EEG, 'etc') || ~isfield(EEG.etc, 'ic_classification') || ~isfield(EEG.etc.ic_classification, 'ICLabel')
    result.status = 'error';
    result.error = '尚未运行 ICLabel 分类，请先调用 eeglab_classify_ica';
else
    classifications = EEG.etc.ic_classification.ICLabel.classifications;
    brain_probs = classifications(:,1);
    remove_idx = find(brain_probs < {auto_threshold});
    if isempty(remove_idx)
        result.message = '没有需要移除的成分(所有成分 Brain 概率均高于阈值)';
        result.removed_components = [];
    else
        EEG = pop_subcomp(EEG, remove_idx, 0);
        result.removed_components = remove_idx';
        result.num_removed = length(remove_idx);
        result.remaining_channels = EEG.nbchan;
    end
end
"""
    elif component_indices:
        indices_str = _arr(component_indices)
        remove_code = f"""
EEG = pop_subcomp(EEG, {indices_str}, 0);
result.removed_components = {indices_str};
result.num_removed = length({indices_str});
result.remaining_channels = EEG.nbchan;
"""
    else:
        return _error_response(
            "missing_required_argument",
            "请指定 component_indices 或 auto_remove_brain_threshold",
            next_step="传入要移除的 ICA 成分索引，或传入自动移除阈值后重试。",
        )

    code = f"""
{_maybe_init()}
{remove_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_reject_epochs(args: dict) -> list[TextContent]:
    """试次拒绝。"""
    method = args.get("method", "threshold")
    threshold = args.get("threshold", [-100, 100])
    channels = args.get("channels", [])
    jp_threshold = args.get("jp_threshold", 3)

    if method == "threshold":
        if channels:
            chan_str = _cell(channels)
            chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
        else:
            chan_code = "chan_idx = 1:EEG.nbchan;"

        # Bug fix: pop_eegthresh 中 Python None -> MATLAB []
        reject_code = f"""
{chan_code}
EEG = pop_eegthresh(EEG, [], EEG, 1, chan_idx, {threshold[0]}, {threshold[1]}, 0, 0);
result.method = 'threshold';
result.threshold = [{threshold[0]}, {threshold[1]}];
result.remaining_trials = EEG.trials;
result.rejected_trials = EEG.trials;
"""
    else:  # joint_probability
        if channels:
            chan_str = _cell(channels)
            chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
        else:
            chan_code = "chan_idx = 1:EEG.nbchan;"

        reject_code = f"""
{chan_code}
EEG = pop_jointprob(EEG, [], EEG, 1, chan_idx, {jp_threshold}, {jp_threshold});
result.method = 'joint_probability';
result.jp_threshold = {jp_threshold};
result.remaining_trials = EEG.trials;
"""

    code = f"""
{_maybe_init()}
{reject_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_get_events(args: dict) -> list[TextContent]:
    """获取事件信息。"""
    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG)
    result.status = 'error';
    result.error = '当前没有加载 EEG 数据，请先调用 eeglab_load_data';
elseif ~isfield(EEG, 'event') || isempty(EEG.event)
    result.num_events = 0;
    result.event_types = {{}};
    result.event_counts = struct();
else
    event_types = unique({{EEG.event.type}});
    result.num_events = length(EEG.event);
    result.event_types = event_types;
    for i = 1:length(event_types)
        cnt = sum(strcmp({{EEG.event.type}}, event_types{{i}}));
        result.event_counts.(event_types{{i}}) = cnt;
    end
    if isfield(EEG.event, 'latency')
        result.latency_range = [min([EEG.event.latency]), max([EEG.event.latency])];
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 4 类：分段与 ERP
# ---------------------------------------------------------------------------

async def _eeglab_epoch(args: dict) -> list[TextContent]:
    """分段 + 基线校正。"""
    event_types = args.get("event_types", [])
    pre_stim = args.get("pre_stimulus", -0.2)
    post_stim = args.get("post_stimulus", 0.8)
    bl_start = args.get("baseline_start", -0.2)
    bl_end = args.get("baseline_end", 0)
    window_errors = validate_analysis_windows(
        epoch_window=[pre_stim, post_stim],
        baseline_window_ms=[bl_start * 1000, bl_end * 1000],
    )
    if window_errors:
        return _error_response(
            "invalid_analysis_window",
            f"分段/基线窗口不合法: {'; '.join(window_errors)}",
            next_step="确保 baseline_start/baseline_end 落在 pre_stimulus/post_stimulus 时间窗内。",
            details={"errors": window_errors},
        )

    if event_types:
        events_str = _cell(event_types)
    else:
        events_str = "{'all'}"

    # Bug fix: pop_epoch epochinfo 参数值应该是 'on' 而非 'yes'
    # Bug fix: 基线参数使用用户指定的 bl_start*1000 而非 EEG.xmin*1000
    code = f"""
{_maybe_init()}
EEG = pop_epoch(EEG, {events_str}, [{pre_stim}, {post_stim}], 'epochinfo', 'on');
baseline_requested = [{bl_start * 1000}, {bl_end * 1000}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
result.trials = EEG.trials;
result.xmin = EEG.xmin;
result.xmax = EEG.xmax;
result.pnts = EEG.pnts;
result.baseline_requested = baseline_requested;
result.baseline_applied = [EEG.times(baseline_points(1)), EEG.times(baseline_points(end))];
result.baseline_points = [baseline_points(1), baseline_points(end)];
result.event_types = {events_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_erp_analysis(args: dict) -> list[TextContent]:
    """ERP 分析。"""
    channels = args.get("channels", [])
    time_window = args.get("time_window", [])
    peak_detection = args.get("peak_detection", True)
    conditions = args.get("conditions", [])

    if channels:
        chan_str = _cell(channels)
        chan_code = f"""
chan_labels = {chan_str};
[~, chan_idx] = ismember(chan_labels, {{EEG.chanlocs.labels}});
chan_idx = chan_idx(chan_idx > 0);
if isempty(chan_idx)
    error('No requested channels were found in EEG.chanlocs');
end
"""
    else:
        chan_code = "chan_idx = 1:EEG.nbchan;"

    if time_window and len(time_window) == 2:
        tw_code = f"time_mask = EEG.times >= {time_window[0]} & EEG.times <= {time_window[1]};"
        tw_vals = f"[{time_window[0]}, {time_window[1]}]"
    else:
        tw_code = "time_mask = true(size(EEG.times));"
        tw_vals = "[EEG.xmin*1000, EEG.xmax*1000]"

    # 按条件分组
    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"""
cond_names = {cond_str};
result.conditions = cond_names;
for c = 1:length(cond_names)
    cond_name = cond_names{{c}};
    cond_field = matlab.lang.makeValidName(char(cond_name));
    cond_trials = [];
    if isfield(EEG, 'epoch') && ~isempty(EEG.epoch)
        for ep = 1:length(EEG.epoch)
            ep_types = EEG.epoch(ep).eventtype;
            if ischar(ep_types)
                ep_types = {{ep_types}};
            elseif isnumeric(ep_types)
                ep_types = {{num2str(ep_types)}};
            end
            if any(strcmp(cellfun(@char, ep_types, 'UniformOutput', false), char(cond_name)))
                cond_trials(end+1) = ep; %#ok<AGROW>
            end
        end
    else
        cond_mask = strcmp({{EEG.event.type}}, cond_name);
        cond_trials = find(cond_mask);
    end
    if ~isempty(cond_trials)
        erp_cond = mean(EEG.data(chan_idx, time_mask, cond_trials), 3);
        result.erp.(cond_field).mean_amplitude = mean(erp_cond, 2);
        result.erp.(cond_field).num_trials = length(cond_trials);
"""
        if peak_detection and time_window:
            cond_code += f"""
        for i = 1:length(chan_idx)
            chan_label = EEG.chanlocs(chan_idx(i)).labels;
            chan_field = matlab.lang.makeValidName(char(chan_label));
            chan_erp = squeeze(erp_cond(i,:));
            [max_val, max_idx] = max(chan_erp);
            [min_val, min_idx] = min(chan_erp);
            peak_times = EEG.times(time_mask);
            result.erp.(cond_field).peaks.(chan_field).positive_peak_amplitude = max_val;
            result.erp.(cond_field).peaks.(chan_field).positive_peak_latency = peak_times(max_idx);
            result.erp.(cond_field).peaks.(chan_field).negative_peak_amplitude = min_val;
            result.erp.(cond_field).peaks.(chan_field).negative_peak_latency = peak_times(min_idx);
        end
"""
        cond_code += "    else\n        result.erp.(cond_field).mean_amplitude = [];\n        result.erp.(cond_field).num_trials = 0;\n    end\nend\n"
    else:
        cond_code = ""

    code = f"""
{_maybe_init()}
{chan_code}
{tw_code}
erp_data = mean(EEG.data(chan_idx, time_mask, :), 3);
result.channels = {{EEG.chanlocs(chan_idx).labels}};
result.time_window = {tw_vals};
result.mean_amplitude = mean(erp_data, 2);
{cond_code}
"""

    if peak_detection and time_window and not conditions:
        code += f"""
for i = 1:length(chan_idx)
    chan_label = EEG.chanlocs(chan_idx(i)).labels;
    chan_field = matlab.lang.makeValidName(char(chan_label));
    chan_erp = squeeze(erp_data(i,:));
    [max_val, max_idx] = max(chan_erp);
    [min_val, min_idx] = min(chan_erp);
    peak_times = EEG.times(time_mask);
    result.peaks.(chan_field).positive_peak_amplitude = max_val;
    result.peaks.(chan_field).positive_peak_latency = peak_times(max_idx);
    result.peaks.(chan_field).negative_peak_amplitude = min_val;
    result.peaks.(chan_field).negative_peak_latency = peak_times(min_idx);
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_sort_epochs(args: dict) -> list[TextContent]:
    """按条件排序试次。"""
    sort_by = args["sort_by"]
    sort_by_lit = matlab_string(sort_by)

    code = f"""
{_maybe_init()}
EEG = pop_sort(EEG, {sort_by_lit});
result.sorted_by = {sort_by_lit};
result.trials = EEG.trials;
if isfield(EEG, 'event') && ~isempty(EEG.event)
    event_types = unique({{EEG.event.type}});
    result.event_types = event_types;
    for i = 1:length(event_types)
        cnt = sum(strcmp({{EEG.event.type}}, event_types{{i}}));
        result.event_counts.(event_types{{i}}) = cnt;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_average_erp(args: dict) -> list[TextContent]:
    """ERP 平均。"""
    conditions = args.get("conditions", [])
    channels = args.get("channels", [])

    if channels:
        chan_str = _cell(channels)
        chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
    else:
        chan_code = "chan_idx = 1:EEG.nbchan;"

    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"""
result.conditions = {cond_str};
for c = 1:length({cond_str})
    cond_name = {cond_str}{{c}};
    cond_mask = strcmp({{EEG.event.type}}, cond_name);
    cond_trials = find(cond_mask);
    if ~isempty(cond_trials)
        avg_erp = mean(EEG.data(chan_idx, :, cond_trials), 3);
        result.erp.(cond_name).mean_amplitude = squeeze(mean(avg_erp, 2));
        result.erp.(cond_name).num_trials = length(cond_trials);
    else
        result.erp.(cond_name).mean_amplitude = [];
        result.erp.(cond_name).num_trials = 0;
    end
end
"""
    else:
        cond_code = """
avg_erp = mean(EEG.data(chan_idx, :, :), 3);
result.mean_amplitude = squeeze(mean(avg_erp, 2));
result.num_trials = EEG.trials;
"""

    code = f"""
{_maybe_init()}
{chan_code}
result.channels = {{EEG.chanlocs(chan_idx).labels}};
{cond_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 5 类：频域与时频
# ---------------------------------------------------------------------------

async def _eeglab_spectral(args: dict) -> list[TextContent]:
    """频谱/功率谱密度分析。"""
    channels = args.get("channels", [])
    freq_range = args.get("freq_range", [0.5, 100])
    band_power = args.get("band_power", True)

    if channels:
        chan_str = _cell(channels)
        # Bug fix: pop_spectopo 正确签名
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    # Bug fix: pop_spectopo 调用签名是 pop_spectopo(EEG, percent, freqspace, 'EEG', EEG, ...)
    code = f"""
{_maybe_init()}
[spectra, freqs] = pop_spectopo(EEG, 1, EEG.pnts, 'EEG', EEG, {chan_code}'freqrange', [{freq_range[0]}, {freq_range[1]}]);
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.freq_resolution = length(freqs);
"""

    if band_power:
        code += """
bands = struct();
band_names = {'delta', 'theta', 'alpha', 'beta', 'gamma'};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
total_power = 0;
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_pow = mean(spectra(fmask,:), 1);
        abs_pow = mean(band_pow);
        bands.(band_names{b}).absolute_power = abs_pow;
        bands.(band_names{b}).freq_range = band_ranges(b,:);
        total_power = total_power + abs_pow;
    end
end
for b = 1:length(band_names)
    if isfield(bands, band_names{b})
        bands.(band_names{b}).relative_power_percent = bands.(band_names{b}).absolute_power / total_power * 100;
    end
end
result.band_power = bands;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_timefreq(args: dict) -> list[TextContent]:
    """时频分析。"""
    channels = args.get("channels", [])
    freq_range = args.get("freq_range", [3, 80])
    cycles = args.get("cycles", [3, 10])
    baseline = args.get("baseline", [-200, 0])
    output_type = args.get("output_type", "both")

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    cycles_str = _arr(cycles)

    # Bug fix: pop_newtimef 正确调用
    code = f"""
{_maybe_init()}
[ERSP, ITC, times, freqs, specs] = pop_newtimef(EEG, 1, 1:EEG.nbchan, ...
    [EEG.xmin*1000 EEG.xmax*1000], ...
    [3 0.5], ...
    {chan_code}...
    'freqs', [{freq_range[0]}, {freq_range[1]}], ...
    'cycles', {cycles_str}, ...
    'baseline', [{baseline[0]}, {baseline[1]}]);
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.freq_resolution = length(freqs);
result.time_points = length(times);
result.method = 'wavelet';
result.baseline = [{baseline[0]}, {baseline[1]}];
result.cycles = {cycles_str};
bands = struct();
band_names = {{'delta', 'theta', 'alpha', 'beta', 'gamma'}};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_ersp = mean(ERSP(fmask,:), 1);
        bands.(band_names{{b}}).mean_ersp = mean(band_ersp);
        bands.(band_names{{b}}).max_ersp = max(band_ersp);
        bands.(band_names{{b}}).freq_range = band_ranges(b,:);
        if size(ITC, 1) == size(ERSP, 1)
            band_itc = mean(ITC(fmask,:), 1);
            bands.(band_names{{b}}).mean_itc = mean(band_itc);
        end
    end
end
result.band_ersp = bands;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_connectivity(args: dict) -> list[TextContent]:
    """功能连接分析。"""
    channels = args.get("channels", [])
    method = args.get("method", "coherence")
    freq_range = args.get("freq_range", [8, 13])
    method_lit = matlab_string(method)

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    if method == "coherence":
        method_str = "'coherence'"
    else:
        method_str = "'plv'"

    code = f"""
{_maybe_init()}
[conn_data, freqs] = pop_crossfreq(EEG, 1, 1:EEG.nbchan, ...
    {chan_code}...
    'method', {method_str}, ...
    'freqs', [{freq_range[0]}, {freq_range[1]}]);
result.method = {method_lit};
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.freq_resolution = length(freqs);
if ~isempty(conn_data)
    result.mean_connectivity = mean(conn_data(:));
    result.max_connectivity = max(conn_data(:));
    result.min_connectivity = min(conn_data(:));
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 6 类：可视化
# ---------------------------------------------------------------------------

async def _eeglab_topoplot(args: dict) -> list[TextContent]:
    """绘制头皮地形图。"""
    output_path = args["output_path"]
    time_point = args.get("time_point")
    time_window = args.get("time_window")
    channels = args.get("channels", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chaninfo', {chan_str}, "
    else:
        chan_code = ""

    if time_point is not None:
        time_code = f"'time', {time_point}, "
    elif time_window and len(time_window) == 2:
        time_code = f"'time', [{time_window[0]}, {time_window[1]}], "
    else:
        time_code = ""

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_topoplot(EEG, {time_code}{chan_code}{title_code}'style', 'straight', 'electrodes', 'on');
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_erp(args: dict) -> list[TextContent]:
    """绘制 ERP 波形图。"""
    channels = args["channels"]
    output_path = args["output_path"]
    conditions = args.get("conditions", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    chan_str = _cell(channels)

    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"'conditions', {cond_str}, "
    else:
        cond_code = ""

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_ploterp(EEG, 'channels', {chan_str}, {cond_code}{title_code}'overlay', 'on');
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
result.channels = {chan_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_timefreq(args: dict) -> list[TextContent]:
    """绘制时频图。"""
    channel = args["channel"]
    output_path = args["output_path"]
    plot_ersp = args.get("plot_ersp", True)
    plot_itc = args.get("plot_itc", True)
    title = args.get("title", "")
    channel_lit = matlab_string(channel)
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_newtimef(EEG, 1, {channel_lit}, [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
    'freqs', [3 80], 'cycles', [3 10], ...
    'plotersp', '{"on" if plot_ersp else "off"}', ...
    'plotitc', '{"on" if plot_itc else "off"}', ...
    {title_code}'pad', 0);
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
result.channel = {channel_lit};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_components(args: dict) -> list[TextContent]:
    """绘制 ICA 成分图。"""
    output_path = args["output_path"]
    component_indices = args.get("component_indices", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if component_indices:
        comp_str = _arr(component_indices)
    else:
        comp_str = "1:min(10, size(EEG.icaweights, 1))"

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    figure('Visible', 'off');
    pop_topoplot(EEG, {title_code}'components', {comp_str});
    saveas(gcf, {output_path_lit});
    close(gcf);
    result.output_path = {output_path_lit};
    result.components = {comp_str};
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 7 类：源定位
# ---------------------------------------------------------------------------

async def _eeglab_source_localization(args: dict) -> list[TextContent]:
    """源定位分析（偶极子拟合）。"""
    component_indices = args.get("component_indices", [])
    head_model = args.get("head_model", "bem")
    template = args.get("template", "mni")

    if component_indices:
        comp_str = _arr(component_indices)
    else:
        comp_str = "1:size(EEG.icaweights,1)"

    # Bug fix: pop_dipfit_settings 需要完整参数
    if head_model == "bem":
        hdmfile = "standard_bem.mat"
    else:
        hdmfile = "standard_vol.mat"

    coord = "MNI" if template == "mni" else "Colin27"

    # Determine chanfile and mrifile based on template
    if template == "mni":
        chanfile = "standard-10-5-cap385.elp"
        mrifile = "standard_mri.mat"
    else:
        chanfile = "standard-10-5-cap385.elp"
        mrifile = "colin27_mri.mat"

    head_model_lit = matlab_string(head_model)
    template_lit = matlab_string(template)
    hdmfile_lit = matlab_string(hdmfile)
    chanfile_lit = matlab_string(chanfile)
    mrifile_lit = matlab_string(mrifile)
    coord_lit = matlab_string(coord)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    EEG = pop_dipfit_settings(EEG, 'hdmfile', {hdmfile_lit}, 'chanfile', {chanfile_lit}, 'mrifile', {mrifile_lit}, 'coordformat', {coord_lit});
    EEG = pop_multifit(EEG, {comp_str});
    result.head_model = {head_model_lit};
    result.template = {template_lit};
    result.ncomponents = length({comp_str});
    if isfield(EEG, 'dipfit') && ~isempty(EEG.dipfit)
        dipoles = struct();
        comp_list = {comp_str};
        for i = 1:length(comp_list)
            ci = comp_list(i);
            if length(EEG.dipfit) >= ci && ~isempty(EEG.dipfit(ci).dippos)
                comp_name = ['comp_' num2str(ci)];
                dipoles.(comp_name).position_x = EEG.dipfit(ci).dippos(1);
                dipoles.(comp_name).position_y = EEG.dipfit(ci).dippos(2);
                dipoles.(comp_name).position_z = EEG.dipfit(ci).dippos(3);
                dipoles.(comp_name).residual_variance = EEG.dipfit(ci).rv;
            end
        end
        result.dipoles = dipoles;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_source_settings(args: dict) -> list[TextContent]:
    """Dipfit 模型设置。"""
    head_model = args.get("head_model", "bem")
    template = args.get("template", "mni")
    chanfile = args.get("chanfile", "")
    mrifile = args.get("mrifile", "")

    if head_model == "bem":
        hdmfile = "standard_bem.mat"
    else:
        hdmfile = "standard_vol.mat"

    coord = "MNI" if template == "mni" else "Colin27"

    if not chanfile:
        chanfile = "standard-10-5-cap385.elp"
    if not mrifile:
        mrifile = "standard_mri.mat" if template == "mni" else "colin27_mri.mat"

    head_model_lit = matlab_string(head_model)
    template_lit = matlab_string(template)
    hdmfile_lit = matlab_string(hdmfile)
    chanfile_lit = matlab_string(chanfile)
    mrifile_lit = matlab_string(mrifile)
    coord_lit = matlab_string(coord)

    code = f"""
{_maybe_init()}
EEG = pop_dipfit_settings(EEG, 'hdmfile', {hdmfile_lit}, 'chanfile', {chanfile_lit}, 'mrifile', {mrifile_lit}, 'coordformat', {coord_lit});
result.head_model = {head_model_lit};
result.template = {template_lit};
result.hdmfile = {hdmfile_lit};
result.chanfile = {chanfile_lit};
result.mrifile = {mrifile_lit};
result.coordformat = {coord_lit};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# 第 8 类：组分析与 Pipeline
# ---------------------------------------------------------------------------

async def _eeglab_study_create(args: dict) -> list[TextContent]:
    """创建 STUDY。"""
    bids_path = args.get("bids_path", "")
    study_name = args.get("study_name", "MyStudy")
    dataset_paths = args.get("dataset_paths", [])
    study_name_lit = matlab_string(study_name)

    if bids_path:
        bids_path_lit = matlab_string(bids_path)
        create_code = f"""
[STUDY, ALLEEG] = pop_importbids({bids_path_lit}, 'studyName', {study_name_lit}, 'bidsevent', 'on', 'bidschanloc', 'on');
"""
    elif dataset_paths:
        paths_str = matlab_cell(dataset_paths)
        create_code = f"""
[STUDY, ALLEEG] = pop_studywizard('dataset',{paths_str},'studyName',{study_name_lit});
"""
    else:
        return _error_response("missing_required_argument", "请指定 bids_path 或 dataset_paths", next_step="传入 BIDS 根目录或 .set 文件路径列表后重试。")

    code = f"""
{_maybe_init()}
{create_code}
STUDY = pop_study(STUDY, ALLEEG, 'name', {study_name_lit}, 'commands', {{}});
result.study_name = {study_name_lit};
result.num_datasets = length(ALLEEG);
result.subjects = {{STUDY.subject}};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_study_design(args: dict) -> list[TextContent]:
    """定义 STUDY 实验设计。"""
    design_name = args.get("design_name", "Design1")
    variable_name = args.get("variable_name", "condition")
    variable_values = args.get("variable_values", ["target", "standard"])

    vals_str = _cell(variable_values)
    design_name_lit = matlab_string(design_name)
    variable_name_lit = matlab_string(variable_name)

    code = f"""
{_maybe_init()}
STUDY = std_makedesign(STUDY, ALLEEG, 1, ...
    'name', {design_name_lit}, ...
    'variable1', {variable_name_lit}, ...
    'values1', {vals_str}, ...
    'vartype1', 'categorical', ...
    'subjselect', STUDY.subject);
result.design_name = {design_name_lit};
result.variable_name = {variable_name_lit};
result.variable_values = {vals_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_study_statistics(args: dict) -> list[TextContent]:
    """STUDY 统计检验。"""
    measure = args.get("measure", "erp")
    alpha = args.get("alpha", 0.05)
    correction = args.get("correction", "fdr")
    measure_lit = matlab_string(measure)
    correction_lit = matlab_string(correction)

    # Map measure to pop_statparams
    measure_map = {
        "erp": "'measure', 'erp'",
        "spectrum": "'measure', 'power'",
        "ersp": "'measure', 'ersp'",
    }
    measure_str = measure_map.get(measure, "'measure', 'erp'")

    # Map correction method
    correction_map = {
        "fdr": "'corr', 'FDR'",
        "bonferroni": "'corr', 'Bonferroni'",
        "cluster": "'corr', 'cluster'",
        "none": "'corr', 'none'",
    }
    correction_str = correction_map.get(correction, "'corr', 'FDR'")

    code = f"""
{_maybe_init()}
STUDY = pop_statparams(STUDY, {measure_str}, {correction_str}, 'alpha', {alpha});
[STUDY, stats] = pop_stat(EEG, STUDY, ALLEEG);
result.measure = {measure_lit};
result.alpha = {alpha};
result.correction = {correction_lit};
if exist('stats', 'var') && ~isempty(stats)
    result.stat_summary = struct();
    if isfield(stats, 'pvalue')
        result.stat_summary.significant_channels = sum(stats.pvalue < {alpha});
        result.stat_summary.min_pvalue = min(stats.pvalue);
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_pipeline(args: dict) -> list[TextContent]:
    """一键流程生成。"""
    pipeline_type = args["pipeline_type"]
    data_path = args["data_path"]
    output_dir = args.get("output_dir", "")
    highpass = args.get("highpass", 1.0)
    lowpass = args.get("lowpass", 40.0)
    event_types = args.get("event_types", [])
    epoch_window = args.get("epoch_window", [-0.2, 0.8])
    baseline_window = args.get("baseline_window", [-200, 0])
    ica_algorithm = args.get("ica_algorithm", "picard")
    burst_criterion = args.get("burst_criterion", 20)

    if not output_dir:
        output_dir = str(Path(cfg.EEGLAB_WORK_DIR) / f"{pipeline_type}_pipeline")

    ext = Path(data_path).suffix.lower().lstrip(".")
    data_path_lit = matlab_string(data_path)
    output_dir_lit = matlab_string(output_dir)
    ica_algorithm_lit = matlab_string(ica_algorithm)

    # 加载数据
    if ext == "set":
        fp = Path(data_path)
        load_code = f"EEG = pop_loadset('filename',{matlab_string(fp.name)},'filepath',{matlab_string(str(fp.parent))});\n"
    else:
        load_code = f"EEG = pop_biosig({data_path_lit});\n"

    # 公共预处理步骤
    common_steps = f"""
%% 1. 加载数据
{load_code}
EEG = eeg_checkset(EEG);

%% 2. 降采样（如果采样率过高）
if EEG.srate > 500
    EEG = pop_resample(EEG, 250);
    EEG = eeg_checkset(EEG);
end

%% 3. 滤波
EEG = pop_eegfiltnew(EEG, 'locutoff', {highpass}, 'hicutoff', {lowpass});
EEG = eeg_checkset(EEG);

%% 4. ASR 伪迹去除
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion', 5, 'ChannelCriterion', 0.8, 'LineNoiseCriterion', 4, 'Highpass', [0.25 0.75], 'BurstCriterion', {burst_criterion}, 'BurstRejection', 'on', 'WindowCriterion', 0.25, 'Distance', 'Euclidian', 'WindowCriterionTolerances', [-Inf 7]);
EEG = eeg_checkset(EEG);

%% 5. 重参考（平均参考）
EEG = pop_reref(EEG, []);
EEG = eeg_checkset(EEG);

%% 6. ICA 分解
EEG = pop_runica(EEG, 'icatype', {ica_algorithm_lit}, 'extended', 1, 'pca', EEG.nbchan-1);
EEG = eeg_checkset(EEG);

%% 7. ICLabel 分类
EEG = pop_iclabel(EEG);
EEG = eeg_checkset(EEG);

%% 8. 标记和移除伪迹成分
EEG = pop_icflag(EEG, [NaN NaN; 0.9 1; 0.9 1; NaN NaN; NaN NaN; NaN NaN; NaN NaN]);
EEG = pop_subcomp(EEG, find(EEG.reject.gcompreject), 0);
EEG = eeg_checkset(EEG);

%% 9. 通道插值
EEG = pop_interp(EEG, EEG.urchanlocs, 'spherical');
EEG = eeg_checkset(EEG);

%% 10. 再次重参考
EEG = pop_reref(EEG, []);
EEG = eeg_checkset(EEG);
"""

    if pipeline_type == "erp":
        events = event_types if event_types else ["stimulus"]
        events_str = _cell(events)
        pipeline_code = f"""
{common_steps}
%% 11. 分段
EEG = pop_epoch(EEG, {events_str}, [{epoch_window[0]}, {epoch_window[1]}], 'epochinfo', 'on');
EEG = eeg_checkset(EEG);

%% 12. 基线校正
baseline_requested = [{baseline_window[0]}, {baseline_window[1]}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
EEG = eeg_checkset(EEG);

%% 13. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'erp_processed.set', 'filepath', output_dir);
result.pipeline_type = 'erp';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'erp_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'epoch', 'baseline', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.trials = EEG.trials;
disp('ERP pipeline complete.');
"""

    elif pipeline_type == "resting":
        pipeline_code = f"""
{common_steps}
%% 11. 频谱分析
[spectra, freqs] = pop_spectopo(EEG, 1, EEG.pnts, 'EEG', EEG, 'freqrange', [0.5, 45]);

%% 12. 计算各频段功率
bands = struct();
band_names = {{'delta', 'theta', 'alpha', 'beta', 'gamma'}};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 45];
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_pow = mean(10*log10(spectra(fmask,:)), 2);
        bands.(band_names{{b}}).mean_power = mean(band_pow);
        bands.(band_names{{b}}).freq_range = band_ranges(b,:);
    end
end

%% 13. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'resting_processed.set', 'filepath', output_dir);
save(fullfile(output_dir, 'spectra.mat'), 'spectra', 'freqs');
result.pipeline_type = 'resting';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'resting_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'spectral', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.band_power = bands;
disp('Resting-state pipeline complete.');
"""

    elif pipeline_type == "timefreq":
        events = event_types if event_types else ["stimulus"]
        events_str = _cell(events)
        pipeline_code = f"""
{common_steps}
%% 11. 分段
EEG = pop_epoch(EEG, {events_str}, [{epoch_window[0]}, {epoch_window[1]}], 'epochinfo', 'on');
EEG = eeg_checkset(EEG);

%% 12. 基线校正
baseline_requested = [{baseline_window[0]}, {baseline_window[1]}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
EEG = eeg_checkset(EEG);

%% 13. 时频分析
[ERSP, ITC, times, freqs] = pop_newtimef(EEG, 1, 1:EEG.nbchan, ...
    [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
    'freqs', [3 80], 'cycles', [3 10], ...
    'baseline', [{baseline_window[0]}, {baseline_window[1]}]);

%% 14. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'timefreq_processed.set', 'filepath', output_dir);
save(fullfile(output_dir, 'timefreq_results.mat'), 'ERSP', 'ITC', 'times', 'freqs');
result.pipeline_type = 'timefreq';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'timefreq_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'epoch', 'baseline', 'timefreq', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.trials = EEG.trials;
disp('Time-frequency pipeline complete.');
"""
    else:
        return _error_response("invalid_arguments", f"不支持的流程类型: {pipeline_type}", next_step="pipeline_type 只能是 erp、resting 或 timefreq。")

    code = f"""
{_eeglab_init_code()}
{pipeline_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


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
                server_version="2.0.0",
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
