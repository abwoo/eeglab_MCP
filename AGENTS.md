# EEGLAB MCP Agent Guidelines

## 概述

本项目提供 48 个 MCP 工具（39 个低层 EEGLAB 工具 + 9 个研究工作流工具）、10 个 MCP prompts、30 个只读 MCP resources、50 条官方对齐声明、39 个方法 profiles、56 条可机器校验的 workflow evals。
同时，仓库还可以作为一个本地 Codex 插件包装体 `eeglab-analysis` 公开，插件入口通过个人 marketplace 指向当前 checkout。
官方主题索引由 `eeglab_mcp_server/official_alignment.py` 生成，并明确区分 `executable`、`gated_guidance`、`indexed_only` 和 `out_of_scope`；未支持的官方主题只做索引和规划，不做执行承诺。

## 工具使用规则

当用户请求任何 EEG/脑电相关工作时：

1. **先加载 skill**：调用 `skill({ name: "eeglab-analysis" })`
2. **按分支调用工具**：工具注册和 verifier 覆盖必须保持 48 个 exposed tools 全量对齐，但单次分析只调用当前分支需要、已门控通过且用户明确接受的工具；不适用的工具要记录原因
3. **遵循 skill 中的工作流**：参考 `references/workflows.md` 和 `references/branch-workflow-matrix.md`

## 文档权威层级

本仓库同时包含 `docs/` 和 `skills/eeglab-analysis/references/`，二者允许有主题重合，但职责不同：

1. **`docs/` 是官方对齐/权威规则层**：官方 gate policy、method map、plugin map、risk/support/tool-support matrix、report field matrix、topic index 和 research standard。
2. **`skills/eeglab-analysis/references/` 是执行手册层**：把 `docs/` 的规则转成 Codex/agent 可执行的 workflow、工具路由、事件语义、预处理决策树、报告模板和恢复步骤。
3. **`skills/eeglab-analysis/docs/` 是 bundled 官方镜像层**：安装后的 Skill 会携带一份镜像的官方文档，包括 `figure-atlas.md`，用于离线/非仓库场景下保持图像规范、报告字段和 branch 规则一致。
4. **`scripts/advanced_figures/` 是默认可浏览的高级图补充层**：它不是新的执行路径，但会在 README、Skill 和 verifier 中保持默认可见，并通过 `eeglab://scripts/advanced_figures/README.md` 资源公开索引。
5. **冲突处理**：如果 `docs/`、`skills/eeglab-analysis/docs/` 与 `references/` 在支持级别、gate 策略、插件映射、风险分类、报告字段或工具覆盖上冲突，必须以 `docs/` 为准，并更新 `references/` 以重新对齐。
6. **同步要求**：修改官方规则、工具数量、方法 profile、报告字段、插件矩阵、figure atlas、默认高级图索引或 workflow 时，必须同时检查并更新 `docs/`、`references/`、`README.md`、`README.zh-CN.md` 和本 `AGENTS.md` 中受影响的内容。

## 任务完成后的文档更新

每次实质性任务完成前，必须执行一次文档同步检查：

1. 如果任务改变了工具数量、工具行为、workflow、安装/验证方式、报告字段、插件/官方 gate、skill bundle 内容或 Codex 配置方式，必须更新 `README.md`、`README.zh-CN.md` 和 `AGENTS.md`。
2. 如果任务只产生运行结果但不改变仓库规范，也必须在最终回复中明确说明 README/AGENTS 无需更新的原因。
3. 完成前运行相关验证（至少 `scripts/eeglab_agent.ps1 verify`；配置/安装变更还要运行 `doctor`），并在最终回复中报告结果。
4. 不允许只修改代码而留下 README/AGENTS 与实际工具数量、脚本、skill bundle 或研究流程不一致。

## 工具路由

- **脑电/EEGLAB 工作** → `eeglab_*` 工具
- **通用 MATLAB 脚本** → `matlab` MCP 工具
- 两个 MCP 服务器的 MATLAB 会话是隔离的，跨服务器协作使用显式文件交接（`.set/.fdt`、`.mat`、`.csv`、`.png`、Markdown 或 JSON 报告）

## 项目级研究系统

大型 EEG 项目应按以下阶段进行：

