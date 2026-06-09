"""MATLAB execution backend for the EEGLAB MCP server."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from .matlab_literals import matlab_string
except ImportError:  # pragma: no cover - direct script execution support
    from matlab_literals import matlab_string


class Config:
    """Configuration loaded from environment variables."""

    EEGLAB_PATH: str = os.environ.get("EEGLAB_PATH", "")
    MATLAB_ROOT: str = os.environ.get("MATLAB_ROOT", "")
    EEGLAB_WORK_DIR: str = os.environ.get(
        "EEGLAB_WORK_DIR",
        str(Path.home() / "Desktop" / "eeglabmcp"),
    )
    MATLAB_EXEC: str = os.environ.get("MATLAB_EXEC", "matlab")
    MATLAB_TIMEOUT: int = int(os.environ.get("MATLAB_TIMEOUT", "300"))


cfg = Config()
DEBUG_ERRORS = os.environ.get("EEGLAB_MCP_DEBUG", "").lower() in {"1", "true", "yes", "on"}


def matlab_json_sanitize_code() -> str:
    """MATLAB function block used before jsonencode for diagnostic-safe JSON."""
    return r"""
function out = eeglab_mcp_sanitize_json(in)
    if isstruct(in)
        out = struct();
        fields = fieldnames(in);
        for k = 1:numel(fields)
            safeField = matlab.lang.makeValidName(fields{k});
            if isempty(safeField)
                safeField = sprintf('field_%d', k);
            end
            out.(safeField) = eeglab_mcp_sanitize_json(in.(fields{k}));
        end
    elseif iscell(in)
        out = cell(size(in));
        for k = 1:numel(in)
            out{k} = eeglab_mcp_sanitize_json(in{k});
        end
    elseif isnumeric(in) || islogical(in)
        out = in;
        if isnumeric(out)
            out(~isfinite(out)) = NaN;
        end
    elseif isstring(in)
        out = cellstr(in);
        if isscalar(out)
            out = out{1};
        end
    elseif ischar(in)
        out = in;
    else
        try
            out = char(in);
        catch
            out = '<unserializable>';
        end
    end
