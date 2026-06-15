# EEGLAB MCP Agent

[中文](README.zh-CN.md) | [Repository Entry](README.md)

EEGLAB MCP Agent is a local-first MCP server plus a research workflow Skill for MATLAB EEGLAB. It lets AI assistants call EEGLAB through structured `eeglab_*` tools while using a research-method policy layer for planning, QC gates, event semantics, official-method preflight, provenance, and reproducible protocol export.

It is not limited to Codex. Any client that supports MCP stdio can use the MCP server, including Codex, Claude Desktop, VS Code MCP integrations, Cursor, and other MCP-capable IDE or agent environments. Clients that support Skills can also install the Skill directly; clients that do not support Skills can still read the same guidance through MCP prompts and resources.

This project supports EEG signal-processing research workflows. It is not a clinical diagnosis system and must not be used for clinical claims.

## Release Facts

- Project/server version: `1.0`.
- MCP tool surface: 37 legacy low-level `eeglab_*` tools plus 8 research workflow tools, for 45 exposed tools.
- MCP guidance surface: 10 prompts and 25 read-only resources.
- Eval contract: 55 machine-checkable workflow evals.
- Official alignment map: 47 official claims and 39 method profiles.
- Runtime model: local-first stdio MCP; EEG data stays on the user's machine.

The counts above are checked by the framework and official-alignment verifiers.

## What This Repository Provides

### MCP Server

The MCP server is the execution layer. It runs locally, starts MATLAB/EEGLAB through MATLAB Engine or `matlab -batch`, and exposes `eeglab_*` tools to an MCP client.

Use the MCP server for:

- Loading EEGLAB datasets and supported EEG import formats.
- Inspecting sampling rate, data shape, events, history, channel locations, and provenance.
- Running gated preprocessing and analysis steps such as filtering, resampling, rereferencing, ICA, ICLabel, ERP, time-frequency, topography, source, STUDY, and pipeline tools.
- Running research workflow tools such as project planning, method preflight, plugin checks, event-semantics audit, and protocol export.

### Skill

The Skill is the method layer. It teaches an assistant how to use the MCP server safely and reproducibly for EEG research.

Use the Skill for:

- Choosing the right workflow before calling tools.
- Asking for missing research goals, event-code maps, acquisition metadata, montage facts, and output requirements.
- Blocking unsafe analysis when event semantics, channel locations, plugin prerequisites, or official method gates are missing.
- Reporting parameters, generated files, gate results, source claim IDs, limitations, and override decisions.

The Skill is stored as a normal `SKILL.md` with supporting reference files. Skill-aware clients can install or import it. Non-Skill clients can still access equivalent guidance through MCP prompts/resources exposed by the server.

### Prompts And Resources

The MCP server separates the product surface clearly:

- Tools execute actions.
- Prompts provide workflow templates.
- Resources expose read-only Skill/reference/official-alignment documents.

Prompts and resources do not run MATLAB and do not modify EEG data.

## Repository Layout

- `eeglab_mcp_server/`: Python stdio MCP server package.
- `skills/eeglab-analysis/`: Skill instructions and reference documents.
- `configs/`: MCP client configuration templates for Codex, Claude Desktop, Cursor, VS Code, and generic MCP clients.
- `docs/`: research standards, official support matrices, gate policies, plugin maps, risk maps, and report-field maps.
- `scripts/`: setup, doctor, uninstall, framework verifier, and official-alignment verifier.

## Requirements

- Python 3.10 or newer.
- MATLAB installed locally.
- EEGLAB installed locally.
- Optional EEGLAB plugins depending on the workflow, such as clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, HEDTools, LIMO, SIFT, AMICA, RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, and NSGportal.

The server can run without a separate generic MATLAB MCP. It can also run beside one when both are registered under different names.

## Quick Start

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

The setup script is mainly for Codex-style local setup: it backs up the user config, registers the MCP server as `eeglab`, and syncs the Skill into the local Skill directory. It does not remove or overwrite a separate generic `matlab` MCP registration.

For Claude Desktop, VS Code, Cursor, or another MCP client, use the templates in `configs/` and adjust local paths.

Client notes:

- Codex: use the setup script for automatic MCP registration and Skill sync, or copy the template manually.
- Claude Desktop: merge the Claude template into the local Claude Desktop MCP config and restart Claude Desktop.
- VS Code and Cursor: use the matching MCP template, keep the server name `eeglab`, and restart or reload the MCP client.
- Other MCP clients: use the generic template and point it at the local Python server entry point.