1. **项目立项**：明确假设、分析类型、数据格式、项目规模、被试/会话布局、条件和预期输出
2. **记录/来源审计**：保留原始文件；检查采样率、数据形状、时长、通道 montage/参考、事件标记、comments/BIDS 元数据和 EEGLAB history
3. **QC 门控**：验证可加载性、通道位置覆盖率、事件完整性、缺失元数据、插件先决条件、数据是连续还是分段
4. **预处理**：透明、适合研究的滤波、工频噪声清理、重参考、坏道处理、ICA/ICLabel（有理由时）、命名中间保存
5. **分析分支**：根据验证的设计选择 ERP、静息态频谱/连接性、时频、源定位或 STUDY/组统计
6. **报告**：输出数据集/图形/表格，包含精确参数、QC 风险、拒绝的数据/成分、软件/插件限制，不做临床声明
7. **演进**：将重复的项目模式、失败和接受的默认值转化为更新的工作流注释/evals

### 规范总顺序

1. 先加载 `eeglab-analysis` Skill
2. 先读 `docs/`，再读 `skills/eeglab-analysis/references/`
3. 先做 `eeglab_project_plan` / `eeglab_workflow_recommend`
4. 再做只读 intake
5. 事件锁定分支前先做 `eeglab_event_semantics_audit`
6. 每个高风险步骤前先做 `eeglab_method_preflight`
7. 严格按 branch matrix 走预处理、分析、图和 derivative 输出
8. 导出 protocol，再生成最终 report
9. 图像家族按 `references/figure-atlas.md` 与 `docs/figure-atlas.md` 对齐，报告里必须记录 required / conditional / guidance-only families、figure atlas entries 和 figure paths

只使用真实加载的 EEG 数据和真实项目元数据，不得虚构 provenance、图、输出或 gate 结果。

## 第一次数据检查（只读）

新 recording 先走只读检查，不修改数据：

1. `eeglab_init`
2. `eeglab_load_data`（使用绝对路径）
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

报告通道数、采样率、数据点/试次、时长、数据形状、通道位置覆盖率、参考/montage、事件类型/数量、事件延迟范围、文件路径、处理历史可用性和 ICA 状态。

快捷名称：`quick_qc`。这是任何新数据集的默认第一个工作流，从不修改 EEG 数据。

## ERP 预处理工作流

快捷名称：`safe_erp`。如果 `eeglab_event_semantics_audit` 报告没有确认的分析事件，不要进入此工作流。

**官方 EEGLAB 预处理顺序**（来自 EEGLAB Wiki 和 Makoto's pipeline）：
1. 高通滤波（1 Hz for ICA）→ 2. ASR/clean_rawdata → 3. 重参考 → 4. ICA → 5. ICLabel → 6. 移除伪迹成分

典型序列：

1. `eeglab_info` 和 `eeglab_get_events` 检查
2. `eeglab_event_semantics_audit` 确认条件触发器
3. `eeglab_method_preflight` 用于 `epoch` 和计划的滤波/ICA/ASR 分支
4. `eeglab_filter`：高通 1 Hz（ICA 前推荐）或 0.5 Hz（最终分析），可选低通 40-100 Hz
5. `eeglab_clean_line_noise`：50 Hz 或 60 Hz（可选，在 ICA 前或后）
6. `eeglab_clean_rawdata`：保守 ASR 清理（在 ICA 前）
7. `eeglab_reref`：通常平均参考（在 ICA 前，ICA 学习特定参考的解混矩阵）
8. 可选 `eeglab_run_ica` → `eeglab_classify_ica` → `eeglab_remove_components`
9. `eeglab_epoch`：使用显式事件类型和基线窗口
10. `eeglab_erp_analysis`
11. 可选 `eeglab_plot_erp`、`eeglab_topoplot`、`eeglab_plot_psd`
12. `eeglab_save_data`
13. `eeglab_protocol_export`

## 静息态频谱分析

1. 检查/加载数据，验证数据形状适合静息态分析
2. `eeglab_method_preflight` 用于 `derivative_processing`、`line_noise` 和 `spectral`
3. `eeglab_filter`：通常高通 0.5 或 1 Hz，低通 45/80/100 Hz
4. `eeglab_clean_line_noise`：记录本地 50/60 Hz 频率
5. 可选保守 `eeglab_clean_rawdata`
6. `eeglab_reref`
7. `eeglab_spectral`：使用显式 `freq_range`

