# MCP + Skill Setup

This project is intended to be distributed as two pieces:

1. The MCP server in `eeglab_mcp_server/`, which exposes executable `eeglab_*` tools.
2. The skill in `skills/eeglab-analysis/`, which teaches an agent how to use those tools for EEG workflows.

## MCP Setup

Install the server:

```powershell
python -m pip install -e .\eeglab_mcp_server
```

Use one of the ready templates in `configs/`:

- Codex: `configs/codex.config.toml`
- Claude Desktop: `configs/claude_desktop_config.json`
- Cursor: `configs/cursor.mcp.json`
- VS Code: `configs/vscode.mcp.json`

Adjust these paths before copying into the target IDE:

- `EEGLAB_PATH`
- `MATLAB_EXEC`
- `EEGLAB_WORK_DIR`
- path to `eeglab_mcp_server/server.py`

## Pairing With MATLAB MCP

The EEGLAB MCP can be used alone or alongside a separate matlab MCP. Register this server as `eeglab` and keep any general MATLAB MCP registered as `matlab`; do not merge the names.

Use eeglab first for EEG-specific work: loading recordings, QC/provenance, event audit, preprocessing, ICA, ERP, time-frequency, STUDY, source localization, and EEGLAB plots. Use matlab MCP for generic MATLAB scripts, custom statistics/matrices, or non-EEGLAB toolboxes.

Assume workspace isolation. The `EEG` variable loaded by `eeglab` is not automatically available to matlab MCP. Cross-server workflows must use file handoff: save `.set/.fdt`, `.mat`, `.csv`, `.png`, or report files from `eeglab`, then pass the explicit path to matlab MCP. Keep `EEGLAB_WORK_DIR` dedicated to this server.

## Skill Setup

For Codex, copy or symlink `skills/eeglab-analysis/` into the user's skill directory, commonly:

```powershell
C:\Users\<USER>\.codex\skills\eeglab-analysis
```

Other IDE agents that support skill-like prompt packs can import the same `SKILL.md` and `references/` folder as their domain workflow guide.

## Verification

Run lightweight checks before real EEG processing:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```

For live official URL checks, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online
```

`eeglab_agent.ps1` is the shortest user entrypoint; it forwards to the dedicated setup, verify, doctor, and uninstall scripts. `verify_eeglab_agent.ps1` is the underlying verifier. It compiles the server/verifier Python files, runs `verify_framework.py`, and runs `verify_official_alignment.py`. `verify_framework.py` confirms that the MCP and skill remain synchronized around the strict research contract: original tool compatibility, planning tools, prompts/resources, official reference terms, eval coverage, config parsing, and repository cleanliness. `verify_official_alignment.py` confirms official claim/profile/tool/resource synchronization, method gate behavior, support/plugin/report matrices, and optionally live official URLs. These checks intentionally do not require EEG test data.
Use `eeglab://official/tool-support-matrix.md` when a client or user asks whether a specific `eeglab_*` tool is executable, gated, read-only, or guidance-only.

MCP protocol smoke test:

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

Expected smoke-test result:

- registry-defined 37 legacy low-level tools and 8 research workflow tools are present
- the current eval contracts validate required/forbidden tools, gate assertions, resource references, and protocol report-field requirements
- `missing_required_arguments`

Before a large project or multi-subject analysis, run `eeglab_project_plan` or `eeglab_workflow_recommend` with the known research goal, project scale, stage, event labels, event semantics, data shape, sampling rate, ICA state, channel-location availability, continuous-raw availability, and behavioral-log status. If those facts are missing, use its `clarifying_questions`, `default_assumptions`, `blocking_conditions`, `not_recommended`, and `qc_gates` as the first planning artifact.

## First Real Dataset Check

After MATLAB and EEGLAB paths are configured, use a small `.set` file:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_info`
4. `eeglab_get_events`
5. `eeglab_history`

Do not start with ICA or `eeglab_pipeline`; first prove load and metadata inspection work.
