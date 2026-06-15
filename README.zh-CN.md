# EEGLAB MCP Agent

[English](README.md)

EEGLAB MCP Agent 是一个本地优先的 MCP server + MATLAB EEGLAB 研究工作流 Skill。它让 AI 助手通过结构化 `eeglab_*` 工具调用 EEGLAB，同时用 Skill 和 MCP guidance surfaces 约束 EEG 工作中的研究规划、QC gate、事件语义、provenance、method preflight 和可复现实验报告。

本项目不限于 Codex。任何支持 MCP stdio 的客户端都可以使用这个 server，包括 Codex、Claude Desktop、VS Code MCP 集成、Cursor，以及其他支持 MCP 的 IDE 或 agent 环境。支持 Skill 的客户端可以直接安装 Skill；只支持 MCP 的客户端也可以通过 MCP prompts 和 resources 使用同一套方法制度。

本项目面向 EEG 信号处理研究流程，不是临床诊断系统，也不能用于临床结论。

## 目录

- [这是什么](#这是什么)
- [谁可以使用](#谁可以使用)
- [快速开始](#快速开始)
- [MCP 使用方式](#mcp-使用方式)
- [Skill 使用方式](#skill-使用方式)
- [研究安全 Gates](#研究安全-gates)
- [报告与复现](#报告与复现)
- [验证](#验证)
- [卸载](#卸载)

## 这是什么

### 简单版

安装本地 `eeglab` MCP server，把它接入你的 AI 客户端，然后让 assistant 在 EEG 研究约束下调用 EEGLAB 工具。

### 详细版

本项目有三层产品表面：

- MCP tools 通过结构化 `eeglab_*` 调用执行本地 EEGLAB/MATLAB 工作。
- Skill 教 assistant 如何选择工作流、在不安全 gate 停止、保留 provenance 并报告限制。
- MCP prompts 和 resources 把同一套工作流模板与参考文档暴露给不能直接加载 Skill 的客户端。

当前发布事实：

- 项目/服务器版本：`1.0`。
- MCP 工具表面：37 个 legacy low-level tools 加 8 个 research workflow tools，共 45 个 exposed tools。
- MCP guidance surface：10 个 prompts 和 25 个只读 resources。
- Eval contract：56 条可机器校验的 workflow evals。
- 官方对齐 map：47 条 official claims 和 39 个 method profiles。
- 运行模式：本地优先 stdio MCP；EEG 数据留在用户机器上。

## 谁可以使用

### 简单版

任何可以启动本地 stdio MCP server 的客户端都能使用。Codex 支持，但它只是可用客户端之一。

### 详细版

支持三种客户端模式：

- MCP-only 客户端：把本地 server 配置为 `eeglab`，然后使用 MCP tools、prompts 和 resources。
- Skill-aware 客户端：在 MCP server 之外安装 `eeglab-analysis` Skill。
- Custom-instruction 客户端：加入项目指令，要求 EEG/EEGLAB 工作必须通过本地 `eeglab` MCP server，并且高风险分析前必须运行 planning/preflight。

客户端示例：

- Codex：使用 setup 脚本或 Codex 配置模板。
- Claude Desktop：合并 Claude Desktop MCP 模板并重启应用。
- VS Code 和 Cursor：使用对应 MCP 模板并 reload MCP 客户端。
- 其他 MCP 客户端：使用通用模板，指向本地 Python server 入口。

## 快速开始

### 简单版

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

重启客户端，然后提出 EEG 或 EEGLAB 任务。

### 详细版

setup 脚本适合 Codex 风格的本地安装。它会备份用户配置，把 MCP server 注册为 `eeglab`，并把 Skill 同步到本地 Skill 目录。它不会删除或覆盖单独存在的通用 `matlab` MCP 注册。

对于 Claude Desktop、VS Code、Cursor 或其他 MCP 客户端，请复制客户端配置模板，并调整这些值：

- `EEGLAB_PATH`：本地 EEGLAB 安装目录。
- `MATLAB_EXEC`：`matlab` 或 `matlab.exe` 的绝对路径。
- `MATLAB_ROOT`：如果客户端或模板需要，填写本地 MATLAB 根目录。
- `EEGLAB_WORK_DIR`：EEGLAB MCP 专用工作目录。
- `MATLAB_TIMEOUT`：可选，每次调用的超时时间。

所有 MCP 客户端都需要类似的 server 结构：

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

server 名称保持为 `eeglab`。Skill、prompts、resources 和 workflow examples 都按这个名称描述工具路由。

## MCP 使用方式

### 简单版

第一次检查数据集时，先使用只读调用顺序：

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

不要一开始就运行 ICA、源定位、一键 pipeline 或会修改数据的预处理。

### 详细版

真实分析使用这个工作流：

1. Plan：调用 `eeglab_project_plan` 或 `eeglab_workflow_recommend`。
2. Audit：检查 recording metadata、通道位置、事件、history 和 provenance。
3. Preflight：高风险方法前调用 `eeglab_method_preflight`。
4. Execute：只有 gate 通过，或记录明确 override reason 后，才调用 low-level `eeglab_*` tools。
5. Report：调用 `eeglab_protocol_export`，传入 gate results、source claim IDs、report fields、overrides、参数、输出文件和 limitations。

主要 research workflow tools：

- `eeglab_qc_report`：只读 recording、event、ICA、通道位置和 provenance 总结。
- `eeglab_workflow_recommend`：根据项目事实生成自适应工作流建议。
- `eeglab_erp_light_workflow`：把 smoke-tested ERP 链写入 derivative 输出路径。
- `eeglab_project_plan`：包含 blockers、gates、quick modes 和官方引用的研究计划。
- `eeglab_method_preflight`：高风险处理前执行官方方法 gate。
- `eeglab_event_semantics_audit`：epoch 或事件锁定分析前分类 markers。
- `eeglab_plugin_check`：检查本地插件可用性和支持级别。
- `eeglab_protocol_export`：导出包含 gates、claims、overrides、report fields 和 limitations 的 Markdown/JSON protocol。

如果同时使用通用 MATLAB MCP，请保持 server 名称分开：

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

两个 server 应视为彼此隔离的 MATLAB 会话。跨 server 协作使用显式文件交接，例如 `.set/.fdt`、`.mat`、`.csv`、`.png`、Markdown 或 JSON 报告。

## Skill 使用方式

### 简单版

如果客户端支持 Skill 或项目 instruction pack，请安装 `eeglab-analysis` Skill。Skill 会让 assistant 在 EEG 研究 gate 下使用 MCP tools，而不是直接跳到不安全操作。

### 详细版

Skill package 包含：

- `SKILL.md`：入口指令，说明何时使用 EEGLAB MCP server，以及如何路由 EEG 工作。
- QC、ERP、spectral、ERSP/ITC、ICA cleanup、BIDS/STUDY、source、插件依赖 guidance 和 report-only recovery 的工作流 recipes。
- 工具调用顺序、常用参数和错误恢复规则。
- 高风险 EEG 处理的 method gate policy。
- 采集元数据、事件语义、预处理、ICA/ICLabel、BIDS/STUDY、源定位、统计/报告和 protocol export 参考。

对于 Skill-aware 客户端：

1. 安装或导入整个 `eeglab-analysis` Skill 目录。
2. 保持 `SKILL.md` 和参考文档在一起。
3. 在 EEG/EEGLAB 任务中触发它，例如 recording inspection、preprocessing、ICA/ICLabel、ERP、ERSP/ITC、spectral analysis、connectivity、BIDS/STUDY、source localization、plugin checks 或 protocol export。

对于 MCP-only 客户端：

- 读取 `eeglab://skill/SKILL.md` 获取 Skill 入口 policy。
- 读取 `eeglab://references/workflows.md` 获取 workflow recipes。
- 读取 `eeglab://references/tools.md` 获取工具分组和预期调用顺序。
- 高风险处理前读取 `eeglab://references/method-gates.md` 和 `eeglab://official/gate-policy.md`。
- 如果客户端支持 MCP prompts，可使用 `eeglab_project_intake`、`eeglab_strict_qc_protocol` 和 `eeglab_report_template`。

实际触发示例：

- “检查这个 `.set` recording，告诉我是否适合做 ERP。”
- “规划 resting-state spectral workflow，但不要修改 raw data。”
- “检查这个数据集是否可以安全运行 ICA/ICLabel。”
- “在 epoching 前审计 event labels。”
- “导出包含 blocked gates 和 limitations 的 methods/protocol report。”

Skill 不是执行器。它不运行 MATLAB。它是告诉 assistant 何时、如何调用 MCP tools 的 policy layer。

## 研究安全 Gates

### 简单版

高风险 EEG 步骤前先运行 method preflight。如果 gate 被阻断，停止并报告缺失内容。

### 详细版

以下高风险处理必须先明确前置条件：

- 滤波、降采样、重参考和 line-noise cleanup。
- ASR/clean_rawdata。
- ICA、ICLabel、component flagging 和 component removal。
- Epoching、ERP、ERSP/ITC 和 time-frequency analysis。
- Resting-state spectral/connectivity claims。
- Source localization 和 DIPFIT。
- BIDS/STUDY/group analysis。
- LIMO、SIFT、AMICA、RELICA、ROIconnect、EEGstats、NSG 和其他插件依赖工作流。

事件语义是 hard gate。Boundary、impedance、segment start/end 和 excluded markers 不能被当作 condition triggers，除非用户提供经过验证的 codebook 或 event sidecar。

如果用户明确 override 被阻断的 gate，assistant 必须在最终报告中记录 `override_used`、`override_reason`、blocked requirements、source claim IDs 和 limitations。

## 报告与复现

### 简单版

使用 `eeglab_protocol_export` 导出最终 Markdown 或 JSON protocol。

### 详细版

报告应保留：

- 输入和输出路径。
- 采样率、时长、通道数、参考、montage、通道位置覆盖率、事件标签、事件数量和 history 可用性。
- 处理参数：filter cutoffs、line-noise 设置、ASR threshold、重参考、ICA 算法、ICLabel thresholds、epoch/baseline windows、frequency windows、剔除的 channels/epochs/components 和输出文件。
- `gate_results`、`method_profile_id`、`gate_status`、missing requirements 和 critical missing requirements。
- 来自官方对齐检查的 `source_claim_ids`。
- `override_used`、`override_reason` 和已确认的 blocked requirements。
- Report-field matrix coverage 和 limitations。

Protocol exporter 不允许覆盖 `.set`、`.fdt`、`.eeg`、`.vhdr`、`.vmrk`、`.edf`、`.bdf` 或 `.cnt` 等 EEG 数据文件。

## 验证

### 简单版

运行两个项目 verifier：

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
```

### 详细版

运行发布级检查：

```powershell
python -B -m py_compile .\eeglab_mcp_server\workflows.py .\eeglab_mcp_server\schemas.py .\scripts\verify_framework.py .\scripts\verify_official_alignment.py
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

可选官方链接在线验证：

```powershell
python .\scripts\verify_official_alignment.py --online
```

## 卸载

### 简单版

先用 `-DryRun` 运行卸载脚本，确认计划无误后再真正卸载。

### 详细版

先 dry-run：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

确认后再卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

卸载脚本会先备份 Codex 配置和 Skill 目录，再移除 `eeglab` 注册或 Skill。