## 时频分析

1. 检查记录元数据和事件
2. 滤波和工频噪声清理
3. 使用任务相关事件类型分段
4. `eeglab_timefreq`：使用显式 `channels`、`freq_range`、`cycles` 和 `baseline`
5. 可选 `eeglab_plot_timefreq`

## ICA 清理

1. 确保数据是连续的或适合 ICA
2. `eeglab_method_preflight` 用于 `run_ica`
3. `eeglab_plugin_check` 检查 ICLabel/Picard 可用性
4. 使用 ICA 适合的高通滤波，通常 1 Hz
5. 仅在有理由时移除或插值明显坏道
6. `eeglab_run_ica`
7. `eeglab_method_preflight` 用于 `iclabel` 或 `remove_components`
8. `eeglab_classify_ica`
9. `eeglab_flag_components` 或 `eeglab_remove_components`
10. 保存处理后的副本，不覆盖原始数据

**ICLabel 阈值**（来自官方文档）：
- Brain: 保留所有（除非明确伪迹）
- Muscle artifact: >80% 概率标记
- Eye artifact: >80% 概率标记
- Heart artifact: >80% 概率标记
- Line noise: >80% 概率标记
- Channel noise: >80% 概率标记
- Other: 保留所有

## 源定位

先决条件：必须存在 ICA，通道位置必须正确，DIPFIT 资源必须可用。

1. `eeglab_info` 检查 ICA 状态
2. `eeglab_method_preflight` 用于 `source`
3. `eeglab_plugin_check` 检查 DIPFIT
4. `eeglab_run_ica`（如需要）
5. `eeglab_source_settings`
6. `eeglab_source_localization`

## STUDY/组分析

快捷名称：`study_ready_check`。

1. `eeglab_project_plan`
2. `eeglab_method_preflight` 用于 `study`
3. `eeglab_method_preflight` 用于 `bids_metadata`
4. `eeglab_plugin_check` 检查 BIDS/LIMO/SIFT（如需要）
5. `eeglab_method_preflight` 用于 `bids_import` 或 `study_create`
6. `eeglab_method_preflight` 用于 `study_design`
7. `eeglab_method_preflight` 用于 `study_statistics`
8. `eeglab_protocol_export`

## 高风险门控字段

高风险工具接受以下可选字段：

- `method_context`：官方 preflight 已知事实，如数据形状、事件角色、插件、ICA 状态、通道位置、输出计划、rank/参考审查或设计变量
- `override_gate`：仅在用户明确接受缺失的官方先决条件后设为 true
- `override_reason`：`override_gate=true` 时必需；必须在来源和协议输出中报告

## 事件语义审计

在 ERP 或 ERSP/ITC 分析前，当标记尚未记录时使用 `eeglab_event_semantics_audit`。

输入（已知时提供）：
- `event_types` 和 `event_counts`（来自 `eeglab_get_events`）
- `event_descriptions`（来自用户/实验室笔记）
- `condition_markers`（已确认的任务条件）
- `boundary_markers`、`segment_markers` 和 `exclude_markers`（非分析标签）

策略：
- 条件标记在检查数量/延迟后可用于分段
- 候选触发器需要用户确认后才能做科学声明
- boundary、impedance、excluded 和 segment 标记不能作为 ERP 触发器
- start/end 标记数据应使用 `segment_qc`，除非提供条件映射或行为日志

## QC 门控

不要声称数据集已准备好分析，直到检查以下门控：

- 原始输入已保留，转换输出指向新路径
- 记录元数据已报告：源路径、数据形状、采样率、时长、通道数、参考/montage、事件标签/数量、history 可用性
- 通道位置覆盖率已检查
- 事件标签和延迟在 ERP/时频分析前已检查
- 处理历史或当前会话步骤已记录
- 分析分支匹配研究设计和数据形状
- 伪迹拒绝和 ICA 决策有显式阈值/理由
- 输出文件和限制已报告

## 报告要求

最终报告应包含：