end
"""


def _preview(text: str, limit: int = 1200) -> str:
    """Return a bounded tail preview for diagnostics."""
    if not text:
        return ""
    return text[-limit:]


def _load_result_file(result_file: str, *, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    """Load MATLAB result JSON with structured diagnostics on malformed output."""
    if not os.path.exists(result_file):
        return {
            "status": "error",
            "error": "无法读取结果文件",
            "code": "matlab_result_missing",
            "details": {
                "result_file": result_file,
                "stdout_preview": _preview(stdout),
                "stderr_preview": _preview(stderr),
            },
        }

    try:
        raw = Path(result_file).read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "status": "error",
            "error": f"读取 MATLAB 结果文件失败: {exc}",
            "code": "matlab_result_read_error",
            "details": {
                "result_file": result_file,
                "stdout_preview": _preview(stdout),
                "stderr_preview": _preview(stderr),
            },
        }

    if not raw.strip():
        return {
            "status": "error",
            "error": "MATLAB 结果文件为空",
            "code": "matlab_result_empty",
            "details": {
                "result_file": result_file,
                "stdout_preview": _preview(stdout),
                "stderr_preview": _preview(stderr),
            },
        }

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "error": f"MATLAB 结果 JSON 解析失败: {exc}",
            "code": "matlab_result_json_error",
            "details": {
                "result_file": result_file,
                "raw_preview": raw[:1200],
                "stdout_preview": _preview(stdout),
                "stderr_preview": _preview(stderr),
            },
        }


def _backend_details(mode: str, *, stdout: str = "", stderr: str = "", returncode: int | None = None) -> dict[str, Any]:
    """Return bounded backend context for actionable MCP diagnostics."""
    details: dict[str, Any] = {
        "mode": mode,
        "matlab_exec": cfg.MATLAB_EXEC,
        "matlab_timeout_sec": cfg.MATLAB_TIMEOUT,
        "work_dir": cfg.EEGLAB_WORK_DIR,
    }
    if returncode is not None:
        details["returncode"] = returncode
    if stdout:
        details["stdout_preview"] = _preview(stdout)
    if stderr:
        details["stderr_preview"] = _preview(stderr)
    return details


class MatlabBackend:
    """MATLAB backend supporting Engine API and CLI fallback."""

    def __init__(self):
        self._engine = None
        self._mode: str | None = None
        self._eeglab_initialized = False
        self._work_dir: str = cfg.EEGLAB_WORK_DIR
        self._eeg_state_file: str = ""

    def _detect_mode(self) -> str:
        """Detect available MATLAB execution mode."""
        try:
            import matlab.engine  # noqa: F401

            return "engine"
        except ImportError:
            pass

        try:
            result = subprocess.run(
                [cfg.MATLAB_EXEC, "-batch", "disp('ok')"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return "cli"
        except Exception:
            pass

        return "none"

    async def execute(self, code: str, project_path: str = "") -> dict[str, Any]:
        """Execute MATLAB code and return a JSON-compatible result dictionary."""
        if self._mode is None:
            self._mode = self._detect_mode()

        if self._mode == "engine":
            result = await self._execute_engine(code, project_path)
        elif self._mode == "cli":
            result = await self._execute_cli(code, project_path)
        else:
            result = {
                "status": "error",
                "code": "matlab_unavailable",
                "error": "MATLAB 不可用。请安装 MATLAB Engine for Python 或确保 matlab 命令在 PATH 中。",
                "next_step": "确认 MATLAB 已安装，MATLAB_EXEC 指向可执行文件，并且 EEGLAB_PATH 指向本地 EEGLAB 目录后重试。",
                "hint": "Engine: cd 'MATLAB_PATH/extern/engines/python' && python setup.py install\n"
                "CLI: 确保 matlab 在系统 PATH 中",
                "details": _backend_details("none"),
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

    async def _execute_engine(self, code: str, project_path: str) -> dict[str, Any]:
        """Execute MATLAB code through MATLAB Engine for Python."""
        try:
            import matlab.engine
        except ImportError:
            self._mode = None
            return await self.execute(code, project_path)

        if self._engine is None:
            try:
                self._engine = matlab.engine.start_matlab()
            except Exception as exc:
                return {
                    "status": "error",
                    "code": "matlab_engine_start_failed",
                    "error": f"启动 MATLAB 引擎失败: {exc}",
                    "next_step": "确认 MATLAB Engine for Python 与当前 Python 版本兼容，或改用 MATLAB CLI 模式。",
                    "details": _backend_details("engine"),
                }

        fd, result_file = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            if project_path:
                self._engine.eval(f"cd({matlab_string(project_path)});", nargout=0)

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
try
    safeResult = eeglab_mcp_sanitize_json(result);
    jsonStr = jsonencode(safeResult);
catch ME
    fallback = struct();
    fallback.status = 'error';
    fallback.code = 'matlab_json_encode_error';
    fallback.error = ME.message;
    jsonStr = jsonencode(fallback);
end
fid = fopen({matlab_string(result_file)}, 'w');
fprintf(fid, '%s', jsonStr);
fclose(fid);
{matlab_json_sanitize_code()}
"""
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._engine.eval(wrapped, nargout=0))
            return _load_result_file(result_file)
        except Exception as exc:
            self._engine = None
            self._eeglab_initialized = False
            return {
                "status": "error",
                "code": "matlab_engine_error",
                "error": f"Engine 执行错误: {exc}",
                "next_step": "检查 MATLAB 会话状态、EEGLAB 初始化状态和输入参数；必要时重启 MCP server 后重试。",
                "details": _backend_details("engine"),
            }
        finally:
            try:
                os.unlink(result_file)
            except Exception:
                pass

    async def _execute_cli(self, code: str, project_path: str) -> dict[str, Any]:
        """Execute MATLAB code through CLI, persisting EEG state across calls."""
        os.makedirs(self._work_dir, exist_ok=True)

        if not self._eeg_state_file:
            fd, self._eeg_state_file = tempfile.mkstemp(
                suffix=".mat",
                prefix="eeg_state_",
                dir=self._work_dir,
            )
            os.close(fd)

        load_code = ""
        if os.path.exists(self._eeg_state_file) and os.path.getsize(self._eeg_state_file) > 0:
            state_file = matlab_string(self._eeg_state_file)
            load_code = f"try; EEG = load({state_file}, 'EEG'); EEG = EEG.EEG; catch; end\n"

        save_code = f"""
if exist('EEG', 'var') && isstruct(EEG)
    try; save({matlab_string(self._eeg_state_file)}, 'EEG', '-v7'); catch; end
end
"""

        fd, result_file = tempfile.mkstemp(suffix=".json")
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
try
    safeResult = eeglab_mcp_sanitize_json(result);
    jsonStr = jsonencode(safeResult);
