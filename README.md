# EEGLAB MCP Agent

EEGLAB MCP Agent is a local-first research workflow product for EEG projects. It turns EEGLAB's MATLAB/GUI capabilities into model-callable `eeglab_*` tools, then pairs those tools with a strict research skill for method selection, QC gates, event semantics, provenance, parameter records, and reproducible reporting.

Why use it:

- Faster than a generic MATLAB MCP for EEG: users ask for research actions instead of writing EEGLAB scripts.
- More reproducible than GUI-only work: tool calls carry JSON parameters, outputs, limitations, and protocol exports.
- Safer than an unconstrained agent: the skill requires goal/design intake, raw preservation, event semantics, montage checks, and plugin gates.
- More reliable than a skill alone: MCP tools execute local EEGLAB; the skill governs decisions and reporting.
- Local-first: EEG data stays on the user's machine. Cross-MCP work uses explicit file handoff only.

This is for EEG signal-processing research workflows, not clinical diagnosis.

## Product Layers

- `eeglab_mcp_server/`: Python stdio MCP server exposing the original 40 stable `eeglab_*` tools plus research planning/audit/export tools.
- `skills/eeglab-analysis/`: research-method guardrail skill for Codex or other skill-aware clients.
- MCP prompts/resources: built-in project intake, QC, routing, analysis-entry prompts, skill docs, workflow docs, and official reference anchors for clients that do not support skills.
- `configs/`: manual MCP client templates.
- `scripts/`: setup, doctor, uninstall, and framework verification helpers.

The skill and MCP connect through a fixed pattern: call `eeglab_project_plan` or `eeglab_workflow_recommend` first, use returned `qc_gates` and `blocking_conditions` as the checklist, run executable `eeglab_*` tools, then export/report exact parameters and limitations.

## Quick Start

From this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

The setup script backs up the Codex config before writing, registers the EEGLAB MCP as `eeglab`, and syncs the skill into the Codex skill directory. It does not modify any existing `matlab` MCP registration.

After setup, restart the IDE/client and ask for an EEGLAB/EEG task.

## What Setup Configures

For Codex, setup manages:

```text
C:\Users\<USER>\.codex\config.toml
C:\Users\<USER>\.codex\skills\eeglab-analysis
```

It writes only the `mcp_servers.eeglab` block and preserves `mcp_servers.matlab` if present.

Important paths:

- `EEGLAB_PATH`: local EEGLAB installation, default `D:\MATLAB_Tools\eeglab`.
- `MATLAB_ROOT`: local MATLAB root, default `D:\MATLAB`.
- `MATLAB_EXEC`: MATLAB executable, default `matlab`.
- `EEGLAB_WORK_DIR`: dedicated EEGLAB MCP work directory.

## C-Tier Product Surface

This package supports three ways for clients to learn the EEG workflow:

- MCP tools: executable `eeglab_*` tools for analysis work.
- MCP prompts/resources: built-in workflow prompts and read-only skill/reference resources for clients that support them.
- Skill files: persistent workflow policy for clients such as Codex that support skills.

Built-in prompts:

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

Built-in resources:

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/setup.md`
- `eeglab://official/references.md`

## Pairing With MATLAB MCP

This EEGLAB MCP can run alone or beside a general `matlab` MCP. Keep the names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Treat the two servers as workspace-isolated sessions. Do not assume `EEG`, `ALLEEG`, or other MATLAB variables are shared. Use file handoff for cross-server work: `.set/.fdt`, `.mat`, `.csv`, `.png`, or reports.

Use `eeglab` MCP first for EEG/EEGLAB work: loading, QC, event audit, preprocessing, ICA, ERP, ERSP/ITC, spectral/connectivity, STUDY, source localization, and EEGLAB figures. Use `matlab` MCP for custom MATLAB scripts, non-EEGLAB toolboxes, or follow-up calculations outside the EEGLAB MCP surface.

## Research Shortcuts

- `quick_qc`: load/QC/events/history only; never modifies data.
- `safe_erp`: ERP only after condition-trigger event semantics are confirmed.
- `segment_qc`: for datasets with start/end markers but no task-condition triggers.
- `study_ready_check`: multi-subject/BIDS/STUDY prerequisites before group statistics.
- `plugin_doctor`: check clean_rawdata, ICLabel, DIPFIT, BIDS, LIMO, and SIFT availability.

See `docs/user-workflows.md` and `docs/research-standard.md` for the research-standard policy and official EEGLAB reference anchors.

## Manual Configuration

Advanced users can skip setup and copy templates from `configs/`:

- `codex.config.toml`
- `claude_desktop_config.json`
- `cursor.mcp.json`
- `vscode.mcp.json`
- `openclaw.mcp.json`

Adjust paths before use. The server name should remain `eeglab`.

## Verification

Framework verification does not require EEG test data:

```powershell
python -B .\scripts\verify_framework.py
```

It checks Python syntax, config templates, skill files, MCP tools, MCP prompts/resources, and cleanliness. It intentionally does not restore or require sample EEG datasets.

For a first real EEG dataset, use a small local file and call:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Avoid ICA, filtering, source localization, and one-click pipelines until load/QC/provenance are verified.

## Uninstall

Dry-run first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

Then uninstall if desired:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

The uninstall script backs up the Codex config and skill directory before removing the `eeglab` registration or skill.