- 输入和 derivative 输出路径
- 采样率、时长、通道数、参考、montage、通道位置覆盖率、事件标签/数量和 history 可用性
- filter、line-noise、ASR、rereference、ICA、ICLabel、epoch、baseline、frequency、rejection 和输出参数
- `gate_results`、`method_profile_id`、`gate_status`、missing requirements
- `source_claim_ids`、plugin status、override status、report-field coverage 和 limitations
- **生成的所有图片文件路径及简要说明**（如 ERP 波形图、地形图、时频图、PSD 图、ICA 成分图等）

Protocol exporter 不允许覆盖 `.set`、`.fdt`、`.eeg`、`.vhdr`、`.vmrk`、`.edf`、`.bdf` 或 `.cnt` 等 EEG 数据文件。

### 最终报告生成

所有分析完成后，必须生成一份完整的标准研究报告。使用 `scripts/generate_eeg_report.py` 或等效方法。报告必须包含：

1. **标题和元数据**：报告标题、日期、作者、软件版本
2. **摘要**：研究目的、方法、主要发现
3. **记录和采集**：输入路径、采样率、通道数、事件等
4. **预处理参数**：滤波、工频噪声、重参考、ICA、ICLabel 等
5. **分析参数**：ERP、频谱、时频、连接性、源定位
6. **所有生成的图片**：包含标题、描述、路径
7. **结果**：各分析类型的主要发现
8. **讨论**：结果解释和意义
9. **局限性**：官方 gate 状态、插件限制、数据限制
10. **附录**：软件版本、插件状态、生成的文件列表

报告格式要求：
- 遵循 `docs/official-report-field-matrix.md` 的字段要求
- 图片和文字排版整齐
- 分析严谨规范，不做临床声明
- 输出为 Markdown 或 HTML 格式

## 失败恢复

如果工作流步骤失败，读取 `code`、`error`、`next_step` 和 `details.step`。常见恢复：初始化 EEGLAB、先加载数据、分段前检查事件标签、保持基线在 epoch 窗口内、选择不覆盖输入的输出路径、ICA/源/STUDY 工作前验证所需插件。如果 `code=official_gate_blocked`，不要盲目重试；解决 `missing_requirements` 或获得显式用户覆盖。

## 自我演进

每个实质性项目后，回顾发生了什么：
- 重复缺失的元数据：更新 intake 问题和来源报告指导
- 重复工具/插件失败：添加恢复注释
- 重复被用户接受的参数选择：记录为项目特定默认值
- 新分析模式：添加需要至少两次工具调用和基于早期输出决策的 eval

## 语言规则

所有机器生成的内容必须使用英文，包括但不限于：

- 图片标题、坐标轴标签、图例和注释
- MATLAB 脚本中的代码注释
- 变量名和函数名
- 日志消息和状态输出
- 协议导出和 QC 报告中的文本
- 错误消息和 next_step 建议

与用户的对话可以使用用户偏好的语言。只有机器生成的产物（图片、代码、报告、日志）必须使用英文。

## 图片输出规则

EEG 数据是时空数据。每种分析类型生成一个图片文件，但每个图片必须包含足够的空间上下文。

### 核心原则

每个图片必须平衡空间和时间两个维度：
- **空间**：哪些通道/脑区显示了效应
- **时间**：效应何时发生及其动态

### 按分析类型的图片规则

#### 1. 地形图 (`eeglab_topoplot`)
- **输出**：每个时间点或频段一张头皮图。
- **包含**：所有有有效位置的通道。
- **多个时间点**：保存为单独文件（如 `topo_p300_250ms.png`、`topo_p300_300ms.png`）。
- **多个条件**：保存为单独文件以便直接比较。

#### 2. ERP 波形 (`eeglab_plot_erp`)
- **输出**：每个成分/分析一张图，包含多个通道。
- **包含**：至少 2-3 个覆盖成分头皮分布的通道（如 P300 显示 Fz/Cz/Pz，N170 显示 O1/O2）。
- **条件**：条件 A vs B 放在同一张图中直接比较。
- **不同成分**：分开文件（如 `erp_n170.png`、`erp_p300.png`）。