## Manual MCP Setup

Every MCP client needs the same basic server shape:

```json
{
  "command": "python",
  "args": ["C:\\path\\to\\eeglab_MCP\\eeglab_mcp_server\\server.py"],
  "env": {
    "EEGLAB_PATH": "D:\\MATLAB_Tools\\eeglab",
    "MATLAB_EXEC": "matlab",
    "MATLAB_ROOT": "D:\\MATLAB",
    "EEGLAB_WORK_DIR": "D:\\eeglab_mcp_work"
  }
}
```

Use the server name `eeglab`. The Skill, prompts, and docs assume this name when describing tool routing.

Templates are provided for:

- Codex: `configs/codex.config.toml`
- Claude Desktop: `configs/claude_desktop_config.json`
- Cursor: `configs/cursor.mcp.json`
- VS Code: `configs/vscode.mcp.json`
- Generic/OpenClaw-style clients: `configs/openclaw.mcp.json`

Adjust:

- `EEGLAB_PATH`: local EEGLAB installation directory.
- `MATLAB_EXEC`: `matlab` or the absolute path to `matlab.exe`.
- `MATLAB_ROOT`: local MATLAB root if your client/template uses it.
- `EEGLAB_WORK_DIR`: a dedicated EEGLAB MCP work directory.
- `MATLAB_TIMEOUT`: optional per-call timeout in seconds.

## Skill Setup

The Skill lives in `skills/eeglab-analysis/`.

The Skill package contains:

- `SKILL.md`: the entry instruction that tells an assistant when to use the EEGLAB MCP server and how to route EEG work.
- `references/workflows.md`: concrete workflow recipes for QC, ERP, spectral, ERSP/ITC, ICA cleanup, BIDS/STUDY, source, plugin-dependent guidance, and report-only recovery.
- `references/tools.md`: tool groups, recommended call order, common parameters, and error-recovery rules.
- `references/method-gates.md` and `references/gate-policy.md`: method preflight rules for high-risk EEG processing.
- Policy references for acquisition metadata, event semantics, preprocessing, ICA/ICLabel, BIDS/STUDY, source localization, statistics/reporting, and protocol export.

For Skill-aware clients:

1. Install or import the whole `skills/eeglab-analysis/` directory.
2. Keep `SKILL.md` and the `references/` directory together.
3. Trigger it for EEG/EEGLAB tasks such as recording inspection, preprocessing, ICA/ICLabel, ERP, ERSP/ITC, spectral analysis, connectivity, BIDS/STUDY, source localization, plugin checks, or protocol export.

For Codex, the setup script can sync the Skill automatically. Manual installs can copy the directory into the user's Codex Skill directory.

For Claude Desktop, VS Code, Cursor, or other agent environments:

- If the client has a Skill/plugin/instructions feature, import the `eeglab-analysis` Skill directory there.
- If the client only supports MCP, use the MCP prompts and resources exposed by the server. They contain the same core workflow policy and reference material.
- If the client supports custom system/project instructions, include the Skill entry rule: use the local `eeglab` MCP server for EEG/EEGLAB work, call planning/preflight tools before high-risk processing, preserve raw data, and report gate results and limitations.

The Skill is not an executor. It does not run MATLAB. It is the policy that tells the assistant when and how to call MCP tools.

Practical trigger examples:

- "Inspect this `.set` recording and tell me whether it is ready for ERP."
- "Plan a resting-state spectral workflow but do not modify the raw data."
- "Check whether this dataset can run ICA/ICLabel safely."
- "Audit event labels before epoching."
- "Export a methods/protocol report with blocked gates and limitations."

When the Skill is active, the assistant should not jump straight to an EEGLAB operation. It should first establish the research goal, dataset state, event semantics, channel-location coverage, plugin prerequisites, derivative-output path, and reporting requirements.

MCP-only fallback:

- Read `eeglab://skill/SKILL.md` for the Skill entry policy.
- Read `eeglab://references/workflows.md` for workflow recipes.
- Read `eeglab://references/tools.md` for tool groups and expected call order.
- Read `eeglab://references/method-gates.md` and `eeglab://official/gate-policy.md` before high-risk processing.
- Use prompts such as `eeglab_project_intake`, `eeglab_strict_qc_protocol`, and `eeglab_report_template` when the client supports MCP prompts.

