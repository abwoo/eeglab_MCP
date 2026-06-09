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
python -m py_compile .\eeglab_mcp_server\server.py
python -c "import tomllib; tomllib.load(open('eeglab_mcp_server/pyproject.toml','rb')); print('pyproject ok')"
python -m pip install -e .\eeglab_mcp_server
python .\scripts\verify_skill.py
python .\scripts\verify_research_alignment.py
python .\scripts\verify_mcp_stdio.py
```

`verify_research_alignment.py` confirms that the MCP and skill remain synchronized around the strict research contract: missing-goal planning, project phases, QC gates, adaptive defaults, provenance reporting, and self-evolution hooks.

If MATLAB and EEGLAB are configured, run the low-cost real dataset smoke test:

```powershell
python .\scripts\verify_real_dataset.py --dataset .\test_eeg.set
```

This uses a temporary work directory by default. It only calls `eeglab_init`, `eeglab_load_data`, `eeglab_info`, `eeglab_get_events`, and `eeglab_history`. It should not run filtering, ICA, source localization, or pipelines.

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

- `tool_count 40`
- `missing_required_arguments`

Full light ERP workflow smoke:

```powershell
python .\scripts\verify_light_erp_workflow.py --dataset .\test_eeg.set
```

This should save `.set/.fdt` outputs in a temporary directory and preserve the original dataset.

Before a large project or multi-subject analysis, run `eeglab_workflow_recommend` with the known research goal, project scale, stage, event labels, data shape, sampling rate, ICA state, and channel-location availability. If those facts are missing, use its `clarifying_questions`, `default_assumptions`, and `qc_gates` as the first planning artifact.

## First Real Dataset Check

After MATLAB and EEGLAB paths are configured, use a small `.set` file:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_info`
4. `eeglab_get_events`
5. `eeglab_history`

Do not start with ICA or `eeglab_pipeline`; first prove load and metadata inspection work.
