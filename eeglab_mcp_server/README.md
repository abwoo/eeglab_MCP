# EEGLAB MCP Server Package

This directory contains the executable MCP stdio server for the EEGLAB MCP Agent. Use the repository README for product-level setup. Use this file when you need package, runtime, protocol, or server-development details.

## Install And Run

From the repository root:

```powershell
python -m pip install -e .\eeglab_mcp_server
```

Run directly:

```powershell
python .\eeglab_mcp_server\server.py
```

Or run the installed console script:

```powershell
eeglab-mcp-server
```

For normal user setup and verification, prefer the unified dispatcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
```

## Environment

Set these in the MCP client registration for the `eeglab` server:

| Variable | Purpose |
| --- | --- |
| `EEGLAB_PATH` | Absolute path to the local EEGLAB installation. |
| `MATLAB_EXEC` | MATLAB executable name or path. Defaults to `matlab`. |
| `MATLAB_ROOT` | Optional MATLAB root path for templates and local notes. |
| `EEGLAB_WORK_DIR` | Dedicated work directory for CLI-mode state files and derivative outputs. |
| `MATLAB_TIMEOUT` | Per-call timeout in seconds. Defaults to `300`. |
| `EEGLAB_MCP_DEBUG` | Set to `1` to include Python tracebacks in tool errors. |

Client templates live in `configs/`. The setup dispatcher can install the Codex registration and Skill automatically; templates are for manual setup and custom MCP clients.

## Execution Modes

The server chooses its MATLAB backend on first tool call.

- Engine mode uses MATLAB Engine for Python and keeps one MATLAB session alive.
- CLI mode uses `matlab -batch` for each call, reloads/saves the current `EEG` state through a temporary `.mat` file, and injects `eeglab nogui` for each call.

The server runs MATLAB locally. It does not send EEG data to a remote service and does not acquire EEG from amplifiers.

## Tool Surface

The server exposes 48 MCP tools:

- 39 low-level EEGLAB wrappers for data import, inspection, preprocessing, ICA, ERP/time-frequency analysis, visualization, source localization, STUDY workflows, and pipelines.
- 9 research workflow tools for QC, planning, official method preflight, event-semantics audit, plugin checks, protocol export, report generation, and the smoke-tested ERP light workflow.

High-risk tools include official method-profile metadata in their descriptions and are gated through `eeglab_method_preflight` before MATLAB execution. Blocked gates return `official_gate_blocked` unless the user supplies an explicit override reason.

## Prompts And Resources

The server also exposes 10 prompts and 29 read-only resources for clients that support MCP guidance surfaces. These include the Skill text, workflow references, the canonical branch workflow matrix, the canonical figure atlas, the default advanced figure gallery index, official topic/support matrices, method gates, plugin matrices, risk matrices, and report-field matrices.

Resources are guidance only. Reading them does not modify EEG data or MATLAB state.

## Error Shape

Tools return JSON inside MCP text content. Errors use this shape:

```json
{
  "status": "error",
  "code": "machine_readable_code",
  "error": "human readable message",
  "next_step": "what to do next"
}
```

Common codes include `unknown_tool`, `missing_required_arguments`, `invalid_arguments`, `invalid_tool_contract`, `matlab_timeout`, `tool_execution_error`, and `official_gate_blocked`.

High-level workflow tools also expose MCP `outputSchema` and return `structuredContent` while preserving the same JSON payload in text content for older clients.

## Package Verification

Run the repository verifier from the root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
```

Run live official URL checks:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online
```

The verifier checks package parsing, registry/handler synchronization, prompt/resource exposure, config templates, Skill references, official claim/profile/tool/resource alignment, eval contracts, report-field coverage, and cache cleanliness.

## MCP Inspector

Inspect the stdio server with MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector python .\eeglab_mcp_server\server.py
```

Use Inspector to confirm `tools/list` reports 48 exposed tools, workflow tools expose `outputSchema`, and error paths return JSON text content.

## Stdio Smoke Test

```powershell
@'
import asyncio, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["eeglab_mcp_server/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tool_count", len(tools.tools))
            result = await session.call_tool("eeglab_load_data", {})
            print(json.loads(result.content[0].text)["code"])

asyncio.run(main())
'@ | python -
```

Expected result:

- `tool_count 48`
- `missing_required_arguments`

## First Real EEGLAB Smoke Test

After MATLAB and EEGLAB paths are configured, use a small local `.set` file:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_info`
4. `eeglab_qc_report`
5. `eeglab_history`

Avoid ICA, filtering, source localization, or one-click pipelines for the first smoke test because those workflows are slower, plugin-dependent, and method-gated.

## Pairing With A General MATLAB MCP

This server can run beside a generic MATLAB MCP if the names stay separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Treat the two servers as isolated MATLAB sessions. Share data through explicit files such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports.
