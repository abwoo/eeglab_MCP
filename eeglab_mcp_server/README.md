# EEGLAB MCP Server

Local-first MCP stdio server for MATLAB EEGLAB EEG research workflows. It exposes 37 legacy low-level `eeglab_*` tools for imported recording inspection, preprocessing, ICA, ERP/time-frequency analysis, visualization, source localization, STUDY workflows, and pipelines, plus 8 research workflow tools for planning, official method preflight, protocol export, plugin checks, QC, and event-semantics audit. The high-level tools are designed as a project system: recording/provenance audit, adaptive planning, official gates, QC gates, analysis branch selection, reporting, and controlled workflow evolution.

The repository is packaged as a standardized MCP + skill workflow:

- `eeglab_mcp_server/`: executable MCP server.
- `configs/`: client configuration templates for Codex, Claude Desktop, Cursor, VS Code, and generic OpenClaw-style MCP clients.
- `skills/eeglab-analysis/`: agent skill that teaches standardized EEG analysis workflows using the MCP tools.
- `scripts/`: lightweight setup and verification helpers.

This server runs MATLAB locally. It does not send EEG data to a remote service. It analyzes imported EEG recordings; it does not acquire EEG from amplifiers or replace lab acquisition notes, so reports should preserve source paths, sampling rate, montage/channel locations, event markers, and processing history.

## Requirements

- Python 3.10+
- MATLAB available either through:
  - MATLAB Engine for Python, preferred for persistent sessions
  - `matlab -batch`, fallback CLI mode
- EEGLAB installed locally
- Optional EEGLAB plugins depending on tools used, for example ICLabel, clean_rawdata, DIPFIT, BIOSIG, and BIDS import support

## Install

From the workspace root:

```powershell
python -m pip install -e .\eeglab_mcp_server
```

Run directly:

```powershell
python .\eeglab_mcp_server\server.py
```

Or via the console script after installation:

```powershell
eeglab-mcp-server
```

## Environment

Set these in your MCP client config:

```text
EEGLAB_PATH       Absolute path to the EEGLAB installation.
MATLAB_EXEC       MATLAB executable name or path. Defaults to matlab.
MATLAB_ROOT       Optional MATLAB root path for your own reference/config templates.
EEGLAB_WORK_DIR   Directory for CLI-mode temporary EEG state files and default pipeline output.
MATLAB_TIMEOUT    Per-call timeout in seconds. Defaults to 300.
EEGLAB_MCP_DEBUG  Set to 1 to include Python tracebacks in tool errors.
```

## Client Config Templates

Ready-to-copy examples live in the workspace `configs/` directory:

- `configs/codex.config.toml`
- `configs/claude_desktop_config.json`
- `configs/cursor.mcp.json`
- `configs/vscode.mcp.json`

This project intentionally does not modify global client config files such as `C:\Users\13803\.codex\config.toml`.

## Pairing With A General MATLAB MCP

The EEGLAB MCP server is independent: it starts MATLAB/EEGLAB itself and does not require a separate `matlab` MCP server. It can still run alongside one when both are registered under different names.

- Register this server as `eeglab`; keep any general MATLAB MCP registered as `matlab`.
- Prefer eeglab first for EEG-specific work: data loading, QC/provenance, events, ICA, ERP, time-frequency, STUDY, source localization, and EEGLAB figures.
- Use the matlab MCP for custom `.m` scripts, generic MATLAB arrays/statistics, and non-EEGLAB toolboxes.
- Treat the servers as workspace-isolated MATLAB sessions. Variables loaded in `eeglab` are not assumed visible in `matlab`.
- Use explicit file handoff for cross-server work, for example `.set/.fdt`, `.mat`, `.csv`, `.png`, or report files.
- Keep `EEGLAB_WORK_DIR` distinct from other MCP scratch folders and avoid simultaneous writes to the same output path.

## Product Setup

For Codex, the product entrypoint is the repository-level setup script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

