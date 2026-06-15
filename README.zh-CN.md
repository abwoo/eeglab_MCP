# EEGLAB MCP Agent

[English](README.md)

EEGLAB MCP Agent 是一个本地优先的 MCP server + MATLAB EEGLAB 研究工作流 Skill。它让支持 MCP 的 AI 助手通过结构化 `eeglab_*` 工具使用 EEGLAB，同时保留 EEG 研究中的 provenance、事件语义、method preflight、EEGLAB/SCCN 官方对齐和可复现报告。

本项目面向 EEG 信号处理研究流程，不是临床诊断系统，也不能用于临床结论。

## 快速开始

在仓库根目录运行统一入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```

重启 MCP 客户端，然后提出 EEG 或 EEGLAB 任务。

前置条件：

- Python 3.10+
- MATLAB 可通过 `matlab` 或绝对 `matlab.exe` 路径调用
- 本地已安装 EEGLAB
- 插件依赖工作流需要对应 EEGLAB 插件，例如 clean_rawdata、ICLabel、DIPFIT、EEG-BIDS、BIOSIG 和导入/导出插件

## 最小 MCP 配置

server 名称保持为 `eeglab`。Skill、prompts、resources 和 workflow docs 都按这个名称路由。

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

`configs/` 中提供 Codex、Claude Desktop、Cursor、VS Code 和通用 MCP 客户端模板。

## 第一次数据检查

新 recording 先走只读检查：

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

不要一开始就运行 ICA、源定位、一键 pipeline 或会修改数据的预处理。先做 planning 和 method preflight。

## 常用命令

| 任务 | 命令 |
| --- | --- |
| 查看帮助 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 help` |
| 预览安装 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup -DryRun` |
| 安装/注册 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 setup` |
| 验证本地 framework 和官方对齐 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify` |
| 同时验证在线官方链接 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online` |
| 检查本地客户端/MATLAB 环境 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor` |
| 预览卸载 | `powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -DryRun -RemoveSkill` |

`eeglab_agent.ps1` 会转发到专用 setup、verify、doctor 和 uninstall 脚本。自动化可以直接调用底层脚本，但新用户优先使用统一入口。

## 项目提供什么

- 45 个 exposed MCP tools：37 个低层 EEGLAB tool wrappers，加 8 个研究工作流工具。
- 10 个 MCP prompts 和 25 个只读 MCP resources。
- 47 条 official alignment claims 和 39 个 method profiles，对齐 EEGLAB/SCCN 与相关标准。
- 56 条可机器校验的 workflow evals，覆盖 gates、报告、插件缺失和失败恢复。
- 本地优先运行模式：EEG 数据留在用户机器上。

## 客户端与 Skill 使用

任何 stdio MCP 客户端都可以使用本 server。Codex、Claude Desktop、VS Code MCP 集成、Cursor，以及其他支持 MCP 的 IDE 都可以把它注册为 `eeglab`。

支持 Skill 的客户端建议安装 `eeglab-analysis` Skill。只支持 MCP 的客户端可以读取同一套 policy resources：

- `eeglab://skill/SKILL.md`
- `eeglab://references/workflows.md`
- `eeglab://references/tools.md`
- `eeglab://references/method-gates.md`
- `eeglab://official/gate-policy.md`

如果同时使用通用 MATLAB MCP，请保持名称分开：

```text
eeglab = EEG/EEGLAB workflows
matlab = generic MATLAB scripts and custom calculations
```

两个 server 应视为彼此隔离的 MATLAB 会话。跨 server 协作使用显式文件交接，例如 `.set/.fdt`、`.mat`、`.csv`、`.png`、Markdown 或 JSON 报告。

## 研究工作流

高风险分析前先使用研究工作流工具：

1. 用 `eeglab_project_plan` 或 `eeglab_workflow_recommend` 规划。
2. 审计 metadata、channel locations、events、history 和 provenance。
3. 用 `eeglab_method_preflight` 对高风险方法做 preflight。
4. 只有 gate 通过，或明确记录 override reason 后，才执行低层 `eeglab_*` tools。
5. 用 `eeglab_protocol_export` 导出 methods/protocol 文本。