#### 3. 时频图 (`eeglab_plot_timefreq`)
- **输出**：每个通道或通道组一张 ERSP/ITC 图。
- **包含**：显示同一功能区的通道（如额叶 theta 通道、枕叶 alpha 通道）。
- **不同频段**：如果频段分开分析，使用单独文件。

#### 4. 功率谱密度 (`eeglab_spectral`)
- **输出**：每个脑区组一张 PSD 图。
- **包含**：按功能区（额叶、中央、顶叶、枕叶）分组通道，每个区域 3-4 个通道。
- **不同区域**：使用单独文件。

#### 5. ICA 成分 (`eeglab_plot_components`)
- **输出**：每个成分一张图，显示地形图 + 频谱 + 时间过程。
- **包含**：每个成分的三个视图（地形图、频谱、ERP）。

#### 6. 连接性 (`eeglab_connectivity`)
- **输出**：每个频段一张连接矩阵/网络图。
- **包含**：全通道集。

### 汇总

| 分析类型 | 输出文件 | 空间内容 |
|---------|---------|---------|
| 地形图 | 每个时间/频段 1 个文件 | 所有通道 |
| ERP | 每个成分 1 个文件 | 2-3+ 通道 |
| 时频 | 每个通道/组 1 个文件 | 区域通道 |
| PSD | 每个区域 1 个文件 | 3-4 通道 |
| ICA | 每个成分 1 个文件 | 地形图 + 频谱 |
| 连接性 | 每个频段 1 个文件 | 完整网络 |

### 例外情况

- **用户请求**：当用户明确要求不同布局时覆盖规则。
- **发表图片**：遵循期刊对多面板图片的要求。
- **探索性分析**：初始数据检查时，单通道图片可接受。

### 输出路径

所有路径必须是绝对路径，不要依赖 MATLAB 默认的 figure 路径。

## 插件前置检查

使用插件依赖工具前，必须先调用 `eeglab_plugin_check`。已知依赖：

| 工具 | 所需插件 | 缺失时的处理 |
|---|---|---|
| `eeglab_clean_line_noise` | CleanLine (`pop_cleanline`) | 报告缺失，建议用户通过 EEGLAB 菜单 `Tools > Manage EEGLAB extensions > CleanLine` 安装 |
| `eeglab_clean_rawdata` | clean_rawdata (`pop_clean_rawdata`) | 报告缺失，建议用户通过 EEGLAB 菜单安装 clean_rawdata |
| `eeglab_run_ica` (picard) | Picard (`picard`) | 降级为 `algorithm=runica`（内置），记录实际使用的算法 |
| `eeglab_classify_ica` | ICLabel (`pop_iclabel`) | 报告缺失，建议用户安装 ICLabel，需人工检查 ICA 成分 |
| `eeglab_flag_components` | ICLabel (`pop_icflag`) | 报告缺失，建议用户安装 ICLabel |
| `eeglab_source_localization` | DIPFIT (`pop_dipfit_settings`) | 报告缺失，建议用户安装 DIPFIT |
| `eeglab_source_settings` | DIPFIT (`pop_dipfit_settings`) | 报告缺失，建议用户安装 DIPFIT |
| `eeglab_import_bids` | EEG-BIDS (`pop_importbids`) | 报告缺失，建议用户安装 EEG-BIDS |
| `eeglab_study_create` | EEG-BIDS (`pop_importbids`) | 报告缺失，建议用户安装 EEG-BIDS |
| `eeglab_plot_erp` | pop_ploterp（EEGLAB 内置） | 报告函数不可用，建议用户更新 EEGLAB 到最新版本 |

插件缺失时：(1) 明确报告缺失的插件名称和所需函数 (2) 告知用户通过 EEGLAB 菜单 `Tools > Manage EEGLAB extensions` 下载安装 (3) 在协议导出中记录限制

## 脚本工具

`scripts/` 文件夹包含安装和验证脚本，以及报告生成工具：

| 脚本 | 用途 |
|------|------|
| `setup_eeglab_agent.ps1` | 安装 EEGLAB Agent |
| `eeglab_agent.ps1` | 主启动脚本 |
| `doctor_eeglab_agent.ps1` | 健康检查 |
| `verify_eeglab_agent.ps1` | 验证安装 |
| `verify_official_alignment.py` | 验证官方对齐 |
| `verify_framework.py` | 验证框架 |
| `uninstall_eeglab_agent.ps1` | 卸载脚本 |
| `generate_eeg_report.py` | 生成标准研究报告 |
| `report_template.json` | 报告模板 JSON 文件 |

