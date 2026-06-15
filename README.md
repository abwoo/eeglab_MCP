# EEGLAB MCP Agent

[中文](README.zh-CN.md)

EEGLAB MCP Agent is a local-first MCP server and research workflow Skill for MATLAB EEGLAB. It lets MCP-capable assistants use structured `eeglab_*` tools while preserving EEG research safeguards: provenance, event semantics, method preflight, official EEGLAB/SCCN alignment, and reproducible reporting.

This project is for EEG signal-processing research workflows. It is not a clinical diagnosis system and must not be used for clinical claims.

## Quick Start

From the repository root, run the dispatcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```

Restart your MCP client, then ask for an EEG or EEGLAB task.

Prerequisites:

- Python 3.10+
- MATLAB available as `matlab` or an absolute `matlab.exe` path
- EEGLAB installed locally
- Optional EEGLAB plugins for plugin-dependent workflows, such as clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, and import/export plugins

## Minimal MCP Config

Register the server as `eeglab`. The Skill, prompts, resources, and workflow docs assume that name.

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

Ready-to-edit templates are in `configs/` for Codex, Claude Desktop, Cursor, VS Code, and generic MCP clients.

## First Dataset Check

For a new recording, start read-only:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Do not start with ICA, source localization, one-click pipelines, or destructive preprocessing. Run planning and method preflight first.

## Common Commands

| Task | Command |
| --- | --- |
| Show help | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 help` |
| Preview setup | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun` |
| Install/register | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup` |
| Verify local framework and official alignment | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify` |
| Verify live official links too | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online` |
| Check local client/MATLAB environment | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor` |
| Preview uninstall | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -DryRun -RemoveSkill` |

The dispatcher forwards to dedicated setup, verify, doctor, and uninstall scripts. Automation may call those lower-level scripts directly, but new users should start with `eeglab_agent.ps1`.

## What You Get

- 45 exposed MCP tools: 37 low-level EEGLAB tool wrappers plus 8 research workflow tools.
- 10 MCP prompts and 25 read-only MCP resources for clients that support guidance surfaces.
- 47 official alignment claims and 39 method profiles mapped to EEGLAB/SCCN and related standards.
- 56 machine-checkable workflow evals covering gates, reports, plugin gaps, and failure recovery.
- A local-first runtime: EEG data stays on the user's machine.

## Client And Skill Usage

Any stdio MCP client can use the server. Codex, Claude Desktop, VS Code MCP integrations, Cursor, and other MCP-capable IDEs can all register it as `eeglab`.

Skill-aware clients should install the `eeglab-analysis` Skill. MCP-only clients can read the same policy through MCP resources:

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/method-gates.md`
- `eeglab://official/gate-policy.md`

If you also use a general MATLAB MCP, keep names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Treat the two servers as isolated MATLAB sessions and pass data through explicit files such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports.

## Research Workflow

Use the workflow tools before high-risk analysis:

1. Plan with `eeglab_project_plan` or `eeglab_workflow_recommend`.
2. Audit metadata, channel locations, events, history, and provenance.
3. Preflight high-risk methods with `eeglab_method_preflight`.
4. Execute low-level `eeglab_*` tools only after gates pass or after an explicit override reason is recorded.
5. Export methods/protocol text with `eeglab_protocol_export`.

Core workflow tools:

- `eeglab_qc_report`: read-only recording, event, ICA, channel-location, and provenance summary.
- `eeglab_workflow_recommend`: adaptive workflow recommendation from project facts.
- `eeglab_project_plan`: research-grade plan with blockers, gates, quick modes, and official references.
- `eeglab_method_preflight`: official method gate evaluation before high-risk processing.
- `eeglab_event_semantics_audit`: marker classification before epoching or event-locked analysis.
- `eeglab_plugin_check`: local plugin availability and support-level check.
- `eeglab_protocol_export`: Markdown/JSON protocol reports with gates, claims, overrides, report fields, and limitations.
- `eeglab_erp_light_workflow`: smoke-tested ERP chain into a derivative output path.

## Official Alignment And Safety

The default policy is conservative: audit first, gate high-risk methods, preserve raw data, write derivatives, and report limitations.

High-risk processing includes filtering, resampling, rereferencing, line-noise cleanup, ASR/clean_rawdata, ICA, ICLabel, component removal, epoching, ERP, ERSP/ITC, spectral/connectivity claims, source localization, BIDS/STUDY, LIMO, SIFT, AMICA, RELICA, ROIconnect, EEGstats, NSG, and other plugin-dependent workflows.

Event semantics are a hard gate. Boundary, impedance, segment start/end, and excluded markers must not be treated as condition triggers unless the user supplies a validated codebook or event sidecar.

Unsupported official plugins or advanced methods are indexed and explained as `indexed_only` or guidance-only. They are not treated as executable support unless a dedicated MCP workflow, method gate, report template, and eval coverage exist.

## Reporting And Reproducibility

Final reports should include:

- input and derivative output paths
- sampling rate, duration, channel count, reference, montage, channel-location coverage, event labels/counts, and history availability
- filter, line-noise, ASR, rereference, ICA, ICLabel, epoch, baseline, frequency, rejection, and output parameters
- `gate_results`, `method_profile_id`, `gate_status`, missing requirements, and critical missing requirements
- `source_claim_ids`, plugin status, override status, report-field coverage, and limitations

The protocol exporter must not overwrite EEG data files such as `.set`, `.fdt`, `.eeg`, `.vhdr`, `.vmrk`, `.edf`, `.bdf`, or `.cnt`.

## Repository Map

| Path | Purpose |
| --- | --- |
| `eeglab_mcp_server/` | Executable MCP server, tool schemas, handlers, registry, and official alignment map. |
| `skills/eeglab-analysis/` | Research workflow Skill and agent references. |
| `docs/` | Official coverage, support, risk, workflow, and report matrices. |
| `configs/` | MCP client templates. |
| `scripts/` | User dispatcher plus setup, doctor, uninstall, and verification helpers. |

## Development And Verification

Run the release-level verifier:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
```

Run live official URL checks:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online
```

Optional style/type checks, when development dependencies are installed:

```powershell
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

The verifier checks tool counts, prompts/resources, handler registry, eval contracts, Skill references, official claim/profile/tool/resource synchronization, method gate behavior, support/plugin/report matrices, and optional live official EEGLAB/SCCN/BIDS URLs.

## Uninstall

Preview first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -DryRun -RemoveSkill
```

Then uninstall if the preview looks right:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -RemoveSkill
```

The uninstall path backs up the Codex config and Skill directory before removing the `eeglab` registration or Skill.

## Further Reading

- GitHub README guidance: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- EEGLAB documentation: https://eeglab.org/
- EEGLAB repository: https://github.com/sccn/eeglab
- Official topic and support matrices: see `docs/` or the `eeglab://official/...` MCP resources.
