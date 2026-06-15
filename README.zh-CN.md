# EEGLAB MCP Agent

[English](README.en.md) | [仓库入口](README.md)

EEGLAB MCP Agent 是一个本地优先的 MCP server + EEG 研究工作流 Skill，用于让 AI 助手以结构化 `eeglab_*` 工具调用 MATLAB EEGLAB，同时通过研究方法制度约束规划、QC gate、事件语义、官方方法 preflight、provenance 和可复现实验报告。

它不是只给 Codex 用的。任何支持 MCP stdio 的客户端都可以接入这个 MCP server，包括 Codex、Claude Desktop、VS Code MCP 集成、Cursor，以及其他支持 MCP 的 IDE 或 agent 环境。支持 Skill 的客户端可以直接安装 Skill；不支持 Skill 的客户端，也可以通过 MCP prompts/resources 读取同一套工作流约束和参考文档。

本项目面向 EEG 信号处理研究流程，不是临床诊断系统，也不能用于临床结论。

## 当前发布事实

- 项目/服务器版本：`1.0`。
- MCP 工具表面：37 个 legacy low-level `eeglab_*` 工具，加 8 个 research workflow 工具，共 45 个暴露工具。
- MCP 指导表面：10 个 prompts 和 25 个只读 resources。
- Eval contract：55 条可机器校验的 workflow eval。
- 官方对齐 map：47 条 official claims 和 39 个 method profiles。
- 运行模式：本地优先 stdio MCP；EEG 数据留在用户机器上。

以上数量由 framework verifier 和 official-alignment verifier 检查。

## 这个仓库提供什么

### MCP Server

MCP server 是执行层。它在本地运行，通过 MATLAB Engine 或 `matlab -batch` 启动 MATLAB/EEGLAB，并向 MCP 客户端暴露 `eeglab_*` 工具。

MCP server 用于：

- 加载 EEGLAB 数据集和支持的 EEG 导入格式。
- 检查采样率、数据形状、事件、history、通道位置和 provenance。
- 运行带 gate 的预处理和分析步骤，例如滤波、降采样、重参考、ICA、ICLabel、ERP、时频、地形图、源定位、STUDY 和 pipeline 工具。
- 运行研究工作流工具，例如项目规划、method preflight、插件检查、事件语义审计和 protocol export。

### Skill

Skill 是方法层。它教 AI 助手如何以安全、可复现、符合 EEG 研究规范的方式使用 MCP server。

Skill 用于：

- 在调用工具前选择正确工作流。
- 追问缺失的研究目标、事件码表、采集元数据、montage 信息和输出要求。
- 在事件语义、通道位置、插件前置条件或官方方法 gate 缺失时阻断不安全分析。
- 报告参数、生成文件、gate 结果、source claim IDs、限制和 override 决策。

Skill 是普通的 `SKILL.md` 加 references 文档。支持 Skill 的客户端可以安装或导入它。不支持 Skill 的客户端仍可通过 MCP prompts/resources 读取等价指导内容。

### Prompts 与 Resources

MCP server 清晰区分三类能力：

- Tools 执行动作。
- Prompts 提供工作流模板。
- Resources 暴露只读 Skill/reference/official-alignment 文档。

Prompts 和 resources 不运行 MATLAB，也不会修改 EEG 数据。

## 仓库结构

- `eeglab_mcp_server/`：Python stdio MCP server 包。
- `skills/eeglab-analysis/`：Skill 指令和参考文档。
- `configs/`：Codex、Claude Desktop、Cursor、VS Code 和通用 MCP 客户端配置模板。
- `docs/`：研究标准、官方支持矩阵、gate policy、插件 map、风险 map 和报告字段矩阵。
- `scripts/`：安装、doctor、卸载、framework verifier 和 official-alignment verifier。

## 环境要求

- Python 3.10 或更新版本。
- 本地 MATLAB。
- 本地 EEGLAB。
- 按工作流需要安装可选 EEGLAB 插件，例如 clean_rawdata、ICLabel、DIPFIT、EEG-BIDS、BIOSIG、File-IO、HEDTools、LIMO、SIFT、AMICA、RELICA、Viewprops、get_chanlocs、ROIconnect、EEGstats 和 NSGportal。

这个 server 不依赖通用 MATLAB MCP。它也可以和通用 MATLAB MCP 并行运行，只要两个 server 使用不同名称。

