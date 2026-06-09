# EEGLAB MCP Agent

Local-first EEGLAB research agent package for MCP clients. It combines:

- `eeglab_mcp_server/`: Python stdio MCP server exposing 40 stable `eeglab_*` tools.
- `skills/eeglab-analysis/`: strict EEG research workflow skill.
- `configs/`: manual MCP client templates.
- `scripts/`: setup, doctor, uninstall, and framework verification helpers.

The server runs MATLAB/EEGLAB locally. EEG data is not sent to a remote service. The package is designed for reproducible EEG research workflows, not clinical diagnosis.

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

Built-in resources:

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/setup.md`

## Pairing With MATLAB MCP

This EEGLAB MCP can run alone or beside a general `matlab` MCP. Keep the names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Treat the two servers as workspace-isolated sessions. Do not assume `EEG`, `ALLEEG`, or other MATLAB variables are shared. Use file handoff for cross-server work: `.set/.fdt`, `.mat`, `.csv`, `.png`, or reports.

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
