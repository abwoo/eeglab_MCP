# EEGLAB MCP Agent

Language: [English](#english) | [中文](#中文)

<a id="english"></a>
## English

EEGLAB MCP Agent is a local-first MCP + Skill product for EEG research workflows. It exposes EEGLAB's MATLAB capabilities as model-callable `eeglab_*` tools, then pairs those tools with a strict research workflow skill for planning, QC gates, event semantics, official-method preflight, provenance, parameter records, and reproducible protocol export.

This project is for EEG signal-processing research workflows. It is not a clinical diagnosis tool and must not be used to make clinical claims.

## Current Release Facts

- Project/server version: `1.0`.
- Tool surface: 37 legacy low-level tools plus 8 research workflow tools, for 45 exposed MCP tools.
- MCP guidance surface: 10 prompts and 25 read-only resources.
- Evaluation contract: 55 machine-checkable workflow evals in `evals.xml`.
- Official alignment map: 47 official claims and 39 method profiles.
- Local-first operation: EEG data stays on the user's machine; cross-tool handoff uses explicit files.

The counts above are enforced by `scripts/verify_framework.py` and `scripts/verify_official_alignment.py`.

## Product Layers

- `eeglab_mcp_server/`: Python stdio MCP server for EEGLAB tools, workflow gates, plugin checks, and protocol export.
- `skills/eeglab-analysis/`: research-method skill for Codex or other skill-aware agents.
- MCP prompts/resources: workflow prompts plus read-only Skill, reference, and official-alignment documents for clients that do not load skills directly.
- `docs/`: research standard, user workflow, official support, risk, plugin, method, gate, and report-field maps.
- `configs/`: manual MCP client templates.
- `scripts/`: setup, doctor, uninstall, framework verification, and official-alignment verification helpers.

The intended workflow is stable: plan first, inspect data and events, run method preflight before high-risk processing, execute only after gates pass or an explicit override is recorded, then export exact parameters, gate results, source claim IDs, limitations, and report fields.

## Quick Start

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

The setup script backs up the Codex config before writing, registers the EEGLAB MCP as `eeglab`, and syncs the Skill into the Codex skill directory. It does not modify an existing generic `matlab` MCP registration.

After setup, restart the IDE/client and ask for an EEG or EEGLAB task.

## Manual Configuration

Advanced users can copy templates from `configs/`:

- `codex.config.toml`
- `claude_desktop_config.json`
- `cursor.mcp.json`
- `vscode.mcp.json`
- `openclaw.mcp.json`

Keep the server name as `eeglab`. Adjust local paths before use:

- `EEGLAB_PATH`: local EEGLAB installation.
- `MATLAB_ROOT`: local MATLAB root, when needed by the client template.
- `MATLAB_EXEC`: MATLAB executable or command name.
- `EEGLAB_WORK_DIR`: dedicated EEGLAB MCP work directory.

## Pairing With MATLAB MCP

This MCP can run alone or beside a general MATLAB MCP. Keep the names separate:

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

Use `eeglab` first for loading, QC, event audit, preprocessing gates, ICA, ERP, ERSP/ITC, spectral/connectivity planning, STUDY, source localization, and EEGLAB figures. Use `matlab` for custom MATLAB scripts, non-EEGLAB toolboxes, or follow-up calculations outside this MCP surface.

Treat the servers as workspace-isolated sessions. Do not assume `EEG`, `ALLEEG`, or other MATLAB variables are shared. Use explicit file handoff such as `.set/.fdt`, `.mat`, `.csv`, `.png`, Markdown, or JSON reports.

## Research Workflow

Recommended entry points:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`
7. `eeglab_project_plan`, `eeglab_workflow_recommend`, or `eeglab_method_preflight`

High-risk processing must be gated before execution: filtering, resampling, rereferencing, ASR/clean_rawdata, ICA, ICLabel, component removal, epoching, time-frequency analysis, source localization, STUDY/group workflows, connectivity, and one-click pipelines. If a gate is blocked, the agent must stop unless the user supplies an explicit override reason, and the final report must preserve the override status and limitations.

Useful research shortcuts:

- `quick_qc`: load, QC, events, and history only; never modifies data.
- `safe_erp`: ERP only after event semantics are confirmed as condition triggers.
- `segment_qc`: for start/end marker datasets without task-condition triggers.
- `study_ready_check`: BIDS/STUDY prerequisites before group statistics.
- `plugin_doctor`: plugin availability and support-level checks for clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, MFF, NWB, BVA, HEDTools, firfilt, CleanLine, Zapline-Plus, AMICA, Picard, RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, LIMO, SIFT, groupSIFT, NFT, and NSGportal.

## MCP Prompts And Resources

The MCP server exposes tools for execution, prompts for workflow templates, and resources for read-only reference material. Prompts and resources are guidance surfaces only; they do not run MATLAB or modify EEG data.

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

Built-in resources include the Skill, workflow/tool/setup references, method gates, acquisition-to-derivatives guidance, event semantics, preprocessing and ICA policies, BIDS/STUDY policy, source policy, report templates, statistics/reporting guidance, official support matrices, plugin matrices, risk matrices, and report-field matrices.

## Reporting Contract

`eeglab_protocol_export` is the research report exit. Reports should preserve:

- Gate results, method profile IDs, gate status, and missing requirements.
- `source_claim_ids` from official alignment checks.
- Override status, override reason, and acknowledged blockers.
- Report-field matrix coverage.
- Input/output paths, parameters, software/plugin facts, and limitations.
- A safe next step when execution is blocked.

Protocol export supports Markdown and JSON and can write to a safe output path. It must not overwrite EEG data files such as `.set`, `.fdt`, `.eeg`, `.vhdr`, `.vmrk`, `.edf`, `.bdf`, or `.cnt`.

## Verification

Framework verification does not require EEG test data:

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python .\scripts\verify_official_alignment.py --online
```

Release-level local checks:

```powershell
python -B -m py_compile .\eeglab_mcp_server\workflows.py .\eeglab_mcp_server\schemas.py .\scripts\verify_framework.py .\scripts\verify_official_alignment.py
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

For a first real EEG dataset, use a small local file and call only `eeglab_init`, `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, and `eeglab_history`. Avoid ICA, filtering, source localization, and one-click pipelines until load/QC/provenance are verified.

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

<a id="中文"></a>
## 中文

EEGLAB MCP Agent 是一个本地优先的 MCP + Skill 脑电研究工作流产品。它把 EEGLAB 的 MATLAB 能力封装成可由模型调用的 `eeglab_*` 工具，同时用严格的研究工作流 Skill 管住规划、质控 gate、事件语义、官方方法 preflight、溯源、参数记录和可复现实验报告导出。

本项目面向 EEG 信号处理研究流程，不是临床诊断工具，也不能用于作出临床结论。

## 当前发布事实

- 项目/服务器版本：`1.0`。
- 工具表面：37 个 legacy low-level 工具加 8 个 research workflow 工具，共 45 个暴露的 MCP tools。
- MCP 指导表面：10 个 prompts 和 25 个只读 resources。
- 评估 contract：`evals.xml` 中有 55 条可机器校验的 workflow eval。
- 官方对齐 map：47 条 official claims 和 39 个 method profiles。
- 本地优先：EEG 数据留在用户机器上；跨工具协作只通过显式文件交接。

这些数量由 `scripts/verify_framework.py` 和 `scripts/verify_official_alignment.py` 共同核验。

## 产品层次

- `eeglab_mcp_server/`：Python stdio MCP server，提供 EEGLAB 工具、workflow gates、插件检查和 protocol export。
- `skills/eeglab-analysis/`：供 Codex 或其他支持 Skill 的 agent 使用的研究方法 Skill。
- MCP prompts/resources：为不直接加载 Skill 的客户端提供 workflow prompts、Skill 文档、参考文档和 official-alignment 文档。
- `docs/`：研究标准、用户流程、官方支持矩阵、风险矩阵、插件矩阵、方法矩阵、gate policy 和报告字段矩阵。
- `configs/`：手动 MCP 客户端配置模板。
- `scripts/`：安装、doctor、卸载、框架验证和官方对齐验证脚本。

推荐流程是固定的：先规划，再检查数据和事件；高风险处理前先运行 method preflight；只有 gate 通过或记录明确 override reason 后才执行；最后导出精确参数、gate 结果、source claim IDs、限制和报告字段。

## 快速开始

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

安装脚本会先备份 Codex 配置，再把 EEGLAB MCP 注册为 `eeglab`，并把 Skill 同步到 Codex skill 目录。它不会修改已有的通用 `matlab` MCP 注册。

安装后重启 IDE 或客户端，然后提出 EEG/EEGLAB 任务即可。

## 手动配置

高级用户可以直接复制 `configs/` 里的模板：

- `codex.config.toml`
- `claude_desktop_config.json`
- `cursor.mcp.json`
- `vscode.mcp.json`
- `openclaw.mcp.json`

服务器名称应保持为 `eeglab`。使用前请调整本地路径：

- `EEGLAB_PATH`：本地 EEGLAB 安装目录。
- `MATLAB_ROOT`：本地 MATLAB 根目录，部分客户端模板可能需要。
- `MATLAB_EXEC`：MATLAB 可执行文件路径或命令名。
- `EEGLAB_WORK_DIR`：EEGLAB MCP 专用工作目录。

## 与 MATLAB MCP 配合

本 MCP 可以独立运行，也可以和通用 MATLAB MCP 并行。名称要分开：

```text
eeglab = EEG/EEGLAB 工作流
matlab = 通用 MATLAB 脚本和自定义计算
```

EEG 专项工作优先使用 `eeglab`：加载、QC、事件审计、预处理 gate、ICA、ERP、ERSP/ITC、频谱/连接规划、STUDY、源定位和 EEGLAB 图形。自定义 MATLAB 脚本、非 EEGLAB 工具箱或 MCP 表面以外的后续计算再使用 `matlab`。

两个 server 应视为相互隔离的 MATLAB 会话。不要假设 `EEG`、`ALLEEG` 或其他 MATLAB 变量可以共享。跨 server 工作要使用显式文件交接，例如 `.set/.fdt`、`.mat`、`.csv`、`.png`、Markdown 或 JSON 报告。

## 研究工作流

推荐入口：

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`
7. `eeglab_project_plan`、`eeglab_workflow_recommend` 或 `eeglab_method_preflight`

高风险处理必须先 gate 再执行：滤波、降采样、重参考、ASR/clean_rawdata、ICA、ICLabel、成分删除、epoch、时频分析、源定位、STUDY/group 工作流、连接分析和一键 pipeline。若 gate 阻断，agent 必须停止；除非用户明确给出 override reason，并且最终报告必须保留 override 状态和限制。

常用研究快捷模式：

- `quick_qc`：只加载、QC、事件和 history，不修改数据。
- `safe_erp`：只有事件语义确认是 condition triggers 后才做 ERP。
- `segment_qc`：适用于只有 start/end marker、没有任务条件 trigger 的数据。
- `study_ready_check`：在 group statistics 前检查 BIDS/STUDY 前置条件。
- `plugin_doctor`：检查 clean_rawdata、ICLabel、DIPFIT、EEG-BIDS、BIOSIG、File-IO、MFF、NWB、BVA、HEDTools、firfilt、CleanLine、Zapline-Plus、AMICA、Picard、RELICA、Viewprops、get_chanlocs、ROIconnect、EEGstats、LIMO、SIFT、groupSIFT、NFT 和 NSGportal 的可用性与支持级别。

## MCP Prompts 与 Resources

MCP server 用 tools 执行动作，用 prompts 提供流程模板，用 resources 提供只读参考材料。Prompts 和 resources 只是指导表面，不会运行 MATLAB，也不会修改 EEG 数据。

内置 prompts：

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

内置 resources 覆盖 Skill、workflow/tool/setup references、method gates、acquisition-to-derivatives、event semantics、preprocessing 和 ICA policy、BIDS/STUDY policy、source policy、report templates、statistics/reporting、official support matrices、plugin matrices、risk matrices 和 report-field matrices。

## 报告 Contract

`eeglab_protocol_export` 是研究报告出口。报告应保留：

- Gate results、method profile IDs、gate status 和 missing requirements。
- 来自 official alignment 的 `source_claim_ids`。
- Override 状态、override reason 和已确认的阻断项。
- Report-field matrix coverage。
- 输入/输出路径、参数、软件/插件事实和限制。
- 执行被阻断时的安全下一步。

Protocol export 支持 Markdown 和 JSON，也可以写入安全输出路径。它不能覆盖 `.set`、`.fdt`、`.eeg`、`.vhdr`、`.vmrk`、`.edf`、`.bdf` 或 `.cnt` 等 EEG 数据文件。

## 验证

框架验证不需要 EEG 测试数据：

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python .\scripts\verify_official_alignment.py --online
```

发布级本地检查：

```powershell
python -B -m py_compile .\eeglab_mcp_server\workflows.py .\eeglab_mcp_server\schemas.py .\scripts\verify_framework.py .\scripts\verify_official_alignment.py
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

第一次用真实 EEG 数据时，请先选一个小的本地文件，只调用 `eeglab_init`、`eeglab_load_data`、`eeglab_qc_report`、`eeglab_info`、`eeglab_get_events` 和 `eeglab_history`。在加载、QC 和 provenance 核验前，不要直接运行 ICA、滤波、源定位或一键 pipeline。

## 卸载

先 dry-run：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

确认后再卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

卸载脚本会在移除 `eeglab` 注册或 Skill 前备份 Codex 配置和 Skill 目录。