## 强制执行协议

本节为强制性规则，每次 EEG 分析会话必须全部遵守，无例外。

### 工具覆盖要求

每次 EEG 分析会话必须让工具覆盖与分支对齐，并在协议中明确记录实际调用、分支必需、条件性启用和不适用工具。完整工具集合（用于注册、验证和能力映射）：

**数据管理 (7 个):** `eeglab_init`, `eeglab_load_data`, `eeglab_save_data`, `eeglab_import_bids`, `eeglab_info`, `eeglab_history`, `eeglab_qc_report`

**预处理 (8 个):** `eeglab_filter`, `eeglab_resample`, `eeglab_reref`, `eeglab_select_channels`, `eeglab_interpolate_channels`, `eeglab_edit_channels`, `eeglab_clean_line_noise`, `eeglab_clean_rawdata`

**ICA 和伪迹 (5 个):** `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_flag_components`, `eeglab_remove_components`, `eeglab_reject_epochs`

**ERP 和分段 (5 个):** `eeglab_epoch`, `eeglab_erp_analysis`, `eeglab_sort_epochs`, `eeglab_average_erp`, `eeglab_get_events`

**频谱和连接性 (3 个):** `eeglab_spectral`, `eeglab_timefreq`, `eeglab_connectivity`

**可视化 (6 个):** `eeglab_topoplot`, `eeglab_plot_erp`, `eeglab_plot_timefreq`, `eeglab_plot_components`, `eeglab_plot_psd`, `eeglab_plot_connectivity`

**源定位和组分析 (6 个):** `eeglab_source_settings`, `eeglab_source_localization`, `eeglab_study_create`, `eeglab_study_design`, `eeglab_study_statistics`, `eeglab_pipeline`

**研究工作流 (9 个):** `eeglab_qc_report`, `eeglab_project_plan`, `eeglab_workflow_recommend`, `eeglab_method_preflight`, `eeglab_event_semantics_audit`, `eeglab_plugin_check`, `eeglab_protocol_export`, `eeglab_erp_light_workflow`, `eeglab_generate_report`

**执行规则:** 如果某个工具无法调用（如插件缺失、数据不适合，或该分支本来就不适用），必须在协议导出中明确记录原因、gate 状态和替代路径。"不需要"只有在分支矩阵或官方门控明确不适用时才成立。

### 参考文档覆盖要求

每次 EEG 分析会话必须在开始任何处理前读取全部 15 个参考文档：

1. `references/workflows.md` - 工作流配方
2. `references/setup.md` - 设置和验证
3. `references/tools.md` - 工具组和参数
4. `references/official-gates.md` - 官方方法门控
5. `references/official-method-map.md` - 官方方法映射
6. `references/gate-policy.md` - 门控策略
7. `references/method-gates.md` - 方法门控详情
8. `references/acquisition-to-derivatives.md` - 原始数据保留和导数
9. `references/event-semantics.md` - 事件歧义
10. `references/ica-iclabel-policy.md` - ICA/ICLabel 策略
11. `references/preprocessing-decision-tree.md` - 预处理决策树
12. `references/report-protocol-templates.md` - 报告模板
13. `references/source-policy.md` - 源定位策略
14. `references/statistics-reporting.md` - 统计报告
15. `references/bids-study-policy.md` - BIDS/STUDY 策略

**执行规则:** 必须使用 Read 工具读取每个参考文件并确认完成，然后才能开始任何数据处理。读取参考文档不是可选的。

### 官方文档覆盖要求

每次 EEG 分析会话还必须读取 `docs/` 文件夹中的全部 10 个官方文档（本地路径或全局 skill 目录下的 `docs/`）：

1. `docs/official-gate-policy.md` - 官方门控策略
2. `docs/official-method-map.md` - 官方方法映射
3. `docs/official-plugin-map.md` - 官方插件映射
4. `docs/official-report-field-matrix.md` - 官方报告字段矩阵
5. `docs/official-risk-matrix.md` - 官方风险矩阵
6. `docs/official-support-matrix.md` - 官方支持矩阵
7. `docs/official-tool-support-matrix.md` - 官方工具支持矩阵
8. `docs/official-topic-index.md` - 官方主题索引
9. `docs/research-standard.md` - 研究标准
10. `docs/user-workflows.md` - 用户工作流