核心 workflow tools：

- `eeglab_qc_report`：只读 recording、event、ICA、通道位置和 provenance 总结。
- `eeglab_workflow_recommend`：根据项目事实生成自适应工作流建议。
- `eeglab_project_plan`：包含 blockers、gates、quick modes 和官方引用的研究计划。
- `eeglab_method_preflight`：高风险处理前执行官方方法 gate。
- `eeglab_event_semantics_audit`：epoch 或事件锁定分析前分类 markers。
- `eeglab_plugin_check`：检查本地插件可用性和支持级别。
- `eeglab_protocol_export`：导出包含 gates、claims、overrides、report fields 和 limitations 的 Markdown/JSON protocol。
- `eeglab_erp_light_workflow`：把 smoke-tested ERP 链写入 derivative 输出路径。

## 官方对齐与安全边界

默认策略是保守的：先审计，高风险方法先 gate，保留 raw data，写 derivative，并报告 limitations。

高风险处理包括 filtering、resampling、rereferencing、line-noise cleanup、ASR/clean_rawdata、ICA、ICLabel、component removal、epoching、ERP、ERSP/ITC、spectral/connectivity claims、source localization、BIDS/STUDY、LIMO、SIFT、AMICA、RELICA、ROIconnect、EEGstats、NSG 和其他插件依赖工作流。

事件语义是 hard gate。Boundary、impedance、segment start/end 和 excluded markers 不能被当作 condition triggers，除非用户提供经过验证的 codebook 或 event sidecar。

不支持执行的官方插件或高级方法只作为 `indexed_only` 或 guidance-only 索引说明。只有存在专用 MCP workflow、method gate、report template 和 eval coverage 时，才能声明可执行支持。

## 报告与复现

最终报告应包含：

- 输入和 derivative 输出路径
- 采样率、时长、通道数、参考、montage、通道位置覆盖率、事件标签/数量和 history 可用性
- filter、line-noise、ASR、rereference、ICA、ICLabel、epoch、baseline、frequency、rejection 和输出参数
- `gate_results`、`method_profile_id`、`gate_status`、missing requirements 和 critical missing requirements
- `source_claim_ids`、plugin status、override status、report-field coverage 和 limitations

Protocol exporter 不允许覆盖 `.set`、`.fdt`、`.eeg`、`.vhdr`、`.vmrk`、`.edf`、`.bdf` 或 `.cnt` 等 EEG 数据文件。

## 仓库地图

| 路径 | 用途 |
| --- | --- |
| `eeglab_mcp_server/` | 可执行 MCP server、tool schemas、handlers、registry 和官方对齐 map。 |
| `skills/eeglab-analysis/` | 研究工作流 Skill 和 agent references。 |
| `docs/` | 官方覆盖、支持、风险、工作流和报告矩阵。 |
| `configs/` | MCP 客户端模板。 |
| `scripts/` | 用户 dispatcher，以及 setup、doctor、uninstall 和 verification helpers。 |

## 开发与验证

运行发布级 verifier：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
```

运行在线官方 URL 检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify-online
```

安装开发依赖后，可选运行 style/type checks：

```powershell
python -m ruff check eeglab_mcp_server scripts
python -m black --check eeglab_mcp_server scripts
python -m mypy --config-file eeglab_mcp_server\pyproject.toml eeglab_mcp_server
```

Verifier 会检查工具数量、prompts/resources、handler registry、eval contracts、Skill references、official claim/profile/tool/resource 同步、method gate 行为、support/plugin/report matrices，以及可选在线 EEGLAB/SCCN/BIDS 官方 URL。

## 卸载

先预览：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -DryRun -RemoveSkill
```

确认后再卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 uninstall -RemoveSkill
```

卸载流程会先备份 Codex config 和 Skill directory，再移除 `eeglab` 注册或 Skill。

## 深入阅读

- GitHub README guidance: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- EEGLAB documentation: https://eeglab.org/
- EEGLAB repository: https://github.com/sccn/eeglab
- 官方 topic/support matrices：见 `docs/` 或 `eeglab://official/...` MCP resources。