The setup script registers this server as `eeglab`, syncs the skill, and leaves any separate `matlab` MCP registration intact. Manual templates remain in `configs/`.

## Skill Setup

The project-local skill is in `skills/eeglab-analysis/`. For Codex, copy or symlink it into:

```powershell
C:\Users\<USER>\.codex\skills\eeglab-analysis
```

Other IDE agents can use the same `SKILL.md` and `references/` files as their EEG workflow guide. The skill tells the agent how to choose tool sequences, report parameters, avoid overclaiming, and recover from MCP tool errors.

## Execution Modes

The server detects MATLAB execution mode on first tool call.

- Engine mode: uses MATLAB Engine for Python and keeps one MATLAB session alive. EEGLAB initialization can be reused after a successful init.
- CLI mode: uses `matlab -batch` for each call. Because each CLI call is a new MATLAB process, the server reloads/saves the current `EEG` variable through a temporary `.mat` state file and injects `eeglab nogui` for each call.

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

Examples include `unknown_tool`, `missing_required_arguments`, `invalid_arguments`, `invalid_tool_contract`, MATLAB backend codes such as `matlab_timeout`, and `tool_execution_error`.

Required-argument, type, enum, array-length, cross-field contract, and analysis-window checks are handled inside `call_tool` so MCP clients receive the same JSON error shape instead of SDK-generated plain-text validation errors. Public tool schemas are intentionally description-oriented; the server keeps stricter internal schemas for validation. Contract checks catch dependent or mutually exclusive arguments before MATLAB runs, for example bandpass filters without valid low/high cutoffs, channel rereference without `ref_channel`, unsafe light-workflow output filenames, and workflow windows outside the requested epoch.

High-level workflow tools also declare MCP `outputSchema` and return `structuredContent` while preserving the same JSON inside text content for older clients. High-risk processing tools evaluate the local EEGLAB/SCCN official claim map before MATLAB execution; blocked gates return JSON error code `official_gate_blocked` unless the user supplies an explicit override reason.

## Research Workflow Tools

- `eeglab_qc_report`: summarize loaded recording dimensions, event provenance, ICA state, channel-location coverage, processing-history availability, and QC/provenance hints without modifying data.
- `eeglab_workflow_recommend`: recommend non-destructive project phases, clarifying questions, conservative defaults, adaptive decision rules, QC gates, self-evolution hooks, and minimum report fields from research goal, analysis type, event labels, sampling rate, ICA state, data shape, project scale, and channel-location availability.
- `eeglab_erp_light_workflow`: run a smoke-tested ERP chain: load, inspect, bandpass filter, epoch, baseline-correct, compute ERP summary, and save a processed copy. It refuses to overwrite the input dataset, requires `output_filename` to be a leaf `.set` filename inside `output_dir`, and reports both processed `.set` and `.fdt` paths.
- `eeglab_project_plan`: build a research-grade project plan with blocking conditions, not-recommended actions, QC gates, quick modes, and official reference anchors.
- `eeglab_method_preflight`: evaluate official EEGLAB/SCCN method gates before high-risk processing without running MATLAB. It returns `gate_status`, missing requirements, `safe_next_step`, and `source_claim_ids`.
- `eeglab_event_semantics_audit`: classify markers as condition triggers, boundaries, impedance/QC annotations, segment markers, excluded labels, or candidate triggers before epoching.
- `eeglab_plugin_check`: probe the official plugin matrix in the local MATLAB/EEGLAB path, including clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, MFF-matlab-io, NWB-io, BVA-io, HEDTools, firfilt, CleanLine, Zapline-Plus, AMICA, Picard, LIMO, SIFT, groupSIFT, NFT, and NSGportal. The response includes support level, claim IDs, dependent profiles, functions checked, and next steps for missing plugins.
- `eeglab_protocol_export`: render Markdown/JSON protocol text and optionally write it to a local file.

## MCP Prompts And Resources