## How To Use The MCP Tools

A conservative first dataset check should be read-only:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Do not begin with ICA, source localization, one-click pipelines, or destructive preprocessing. First prove that the dataset loads and that sampling rate, channels, events, history, and provenance are interpretable.

For a real analysis, use this pattern:

1. Plan: call `eeglab_project_plan` or `eeglab_workflow_recommend`.
2. Audit: inspect recording metadata, channel locations, events, and history.
3. Preflight: call `eeglab_method_preflight` before high-risk methods.
4. Execute: call low-level `eeglab_*` tools only after gates pass or an explicit override reason is recorded.
5. Report: call `eeglab_protocol_export` with gate results, source claim IDs, report fields, overrides, parameters, output files, and limitations.

## Research Workflow Tools

The 8 research workflow tools are the main product layer for agentic use:

- `eeglab_qc_report`: read-only recording, event, ICA, channel-location, and provenance summary.
- `eeglab_workflow_recommend`: adaptive workflow recommendation from project facts.
- `eeglab_erp_light_workflow`: smoke-tested ERP chain into a new derivative output path.
- `eeglab_project_plan`: research-grade plan with blockers, gates, quick modes, and official references.
- `eeglab_method_preflight`: official method gate evaluation before high-risk processing.
- `eeglab_event_semantics_audit`: classify markers before epoching or event-locked analysis.
- `eeglab_plugin_check`: check local plugin availability and support level.
- `eeglab_protocol_export`: export Markdown/JSON protocol reports with gates, claims, overrides, report fields, and limitations.

## High-Risk Gate Policy

High-risk processing is blocked until prerequisites are explicit. This includes:

- Filtering, resampling, rereferencing, and line-noise cleanup.
- ASR/clean_rawdata.
- ICA, ICLabel, component flagging, and component removal.
- Epoching, ERP, ERSP/ITC, and time-frequency analysis.
- Resting-state spectral/connectivity claims.
- Source localization and DIPFIT.
- BIDS/STUDY/group analysis.
- LIMO, SIFT, AMICA, RELICA, ROIconnect, EEGstats, NSG, and other plugin-dependent workflows.

When a gate is blocked, the assistant should stop, report missing requirements and `source_claim_ids`, and ask for missing facts. If the user explicitly overrides, the override reason must be recorded and reported.

## Pairing With A Generic MATLAB MCP

This project can coexist with a general MATLAB MCP.

Use this naming convention:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Use `eeglab` first for EEG loading, QC, event audit, EEGLAB preprocessing, ICA, ERP, time-frequency, source, STUDY, and EEGLAB figures. Use `matlab` for custom `.m` scripts, generic matrix/statistical code, or non-EEGLAB toolboxes.

Treat the two servers as isolated MATLAB sessions. Do not assume variables are shared. Use explicit file handoff such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports.

## Reporting Contract

`eeglab_protocol_export` is the research report exit. Reports should preserve:

- Input and output paths.
- Sampling rate, duration, channel count, reference, montage, channel-location coverage, event labels, event counts, and history availability.
- Processing parameters: filter cutoffs, line-noise settings, ASR threshold, rereference, ICA algorithm, ICLabel thresholds, epoch/baseline windows, frequency windows, rejected channels/epochs/components, and output files.
- `gate_results`, `method_profile_id`, `gate_status`, missing requirements, and critical missing requirements.
- `source_claim_ids` from official alignment checks.
- `override_used`, `override_reason`, and acknowledged blocked requirements.
- Report-field matrix coverage and limitations.

The protocol exporter must not overwrite EEG data files such as `.set`, `.fdt`, `.eeg`, `.vhdr`, `.vmrk`, `.edf`, `.bdf`, or `.cnt`.

## Verification

Run framework checks without EEG test data:

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
```

Run release-level checks:

```powershell
python -B -m py_compile .\eeglab_mcp_server\workflows.py .\eeglab_mcp_server\schemas.py .\scripts\verify_framework.py .\scripts\verify_official_alignment.py
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

Optional live official-link verification:

```powershell
python .\scripts\verify_official_alignment.py --online
```

## Uninstall

Dry-run first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

Then uninstall if desired:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

The uninstall script backs up the Codex config and Skill directory before removing the `eeglab` registration or Skill.