catch ME
    fallback = struct();
    fallback.status = 'error';
    fallback.code = 'matlab_json_encode_error';
    fallback.error = ME.message;
    jsonStr = jsonencode(fallback);
end
fid = fopen({result_literal}, 'w');
fprintf(fid, '%s', jsonStr);
fclose(fid);
exit;
{matlab_json_sanitize_code()}
"""

        fd, script_path = tempfile.mkstemp(suffix=".m")
        with os.fdopen(fd, "w", encoding="utf-8") as script:
            script.write(wrapped)

        try:
            loop = asyncio.get_event_loop()
            proc_result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [cfg.MATLAB_EXEC, "-batch", f"run({matlab_string(script_path)})"],
                    capture_output=True,
                    text=True,
                    timeout=cfg.MATLAB_TIMEOUT,
                ),
            )

            if os.path.exists(result_file):
                return _load_result_file(result_file, stdout=proc_result.stdout, stderr=proc_result.stderr)
            return {
                "status": "error",
                "error": f"MATLAB 执行失败 (exit code: {proc_result.returncode})",
                "code": "matlab_process_failed",
                "next_step": "查看 stdout/stderr 预览，确认 MATLAB_EXEC、EEGLAB_PATH、插件依赖和输入文件路径后重试。",
                "details": _backend_details(
                    "cli",
                    stdout=proc_result.stdout,
                    stderr=proc_result.stderr,
                    returncode=proc_result.returncode,
                ),
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"MATLAB 执行超时 ({cfg.MATLAB_TIMEOUT}秒)",
                "code": "matlab_timeout",
                "next_step": "增大 MATLAB_TIMEOUT，或先运行更小的检查步骤定位耗时环节。",
                "details": _backend_details("cli"),
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": f"CLI 执行错误: {exc}",
                "code": "matlab_cli_error",
                "next_step": "确认 MATLAB 命令可从当前 shell 启动，并检查 EEGLAB_WORK_DIR 是否可写。",
                "details": _backend_details("cli"),
            }
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

    def _save_eeg_state(self) -> str:
        """Generate MATLAB code to save EEG state in CLI mode."""
        if self._mode == "cli" and self._eeg_state_file:
            return f"if exist('EEG','var') && isstruct(EEG); save({matlab_string(self._eeg_state_file)},'EEG','-v7'); end\n"
        return ""

    def _load_eeg_state(self) -> str:
        """Generate MATLAB code to load EEG state in CLI mode."""
        if self._mode == "cli" and self._eeg_state_file:
            return f"try; tmp=load({matlab_string(self._eeg_state_file)},'EEG'); EEG=tmp.EEG; catch; end\n"
        return ""


matlab = MatlabBackend()