## 快速开始

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\setup_eeglab_agent.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\doctor_eeglab_agent.ps1
```

这个 setup 脚本主要用于 Codex 风格的本地安装：它会备份用户配置，把 MCP server 注册为 `eeglab`，并把 Skill 同步到本地 Skill 目录。它不会删除或覆盖已有的通用 `matlab` MCP 注册。

对于 Claude Desktop、VS Code、Cursor 或其他 MCP 客户端，请使用 `configs/` 中的模板，并修改本地路径。

客户端说明：

- Codex：使用 setup 脚本自动注册 MCP 并同步 Skill，或手动复制模板。
- Claude Desktop：把 Claude 模板合并到本地 Claude Desktop MCP 配置，然后重启 Claude Desktop。
- VS Code 和 Cursor：使用对应 MCP 模板，保持 server 名称为 `eeglab`，然后重启或 reload MCP 客户端。
- 其他 MCP 客户端：使用通用模板，并指向本地 Python server 入口。

## 手动 MCP 配置

所有 MCP 客户端都需要同样的 server 结构：

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

server 名称建议保持为 `eeglab`。Skill、prompts 和 docs 中的工具路由说明都默认使用这个名称。

已有模板：

- Codex：`configs/codex.config.toml`
- Claude Desktop：`configs/claude_desktop_config.json`
- Cursor：`configs/cursor.mcp.json`
- VS Code：`configs/vscode.mcp.json`
- 通用/OpenClaw 风格客户端：`configs/openclaw.mcp.json`

需要调整：

- `EEGLAB_PATH`：本地 EEGLAB 安装目录。
- `MATLAB_EXEC`：`matlab` 或 `matlab.exe` 的绝对路径。
- `MATLAB_ROOT`：本地 MATLAB 根目录，如果你的客户端模板需要。
- `EEGLAB_WORK_DIR`：EEGLAB MCP 专用工作目录。
- `MATLAB_TIMEOUT`：可选，每次调用的超时时间。

## Skill 安装与使用

Skill 位于 `skills/eeglab-analysis/`。

Skill 包含：

- `SKILL.md`：入口指令，告诉 AI 助手何时使用 EEGLAB MCP server，以及如何路由 EEG 工作。
- `references/workflows.md`：QC、ERP、spectral、ERSP/ITC、ICA cleanup、BIDS/STUDY、source、插件依赖 guidance 和 report-only recovery 的具体流程。
- `references/tools.md`：工具分组、推荐调用顺序、常用参数和错误恢复规则。
- `references/method-gates.md` 与 `references/gate-policy.md`：高风险 EEG 处理的 method preflight 规则。
- 采集元数据、事件语义、预处理、ICA/ICLabel、BIDS/STUDY、源定位、统计/报告和 protocol export 的 policy references。

对于支持 Skill 的客户端：

1. 安装或导入整个 `skills/eeglab-analysis/` 目录。
2. 保持 `SKILL.md` 和 `references/` 目录在一起。
3. 在 EEG/EEGLAB 任务中触发它，例如 recording inspection、preprocessing、ICA/ICLabel、ERP、ERSP/ITC、spectral analysis、connectivity、BIDS/STUDY、source localization、plugin check 或 protocol export。

对于 Codex，setup 脚本可以自动同步 Skill。手动安装时可以把该目录复制到用户的 Codex Skill 目录。

对于 Claude Desktop、VS Code、Cursor 或其他 agent 环境：

- 如果客户端有 Skill、plugin 或 instructions 功能，把 `eeglab-analysis` Skill 目录导入那里。
- 如果客户端只支持 MCP，就使用 server 暴露的 MCP prompts 和 resources；它们包含同样的核心工作流 policy 和参考材料。
- 如果客户端支持自定义 system/project instructions，请加入这条核心规则：EEG/EEGLAB 工作使用本地 `eeglab` MCP server；高风险处理前先调用 planning/preflight 工具；保存原始数据；报告 gate 结果和限制。

Skill 不是执行器。它不运行 MATLAB。它是告诉 AI 助手何时、如何调用 MCP tools 的方法制度。

实际触发示例：

- “检查这个 `.set` recording，告诉我是否已经适合做 ERP。”
- “规划 resting-state spectral 工作流，但不要修改原始数据。”
- “检查这个数据集是否可以安全运行 ICA/ICLabel。”
- “在 epoching 前审计事件标签。”
- “导出包含 blocked gates 和 limitations 的 methods/protocol report。”

Skill 激活后，assistant 不应直接跳到 EEGLAB 操作。它应该先确认研究目标、数据状态、事件语义、通道位置覆盖、插件前置条件、derivative 输出路径和报告要求。

MCP-only fallback：

- 读取 `eeglab://skill/SKILL.md` 获取 Skill 入口 policy。
- 读取 `eeglab://references/workflows.md` 获取工作流 recipes。
- 读取 `eeglab://references/tools.md` 获取工具分组和调用顺序。
- 高风险处理前读取 `eeglab://references/method-gates.md` 和 `eeglab://official/gate-policy.md`。
- 如果客户端支持 MCP prompts，可使用 `eeglab_project_intake`、`eeglab_strict_qc_protocol` 和 `eeglab_report_template`。

