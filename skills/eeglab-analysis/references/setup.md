# MCP + Skill Setup Reference

Use the repository README for first-time setup. This reference exists for agents and MCP clients that need the short operational contract after the project is already installed or cloned.

## User Entry Point

From the repository root, prefer the unified dispatcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```

Use `verify-online` when live official URL checks are required:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online
```

The dispatcher routes to the dedicated setup, verify, doctor, and uninstall scripts. New users should not need to call those lower-level scripts directly.

## MCP Registration Contract

Register the server as `eeglab`. The Skill, prompts, resources, and dual-MCP routing guidance assume that name.

Minimum environment values:

- `EEGLAB_PATH`
- `MATLAB_EXEC`
- `EEGLAB_WORK_DIR`
- optional `MATLAB_ROOT`
- optional `MATLAB_TIMEOUT`

Ready-to-edit templates are in `configs/` for Codex, Claude Desktop, Cursor, VS Code, and generic MCP clients. After editing a template, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```

## Skill Installation

Skill-aware clients should install or sync `skills/eeglab-analysis/`. The Skill teaches agents how to route EEG tasks through official EEGLAB/SCCN method gates, report limitations, and avoid unsupported claims.

MCP-only clients can read the same guidance through resources:

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/method-gates.md`
- `eeglab://official/tool-support-matrix.md`
- `eeglab://official/gate-policy.md`

## First Real Dataset Check

After MATLAB and EEGLAB paths are configured, use a small local `.set` file and stay read-only:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Do not begin with ICA, ASR, source localization, or `eeglab_pipeline`. First prove that load, metadata inspection, event inspection, and provenance reporting work.

## Pairing With MATLAB MCP

This server can run alone or beside a generic MATLAB MCP. Keep names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Assume the two servers have isolated MATLAB sessions. Use explicit file handoff, such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports. Keep `EEGLAB_WORK_DIR` dedicated to the EEGLAB MCP server.

## Research Safety Reminder

Before high-risk methods, use `eeglab_project_plan`, `eeglab_workflow_recommend`, `eeglab_event_semantics_audit`, and `eeglab_method_preflight`. Boundary, impedance, segment, and excluded markers are not condition triggers unless the user supplies a validated event codebook or sidecar.
