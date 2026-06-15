# EEGLAB MCP Agent

[中文](README.zh-CN.md)

EEGLAB MCP Agent is a local-first MCP server and research workflow Skill for MATLAB EEGLAB. It lets AI assistants call EEGLAB through structured `eeglab_*` tools, while the Skill and MCP guidance surfaces keep EEG work aligned with research-grade planning, QC gates, event semantics, provenance, method preflight, and reproducible reporting.

This is not a Codex-specific project. Any MCP stdio client can use the server, including Codex, Claude Desktop, VS Code MCP integrations, Cursor, and other MCP-capable IDE or agent environments. Skill-aware clients can install the Skill directly. MCP-only clients can still use the same policy through MCP prompts and resources.

This project supports EEG signal-processing research workflows. It is not a clinical diagnosis system and must not be used for clinical claims.

## Table Of Contents

- [What This Is](#what-this-is)
- [Who Can Use It](#who-can-use-it)
- [Quick Start](#quick-start)
- [MCP Usage](#mcp-usage)
- [Skill Usage](#skill-usage)
- [Research Safety Gates](#research-safety-gates)
- [Reporting And Reproducibility](#reporting-and-reproducibility)
- [Verification](#verification)
- [Uninstall](#uninstall)

## What This Is

### Simple Version

Install the local `eeglab` MCP server, connect it to your AI client, and let the assistant use EEGLAB tools with EEG research guardrails.

### Detailed Version

The project has three product layers:

- MCP tools execute local EEGLAB/MATLAB work through structured `eeglab_*` calls.
- The Skill teaches an assistant how to choose workflows, stop at unsafe gates, preserve provenance, and report limitations.
- MCP prompts and resources expose the same workflow templates and reference documents to clients that do not load Skills directly.

Current release facts:

- Project/server version: `1.0`.
- MCP tool surface: 37 legacy low-level tools plus 8 research workflow tools, for 45 exposed tools.
- MCP guidance surface: 10 prompts and 25 read-only resources.
- Eval contract: 56 machine-checkable workflow evals.
- Official alignment map: 47 official claims and 39 method profiles.
- Runtime model: local-first stdio MCP; EEG data stays on the user's machine.

## Who Can Use It

### Simple Version

Use it with any client that can launch a local stdio MCP server. Codex is supported, but it is only one possible client.

### Detailed Version

Supported client patterns:

- MCP-only clients: configure the local server as `eeglab`, then use MCP tools, prompts, and resources.
- Skill-aware clients: install the `eeglab-analysis` Skill in addition to the MCP server.
- Custom-instruction clients: add a project instruction that EEG/EEGLAB work must route through the local `eeglab` MCP server and must run planning/preflight before high-risk analysis.

Practical client examples:

- Codex: use the setup script or the Codex config template.
- Claude Desktop: merge the Claude Desktop MCP template and restart the app.
- VS Code and Cursor: use the matching MCP template and reload the MCP client.
- Other MCP clients: use the generic template and point it at the local Python server entry point.

## Quick Start

### Simple Version

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

Restart your client and ask for an EEG or EEGLAB task.

### Detailed Version

The setup script is convenient for Codex-style local setup. It backs up the user config, registers the MCP server as `eeglab`, and syncs the Skill into the local Skill directory. It does not remove or overwrite a separate generic `matlab` MCP registration.

For Claude Desktop, VS Code, Cursor, or another MCP client, copy a template from the client configuration examples and adjust these values:

- `EEGLAB_PATH`: local EEGLAB installation directory.
- `MATLAB_EXEC`: `matlab` or the absolute path to `matlab.exe`.
- `MATLAB_ROOT`: local MATLAB root if your client/template uses it.
- `EEGLAB_WORK_DIR`: a dedicated EEGLAB MCP work directory.
- `MATLAB_TIMEOUT`: optional per-call timeout in seconds.

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

Keep the server name as `eeglab`. The Skill, prompts, resources, and workflow examples use that name when describing tool routing.

## MCP Usage

### Simple Version

For a first dataset check, use a read-only sequence:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Do not start with ICA, source localization, one-click pipelines, or destructive preprocessing.

### Detailed Version

For a real analysis, use this workflow:

1. Plan: call `eeglab_project_plan` or `eeglab_workflow_recommend`.
2. Audit: inspect recording metadata, channel locations, events, history, and provenance.
3. Preflight: call `eeglab_method_preflight` before high-risk methods.
4. Execute: call low-level `eeglab_*` tools only after gates pass or an explicit override reason is recorded.
5. Report: call `eeglab_protocol_export` with gate results, source claim IDs, report fields, overrides, parameters, output files, and limitations.

The main research workflow tools are:

- `eeglab_qc_report`: read-only recording, event, ICA, channel-location, and provenance summary.
- `eeglab_workflow_recommend`: adaptive workflow recommendation from project facts.
- `eeglab_erp_light_workflow`: smoke-tested ERP chain into a derivative output path.
- `eeglab_project_plan`: research-grade plan with blockers, gates, quick modes, and official references.
- `eeglab_method_preflight`: official method gate evaluation before high-risk processing.
- `eeglab_event_semantics_audit`: marker classification before epoching or event-locked analysis.
- `eeglab_plugin_check`: local plugin availability and support-level check.
- `eeglab_protocol_export`: Markdown/JSON protocol reports with gates, claims, overrides, report fields, and limitations.

If you also use a generic MATLAB MCP, keep the server names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Treat the two servers as isolated MATLAB sessions. Use explicit file handoff, such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports.

## Skill Usage

### Simple Version

Install the `eeglab-analysis` Skill when your client supports Skills or project instruction packs. The Skill tells the assistant how to use MCP tools without skipping EEG research safeguards.

### Detailed Version

The Skill package contains:

- `SKILL.md`: entry instructions for when to use the EEGLAB MCP server and how to route EEG work.
- Workflow recipes for QC, ERP, spectral, ERSP/ITC, ICA cleanup, BIDS/STUDY, source, plugin-dependent guidance, and report-only recovery.
- Tool guidance for call order, common parameters, and error recovery.
- Method gate policy for high-risk EEG processing.
- References for acquisition metadata, event semantics, preprocessing, ICA/ICLabel, BIDS/STUDY, source localization, statistics/reporting, and protocol export.

For Skill-aware clients:

1. Install or import the whole `eeglab-analysis` Skill directory.
2. Keep `SKILL.md` and the reference documents together.
3. Trigger it for EEG/EEGLAB tasks such as recording inspection, preprocessing, ICA/ICLabel, ERP, ERSP/ITC, spectral analysis, connectivity, BIDS/STUDY, source localization, plugin checks, or protocol export.

For MCP-only clients:

- Read `eeglab://skill/SKILL.md` for the Skill entry policy.
- Read `eeglab://references/workflows.md` for workflow recipes.
- Read `eeglab://references/tools.md` for tool groups and expected call order.
- Read `eeglab://references/method-gates.md` and `eeglab://official/gate-policy.md` before high-risk processing.
- Use prompts such as `eeglab_project_intake`, `eeglab_strict_qc_protocol`, and `eeglab_report_template` when the client supports MCP prompts.

Practical trigger examples:

- "Inspect this `.set` recording and tell me whether it is ready for ERP."
- "Plan a resting-state spectral workflow but do not modify the raw data."
- "Check whether this dataset can run ICA/ICLabel safely."
- "Audit event labels before epoching."
- "Export a methods/protocol report with blocked gates and limitations."

The Skill is not an executor. It does not run MATLAB. It is the policy layer that tells the assistant when and how to call MCP tools.

## Research Safety Gates

### Simple Version

Run method preflight before high-risk EEG steps. If a gate is blocked, stop and report what is missing.

### Detailed Version

High-risk processing is blocked until prerequisites are explicit. This includes:

- Filtering, resampling, rereferencing, and line-noise cleanup.
- ASR/clean_rawdata.
- ICA, ICLabel, component flagging, and component removal.
- Epoching, ERP, ERSP/ITC, and time-frequency analysis.
- Resting-state spectral/connectivity claims.
- Source localization and DIPFIT.
- BIDS/STUDY/group analysis.
- LIMO, SIFT, AMICA, RELICA, ROIconnect, EEGstats, NSG, and other plugin-dependent workflows.

Event semantics are a hard gate. Boundary, impedance, segment start/end, and excluded markers must not be treated as condition triggers unless the user supplies a validated codebook or event sidecar.

If a user explicitly overrides a blocked gate, the assistant must record `override_used`, `override_reason`, blocked requirements, source claim IDs, and limitations in the final report.

## Reporting And Reproducibility

### Simple Version

Use `eeglab_protocol_export` to export the final Markdown or JSON protocol.

### Detailed Version

Reports should preserve:

- Input and output paths.
- Sampling rate, duration, channel count, reference, montage, channel-location coverage, event labels, event counts, and history availability.
- Processing parameters: filter cutoffs, line-noise settings, ASR threshold, rereference, ICA algorithm, ICLabel thresholds, epoch/baseline windows, frequency windows, rejected channels/epochs/components, and output files.
- `gate_results`, `method_profile_id`, `gate_status`, missing requirements, and critical missing requirements.
- `source_claim_ids` from official alignment checks.
- `override_used`, `override_reason`, and acknowledged blocked requirements.
- Report-field matrix coverage and limitations.

The protocol exporter must not overwrite EEG data files such as `.set`, `.fdt`, `.eeg`, `.vhdr`, `.vmrk`, `.edf`, `.bdf`, or `.cnt`.

## Verification

### Simple Version

Run the two project verifiers:

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
```

### Detailed Version

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

### Simple Version

Run the uninstall script with `-DryRun` first, then run it for real if the plan looks correct.

### Detailed Version

Dry-run first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

Then uninstall if desired:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

The uninstall script backs up the Codex config and Skill directory before removing the `eeglab` registration or Skill.