## 如何使用 MCP 工具

第一次检查数据集时，应先做只读检查：

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

不要一开始就跑 ICA、源定位、一键 pipeline 或会修改数据的预处理。先确认数据能加载，并且采样率、通道、事件、history 和 provenance 可解释。

真实分析建议采用这个模式：

1. Plan：调用 `eeglab_project_plan` 或 `eeglab_workflow_recommend`。
2. Audit：检查 recording metadata、通道位置、事件和 history。
3. Preflight：高风险方法前调用 `eeglab_method_preflight`。
4. Execute：只有 gate 通过，或记录明确 override reason 后，才调用 low-level `eeglab_*` 工具。
5. Report：调用 `eeglab_protocol_export`，传入 gate results、source claim IDs、report fields、override、参数、输出文件和限制。

## 研究工作流工具

8 个 research workflow tools 是 agent 使用时最重要的产品层：

- `eeglab_qc_report`：只读总结 recording、event、ICA、通道位置和 provenance。
- `eeglab_workflow_recommend`：根据项目事实推荐自适应工作流。
- `eeglab_erp_light_workflow`：把 smoke-tested ERP 链写入新的 derivative 输出路径。
- `eeglab_project_plan`：生成包含 blockers、gates、quick modes 和官方引用的研究计划。
- `eeglab_method_preflight`：高风险处理前执行官方方法 gate。
- `eeglab_event_semantics_audit`：epoch 或事件锁定分析前分类 markers。
- `eeglab_plugin_check`：检查本地插件可用性和支持级别。
- `eeglab_protocol_export`：导出包含 gates、claims、overrides、report fields 和 limitations 的 Markdown/JSON protocol。

## 高风险 Gate Policy

以下高风险处理必须先明确前置条件：

- 滤波、降采样、重参考和 line-noise cleanup。
- ASR/clean_rawdata。
- ICA、ICLabel、component flagging 和 component removal。
- Epoching、ERP、ERSP/ITC 和时频分析。
- Resting-state spectral/connectivity 解释。
- Source localization 和 DIPFIT。
- BIDS/STUDY/group analysis。
- LIMO、SIFT、AMICA、RELICA、ROIconnect、EEGstats、NSG 和其他插件依赖工作流。

如果 gate 被阻断，assistant 应停止，报告 missing requirements 和 `source_claim_ids`，并询问缺失事实。若用户明确 override，必须记录并报告 override reason。

## 与通用 MATLAB MCP 并行

本项目可以和通用 MATLAB MCP 共存。

推荐命名：

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

EEG 加载、QC、事件审计、EEGLAB 预处理、ICA、ERP、时频、源定位、STUDY 和 EEGLAB 图形优先用 `eeglab`。自定义 `.m` 脚本、通用矩阵/统计代码或非 EEGLAB 工具箱再用 `matlab`。

两个 server 应视为彼此隔离的 MATLAB 会话。不要假设变量共享。跨 server 协作使用显式文件交接，例如 `.set/.fdt`、`.mat`、`.csv`、`.png`、Markdown 或 JSON 报告。

## 报告 Contract

`eeglab_protocol_export` 是研究报告出口。报告应保留：

- 输入和输出路径。
- 采样率、时长、通道数、参考、montage、通道位置覆盖率、事件标签、事件数量和 history 可用性。
- 处理参数：滤波 cutoff、line-noise 设置、ASR threshold、重参考、ICA 算法、ICLabel threshold、epoch/baseline 窗口、频率窗口、剔除的通道/epochs/components 和输出文件。
- `gate_results`、`method_profile_id`、`gate_status`、missing requirements 和 critical missing requirements。
- 来自官方对齐检查的 `source_claim_ids`。
- `override_used`、`override_reason` 和已确认的 blocked requirements。
- Report-field matrix coverage 和 limitations。

Protocol exporter 不允许覆盖 `.set`、`.fdt`、`.eeg`、`.vhdr`、`.vmrk`、`.edf`、`.bdf` 或 `.cnt` 等 EEG 数据文件。

## 验证

不需要 EEG 测试数据即可运行 framework 检查：

```powershell
python -B .\scripts\verify_framework.py
python -B .\scripts\verify_official_alignment.py
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

可选官方链接在线验证：

```powershell
python .\scripts\verify_official_alignment.py --online
```

## 卸载

先 dry-run：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -DryRun -RemoveSkill
```

确认后再卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_eeglab_agent.ps1 -RemoveSkill
```

卸载脚本会先备份 Codex 配置和 Skill 目录，再移除 `eeglab` 注册或 Skill。