**执行规则:** 必须使用 Read 工具读取每个 docs 文件并确认完成。这些文档是官方 EEGLAB 对齐的权威来源。如果 `references/` 和 `docs/` 之间存在冲突，以 `docs/` 为准。

### 工作流步骤强制执行

每个工作流步骤必须按顺序完成，不允许跳步：

1. **步骤 1 - 读取所有参考:** 读取全部 15 个参考文档和全部 10 个 docs 文档，确认每个都已读取
2. **步骤 2 - 插件检查:** 调用 `eeglab_plugin_check` 验证所有所需插件
3. **步骤 3 - 项目计划:** 调用 `eeglab_project_plan` 或 `eeglab_workflow_recommend`
4. **步骤 4 - 数据加载:** 调用 `eeglab_init`, `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, `eeglab_history`
5. **步骤 5 - 事件审计:** 如果存在事件，调用 `eeglab_event_semantics_audit`
6. **步骤 6 - 方法预检:** 在每个高风险工具前调用 `eeglab_method_preflight`
7. **步骤 7 - 预处理:** 应用滤波、工频噪声清理、重参考、通道处理
8. **步骤 8 - ICA/ICLabel:** 运行 ICA、分类成分、标记/移除伪迹
9. **步骤 9 - 分析:** 运行 ERP、频谱、时频、连接性或源定位分析
10. **步骤 10 - 可视化:** 生成所有所需图形
11. **步骤 11 - 保存:** 保存所有导数输出
12. **步骤 12 - 报告:** 调用 `eeglab_protocol_export` 包含完整 provenance

**执行规则:** 每个步骤必须产生明确输出后才能开始下一步。如果步骤失败，必须记录失败和恢复尝试后才能继续。

### 高风险工具门控执行

在调用以下任何高风险工具前，必须先调用 `eeglab_method_preflight`：

`eeglab_epoch`, `eeglab_erp_light_workflow`, `eeglab_timefreq`, `eeglab_plot_timefreq`, `eeglab_clean_rawdata`, `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_flag_components`, `eeglab_remove_components`, `eeglab_source_settings`, `eeglab_source_localization`, `eeglab_import_bids`, `eeglab_study_create`, `eeglab_study_design`, `eeglab_study_statistics`, `eeglab_filter`, `eeglab_resample`, `eeglab_reref`, `eeglab_reject_epochs`, `eeglab_clean_line_noise`, `eeglab_interpolate_channels`, `eeglab_edit_channels`, `eeglab_spectral`, `eeglab_connectivity`, `eeglab_topoplot`, `eeglab_pipeline`

**执行规则:** 如果 `gate_status=blocked`，必须停止并解释缺失的要求。未经用户批准的 `override_reason` 不得继续。如果批准覆盖，使用 `override_gate=true`, `override_reason` 和 `method_context` 调用工具。

### 工具调用跟踪

每次会话结束时，必须生成工具覆盖报告：

```
## 工具覆盖报告
- 已调用工具数: X/48
- 分支必需工具: [列表]
- 已调用工具: [列表]
- 条件性启用工具: [列表]
- 不适用/被阻断工具: [列表]
- 每个不适用/被阻断原因: [解释]
- 已读取参考: X/15
- 缺失参考: [列表]
- 已读取官方文档: X/10
- 缺失官方文档: [列表]
- 方法预检调用次数: X
- 未预检的高风险工具: [列表]
```

**执行规则:** 此报告必须包含在协议导出中。如果分支必需工具缺失且无有效理由，会话为"不合规"；不适用工具可以不调用，但必须说明为什么不调用。

### 违规处理

任何违反本强制执行协议的结果：
1. 立即暂停会话
2. 记录违规
3. 通知用户差距
4. 协议导出必须包含违规记录
5. 所有差距解决前，会话不能标记为"完成"

除非分析类型明确不需要且在协议中记录，否则没有工具调用是"可选"的。