In addition to tools, the server exposes read-only guidance for clients that support MCP prompts/resources.

Prompts:

- `eeglab_project_intake`
- `eeglab_strict_qc_protocol`
- `eeglab_dual_mcp_routing`
- `eeglab_report_template`
- `eeglab_erp_research_entry`
- `eeglab_resting_research_entry`
- `eeglab_time_frequency_entry`
- `eeglab_ica_cleanup_entry`
- `eeglab_bids_study_entry`
- `eeglab_source_connectivity_entry`

Resources:

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/setup.md`
- `eeglab://references/official-method-map.md`
- `eeglab://references/gate-policy.md`
- `eeglab://references/method-gates.md`
- `eeglab://references/acquisition-to-derivatives.md`
- `eeglab://references/event-semantics.md`
- `eeglab://references/preprocessing-decision-tree.md`
- `eeglab://references/ica-iclabel-policy.md`
- `eeglab://references/bids-study-policy.md`
- `eeglab://references/source-policy.md`
- `eeglab://references/report-protocol-templates.md`
- `eeglab://references/statistics-reporting.md`
- `eeglab://official/references.md`
- `eeglab://official/topic-index.md`
- `eeglab://official/support-matrix.md`
- `eeglab://official/tool-support-matrix.md`
- `eeglab://official/method-map.md`
- `eeglab://official/gate-policy.md`
- `eeglab://official/plugin-map.md`
- `eeglab://official/plugin-matrix.md`
- `eeglab://official/risk-matrix.md`
- `eeglab://official/report-field-matrix.md`

These are guidance surfaces only; they do not modify EEG data or MATLAB state.

## Lightweight Verification

These checks validate packaging and MCP protocol behavior without EEG test data:

```powershell
python -B -m py_compile .\eeglab_mcp_server\server.py .\eeglab_mcp_server\schemas.py .\eeglab_mcp_server\workflows.py
python -c "import tomllib; tomllib.load(open('eeglab_mcp_server/pyproject.toml','rb')); print('pyproject ok')"
python -m pip install -e .\eeglab_mcp_server
python -B .\scripts\verify_framework.py
python .\scripts\verify_official_alignment.py
python .\scripts\verify_official_alignment.py --online
```

The framework verification asserts the registry-defined 37 legacy low-level tools and 8 research workflow tools are present, prompts/resources are exposed, config templates parse, skill/reference files contain research-standard terms, and no bundled EEG test data is present. It also treats the `evals.xml` contract as a machine-checkable workflow specification: required/forbidden tools, official gate assertions, source claim IDs, resources, and protocol report-field requirements must stay synchronized with the registry and official alignment map. Official-alignment verification checks claim/profile/tool/resource synchronization, support/plugin/report matrices, method-gate behavior, and, with `--online`, live official EEGLAB/SCCN/BIDS URLs.

## MCP Inspector

You can also inspect the stdio server with MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector python .\eeglab_mcp_server\server.py
```

Use Inspector to confirm `tools/list` matches the registry-defined 45 exposed tools, workflow tools expose `outputSchema`, and error paths return JSON text content.

MCP stdio smoke test:

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
            print(len(tools.tools))
            result = await session.call_tool("eeglab_load_data", {})
            print(result.content[0].text)

asyncio.run(main())
'@ | python -
```

## Optional Real EEGLAB Smoke Test

When MATLAB and EEGLAB are ready, use a small local dataset and call:

1. `eeglab_init`
2. `eeglab_load_data` with an absolute `.set` path
3. `eeglab_info`
4. `eeglab_qc_report`
5. `eeglab_history`

Avoid full ICA, filtering, or one-click pipelines for a first smoke test because they can be slow and plugin-dependent.

## Evals

`evals.xml` contains task-level evaluation prompts. They are intended to check whether a model can choose and chain the MCP tools correctly, including missing-goal planning, provenance-first reporting, group/STUDY assumptions, and self-evolution behavior; they are not an automated unit test runner.
