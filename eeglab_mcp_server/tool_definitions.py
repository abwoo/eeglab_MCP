"""MCP Tool schema surface for the EEGLAB MCP server."""

from __future__ import annotations

from mcp.types import Tool

try:
    from .schemas import annotate_tools, workflow_tools
    from .tool_registry import validate_tool_definitions
except ImportError:  # pragma: no cover - direct script execution support
    from schemas import annotate_tools, workflow_tools
    from tool_registry import validate_tool_definitions


def build_tool_definitions() -> list[Tool]:
    """Build raw tool definitions with complete schemas for internal validation."""
    tools = [
        # ===== 第 1 类：数据管理 =====
        Tool(
            name="eeglab_init",
            description="初始化 EEGLAB 环境。在执行任何 EEGLAB 操作前必须先调用此工具。"
            "会启动 MATLAB 并加载 EEGLAB（无界面模式）。"
            "可选指定 EEGLAB 安装路径，否则使用环境变量 EEGLAB_PATH。",
            inputSchema={
                "type": "object",
                "properties": {
                    "eeglab_path": {
                        "type": "string",
                        "description": "EEGLAB 安装目录的绝对路径。例如: C:/eeglab2024.0 或 /home/user/eeglab",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_load_data",
            description="加载 EEG 数据文件。支持 EEGLAB 原生格式(.set/.fdt)、BrainVision(.vhdr)、"
            "EDF/EDF+(.edf)、BioSemi(.bdf)、Neuroscan(.cnt) 等格式。"
            "加载后数据存储在 MATLAB 工作区的 EEG 变量中，可供后续分析工具使用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "EEG 数据文件的绝对路径。例如: C:/data/subject01.set",
                    },
                    "filename": {
                        "type": "string",
                        "description": "文件名（当 filepath 仅指定目录时需要）。例如: subject01.set",
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="eeglab_save_data",
            description="保存当前 EEG 数据到文件（.set 格式）。"
            "在执行破坏性操作（如滤波、ICA 去伪迹）后建议保存数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "保存文件的绝对路径。例如: C:/data/subject01_filtered.set",
                    },
                    "filename": {
                        "type": "string",
                        "description": "保存的文件名。例如: subject01_filtered.set",
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="eeglab_import_bids",
            description="导入 BIDS 格式数据集。BIDS (Brain Imaging Data Structure) 是神经科学数据组织的标准格式。"
            "导入后自动创建 STUDY 和 ALLEEG，可进行组级别分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "BIDS 数据集根目录的绝对路径",
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY 名称",
                    },
                },
                "required": ["bids_path"],
            },
        ),
        Tool(
            name="eeglab_info",
            description="获取当前 EEG 数据集的详细信息。包括通道数、采样率、数据点数、试次数、"
            "时间窗口、通道标签、事件类型、ICA 状态等。用于了解数据概况和验证处理结果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_channels": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含通道标签列表",
                    },
                    "include_events": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含事件类型列表",
                    },
                    "include_ica": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否包含 ICA 信息",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_history",
            description="获取当前 EEG 数据集的操作历史记录。记录了从加载数据以来执行的所有 EEGLAB 操作。"
            "可用于追踪分析流程、验证处理步骤、复现分析过程。",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ===== 第 2 类：预处理 =====
        Tool(
            name="eeglab_filter",
            description="对 EEG 数据进行滤波处理。支持带通(bandpass)、高通(highpass)、低通(lowpass)和陷波(notch)滤波。"
            "使用 EEGLAB 推荐的 pop_eegfiltnew (FIR Hamming 窗) 和 pop_cleanline (陷波)。"
            "专业建议: ERP研究用 0.1-40Hz 带通; 时频研究用 0.5-80Hz 带通; "
            "50Hz(中国/欧洲)或60Hz(美国)陷波去工频; ICA 前建议高通 1Hz 滤波。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["bandpass", "highpass", "lowpass", "notch"],
                        "description": "滤波类型: bandpass(带通), highpass(高通), lowpass(低通), notch(陷波)",
                    },
                    "low_cutoff": {
                        "type": "number",
                        "description": "低截止频率(Hz)。带通/高通时必填。常用值: 0.1(去漂移), 0.5, 1(ICA前推荐)",
                    },
                    "high_cutoff": {
                        "type": "number",
                        "description": "高截止频率(Hz)。带通/低通时必填。常用值: 30, 40, 80, 100",
                    },
                    "notch_freq": {
                        "type": "number",
                        "description": "陷波频率(Hz)。notch 类型时必填。50(中国/欧洲)或60(美国)",
                    },
                    "notch_harmonics": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否同时去除陷波频率的谐波(如100Hz, 150Hz)",
                    },
                },
                "required": ["filter_type"],
            },
        ),
        Tool(
            name="eeglab_resample",
            description="对 EEG 数据进行重采样。降低采样率可减少数据量和计算时间。"
            "专业建议: 降采样前应先加低通抗混叠滤波; 常用目标采样率: 250Hz(ERP), 500Hz(时频)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "new_srate": {
                        "type": "number",
                        "description": "目标采样率(Hz)。例如: 250, 500",
                    }
                },
                "required": ["new_srate"],
            },
        ),
        Tool(
            name="eeglab_reref",
            description="对 EEG 数据进行重参考。支持平均参考(所有通道均值)、单通道参考(如 Cz, 乳突)和 REST 参考。"
            "专业建议: 平均参考是最常用的参考方式，适用于大多数研究场景; "
            "平均参考会使数据秩减 1，ICA 时需设置 pca=nchan-1; "
            "ICA 通常在重参考前运行，或使用平均参考。",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref_type": {
                        "type": "string",
                        "enum": ["average", "channel", "rest"],
                        "description": "参考类型: average(平均参考), channel(单通道参考), rest(REST参考)",
                    },
                    "ref_channel": {
                        "type": "string",
                        "description": "参考通道标签。ref_type 为 channel 时必填。例如: 'Cz', 'M1', 'A1'",
                    },
                },
                "required": ["ref_type"],
            },
        ),
        Tool(
            name="eeglab_select_channels",
            description="选择或排除特定通道。用于去除坏通道或只保留感兴趣的区域。"
            "专业建议: ICA 前应去除明显坏通道，但保留足够通道数; "
            "去除通道后再做 ICA 会降低成分数。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要保留的通道标签列表。例如: ['Fz','Cz','Pz']。与 exclude_channels 二选一",
                    },
                    "exclude_channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要排除的通道标签列表。例如: ['EOG1','EOG2','EMG']。与 channels 二选一",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_interpolate_channels",
            description="通道插值。使用球面样条插值法从周围通道估计坏通道的信号。"
            "专业建议: 应在 ICA 去伪迹后使用，而非之前; "
            "可使用 urchanlocs 恢复之前删除的通道。",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref_chanlocs": {
                        "type": "string",
                        "description": "参考通道位置。'urchanlocs' 恢复原始通道，或指定 .loc 文件路径。留空则使用当前通道位置",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["spherical", "v4"],
                        "default": "spherical",
                        "description": "插值方法: spherical(球面样条,推荐) 或 v4(双调和样条)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_edit_channels",
            description="编辑通道信息。加载 .loc 位置文件、重命名通道等。"
            "专业建议: 加载数据后应检查通道位置是否正确，否则地形图和源定位结果会出错。",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["load_loc", "rename"],
                        "description": "操作类型: load_loc(加载位置文件), rename(重命名通道)",
                    },
                    "loc_file": {
                        "type": "string",
                        "description": "通道位置文件路径(.loc/.ced)。action 为 load_loc 时必填",
                    },
                    "rename_map": {
                        "type": "object",
                        "description": '重命名映射，键为旧名称，值为新名称。action 为 rename 时必填。例如: {"Fp1":"E1", "Fp2":"E2"}',
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="eeglab_clean_line_noise",
            description="专用工频噪声去除工具。使用 clean_rawdata 插件的 pop_cleanline 函数。"
            "比简单陷波滤波更精确，可自适应估计和去除工频及其谐波。"
            "需要 clean_rawdata 插件。专业建议: 如果数据有明显的 50/60Hz 工频干扰，优先使用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "line_freq": {
                        "type": "number",
                        "default": 50,
                        "description": "工频频率(Hz)。50(中国/欧洲)或60(美国)",
                    },
                    "bandwidth": {
                        "type": "number",
                        "default": 2,
                        "description": "陷波带宽(Hz)",
                    },
                    "tau": {
                        "type": "number",
                        "default": 100,
                        "description": "平滑参数 tau",
                    },
                    "winsize": {
                        "type": "number",
                        "default": 4,
                        "description": "窗口大小(秒)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_clean_rawdata",
            description="ASR (Artifact Subspace Reconstruction) 伪迹去除。使用 clean_rawdata 插件。"
            "可自动检测和修复坏通道、去除高幅伪迹。"
            "专业建议: 在连续数据上运行（分段前）; ICA 前使用可提高 ICA 质量; "
            "burst_criterion: 5=激进, 20=保守, 40=温和。需要 clean_rawdata 插件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "flatline_criterion": {
                        "type": "number",
                        "default": 5,
                        "description": "平线检测阈值(秒)。通道信号标准差接近0超过此时长则标记为坏通道",
                    },
                    "channel_criterion": {
                        "type": "number",
                        "default": 0.8,
                        "description": "坏通道检测阈值(相关系数)。低于此值的通道被标记为坏通道",
                    },
                    "line_noise_criterion": {
                        "type": "number",
                        "default": 4,
                        "description": "工频噪声检测阈值(Z分数)",
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "突发伪迹检测阈值(Z分数)。5=激进, 20=保守, 40=温和",
                    },
                    "window_criterion": {
                        "type": "number",
                        "default": 0.25,
                        "description": "坏时间段检测阈值(比例)。超过此比例的窗口被标记为坏段",
                    },
                },
                "required": [],
            },
        ),
        # ===== 第 3 类：ICA 与伪迹处理 =====
        Tool(
            name="eeglab_run_ica",
            description="对 EEG 数据运行 ICA（独立成分分析）分解。ICA 用于分离脑源信号和伪迹成分（眼电、肌电、心电等）。"
            "专业建议: ICA 前建议高通 1Hz 滤波; 不要在 ICA 前做基线校正; "
            "平均参考会使秩减 1，需设置 pca=nchan-1; "
            "runica 和 picard 是 EEGLAB 内置算法; fastica 需要单独插件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "runica",
                        "description": "ICA 算法: runica(Infomax,默认稳定), picard(速度与精度平衡,推荐)",
                    },
                    "pca_components": {
                        "type": "integer",
                        "description": "PCA 降维后的成分数。不填则等于通道数。平均参考后建议设为 nchan-1",
                    },
                    "extended": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否使用扩展 Infomax(可分离超高斯和亚高斯分布)。推荐开启以更好地分离肌电伪迹",
                    },
                    "max_steps": {
                        "type": "integer",
                        "default": 512,
                        "description": "最大迭代步数。默认512，大数据集可增加到1000-2000",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_classify_ica",
            description="使用 ICLabel 自动分类 ICA 成分。ICLabel 是基于深度学习的自动分类工具，"
            "将每个 IC 成分分为: Brain(脑源), Muscle(肌电), Eye(眼电), Heart(心电), "
            "Line_Noise(工频), Channel_Noise(通道噪声), Other(其他) 七类。"
            "分类结果包含每个成分属于各类别的概率。需先运行 ICA 分解。需要 ICLabel 插件。",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="eeglab_flag_components",
            description="根据 ICLabel 分类概率标记 ICA 成分。可设置各类别的概率阈值来决定哪些成分应被标记为伪迹。"
            "专业建议: 常用策略是标记 Brain 概率低于 0.2 的成分，或标记 Muscle/Eye 概率高于 0.8 的成分。",
            inputSchema={
                "type": "object",
                "properties": {
                    "brain_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Brain 类别概率范围 [min, max]，超出此范围标记。例如: [0, 0.2] 标记 Brain<20% 的",
                    },
                    "muscle_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Muscle 类别概率范围 [min, max]，在此范围内标记。例如: [0.8, 1] 标记 Muscle>80%",
                    },
                    "eye_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Eye 类别概率范围 [min, max]。例如: [0.8, 1]",
                    },
                    "heart_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Heart 类别概率范围 [min, max]。例如: [0.8, 1]",
                    },
                    "line_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Line_Noise 类别概率范围 [min, max]",
                    },
                    "channel_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Channel_Noise 类别概率范围 [min, max]",
                    },
                    "other_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Other 类别概率范围 [min, max]",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_remove_components",
            description="移除指定的 ICA 伪迹成分并重建 EEG 数据。根据 ICLabel 分类结果或手动选择，"
            "移除非脑源成分（如眼电、肌电、心电、工频噪声等）。"
            "这是 ICA 去伪迹的核心步骤。建议先运行 eeglab_classify_ica 查看分类结果再决定移除哪些成分。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要移除的 IC 成分索引列表(从1开始)。例如: [2, 5, 7, 10]",
                    },
                    "auto_remove_brain_threshold": {
                        "type": "number",
                        "description": "自动移除模式: Brain 类别概率低于此阈值的成分将被移除。例如: 0.3 表示保留 Brain 概率>=30% 的成分。不填则使用手动 component_indices",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_reject_epochs",
            description="试次拒绝。根据阈值或联合概率方法拒绝包含伪迹的试次。"
            "专业建议: 分段后使用; 阈值应根据数据幅度设置（通常 ±100μV）; "
            "联合概率方法可检测多通道联合异常。",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["threshold", "joint_probability"],
                        "default": "threshold",
                        "description": "拒绝方法: threshold(阈值), joint_probability(联合概率)",
                    },
                    "threshold": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-100, 100],
                        "description": "阈值范围[下限μV, 上限μV]。method 为 threshold 时使用",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "检测的通道列表。留空则使用所有通道",
                    },
                    "jp_threshold": {
                        "type": "number",
                        "default": 3,
                        "description": "联合概率的 Z 分数阈值。method 为 joint_probability 时使用",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_get_events",
            description="获取当前 EEG 数据集的事件信息。查看可用事件类型和数量。"
            "用于了解数据中有哪些标记事件，以便后续分段和分析。",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        # ===== 第 4 类：分段与 ERP =====
        Tool(
            name="eeglab_epoch",
            description="对连续 EEG 数据进行分段和基线校正。根据事件类型将数据切分为试次。"
            "分段是 ERP 分析的必要步骤。专业建议: 常用时间窗 [-200, 800]ms (P300), "
            "[-200, 500]ms (N170); 基线校正使用刺激前时间段消除直流偏移; "
            "基线窗口通常与刺激前窗口相同。",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "用于分段的事件类型列表。例如: ['target', 'standard']。留空则使用所有事件",
                    },
                    "pre_stimulus": {
                        "type": "number",
                        "default": -0.2,
                        "description": "刺激前时间窗口(秒)。例如: -0.2 表示刺激前200ms",
                    },
                    "post_stimulus": {
                        "type": "number",
                        "default": 0.8,
                        "description": "刺激后时间窗口(秒)。例如: 0.8 表示刺激后800ms",
                    },
                    "baseline_start": {
                        "type": "number",
                        "default": -0.2,
                        "description": "基线校正起始时间(秒)。通常与 pre_stimulus 相同",
                    },
                    "baseline_end": {
                        "type": "number",
                        "default": 0,
                        "description": "基线校正结束时间(秒)。通常为0(刺激 onset)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_erp_analysis",
            description="ERP（事件相关电位）分析。计算各条件的平均 ERP 波形，支持按条件分组、"
            "选择通道、指定时间窗口。输出各条件在各通道的 ERP 均值、峰值及潜伏期。"
            "专业建议: 常用 ERP 成分: N1(80-150ms), P2(150-280ms), "
            "N170(140-200ms,颞枕区), P300(250-500ms,中央顶区), N400(300-500ms,中央区)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Fz', 'Cz', 'Pz']。留空则分析所有通道",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "分析的时间窗口[起始ms, 结束ms]。例如: [250, 500] 分析 P300 成分",
                    },
                    "peak_detection": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否在指定时间窗口内检测峰值(最大正波和最大负波)",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组分析。留空则分析所有试次的平均",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_sort_epochs",
            description="按条件排序试次。将试次按事件类型分组排序，便于后续分组分析。"
            "专业建议: 分段后使用; 排序后可用 eeglab_erp_analysis 按条件分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "description": "排序依据的事件类型字段名。例如: 'type'",
                    }
                },
                "required": ["sort_by"],
            },
        ),
        Tool(
            name="eeglab_average_erp",
            description="ERP 平均。按条件分组计算 ERP 平均波形。"
            "专业建议: 通常在分段和基线校正后使用; "
            "可按事件类型分组计算各条件的平均 ERP。",
            inputSchema={
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组。留空则计算所有试次的总体平均",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "计算的通道列表。留空则计算所有通道",
                    },
                },
                "required": [],
            },
        ),
        # ===== 第 5 类：频域与时频 =====
        Tool(
            name="eeglab_spectral",
            description="频谱/功率谱密度(PSD)分析。使用 Welch 方法计算各通道的功率谱密度。"
            "输出各频段(Delta/Theta/Alpha/Beta/Gamma)的绝对功率和相对功率。"
            "专业建议: 频段定义: Delta(0.5-4Hz), Theta(4-8Hz), Alpha(8-13Hz), "
            "Beta(13-30Hz), Gamma(30-80Hz); 静息态分析常用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Oz', 'Pz']。留空则分析所有通道",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [0.5, 100],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [0.5, 100]",
                    },
                    "band_power": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否计算各频段(Delta/Theta/Alpha/Beta/Gamma)的功率",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_timefreq",
            description="时频分析。计算 EEG 信号的事件相关谱扰动(ERSP)和跨试次相干性(ITC)。"
            "支持 Morlet 小波变换。"
            "ERSP 反映各频段能量随时间的变化; ITC 反映各频段相位锁定程度。"
            "专业建议: 频率范围 3-80Hz; 周期数 3-10(低频到高频线性增长); "
            "需要分段数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Cz', 'Pz']。留空则分析所有通道",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [3, 80],
                        "description": "频率范围[最低Hz, 最高Hz]。例如: [3, 80]",
                    },
                    "cycles": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 3,
                        "default": [3, 10],
                        "description": "小波周期数。2个值: [起始, 结束]; 3个值: [起始, 增长率, 结束]。默认: [3, 10]",
                    },
                    "baseline": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-200, 0],
                        "description": "基线窗口[起始ms, 结束ms]。默认: [-200, 0] 刺激前200ms",
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["ersp", "itc", "both"],
                        "default": "both",
                        "description": "输出类型: ersp(仅功率), itc(仅相位一致性), both(两者)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_connectivity",
            description="功能连接分析。计算通道间的相干性(Coherence)和相位锁定值(PLV)。"
            "专业建议: 相干性反映两个信号在不同频率上的线性关系; "
            "PLV 反映相位同步程度; 常用于静息态脑网络分析。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。留空则分析所有通道",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["coherence", "plv"],
                        "default": "coherence",
                        "description": "连接性度量: coherence(相干性), plv(相位锁定值)",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [8, 13],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [8, 13] Alpha 频段",
                    },
                },
                "required": [],
            },
        ),
        # ===== 第 6 类：可视化 =====
        Tool(
            name="eeglab_topoplot",
            description="绘制头皮地形图(Topography)。将 EEG 信号在头皮上的分布以等高线图形式展示。"
            "支持绘制特定时间点或时间窗的平均电位分布。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_point": {
                        "type": "number",
                        "description": "绘制的时间点(ms)。例如: 300 表示刺激后300ms。与 time_window 二选一",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "绘制的时间窗平均值[起始ms, 结束ms]。例如: [250, 350] 表示 P300 时间窗。与 time_point 二选一",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "绘制的通道列表。留空则使用所有通道",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径。例如: C:/results/topo_300ms.png",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_erp",
            description="绘制 ERP 波形图。显示指定通道的 ERP 平均波形。"
            "支持按条件分组绘制、添加置信区间。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "绘制的通道列表。例如: ['Fz', 'Cz', 'Pz']",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按条件分组绘制。留空则绘制所有试次平均",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["channels", "output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_timefreq",
            description="绘制时频图。显示指定通道的 ERSP 和/或 ITC 时频图。"
            "需要先运行 eeglab_timefreq 获取时频数据。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "绘制的通道标签。例如: 'Cz'",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径",
                    },
                    "plot_ersp": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否绘制 ERSP 图",
                    },
                    "plot_itc": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否绘制 ITC 图",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["channel", "output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_components",
            description="绘制 ICA 成分图。显示每个 IC 成分的头皮拓扑图和功率谱。"
            "用于人工检查和判断 ICA 成分性质。图形保存为 PNG 文件。"
            "专业建议: 需先运行 ICA 分解; 可结合 ICLabel 分类结果判断成分性质。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要绘制的 IC 成分索引列表(从1开始)。留空则绘制前 10 个",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_psd",
            description="绘制功率谱密度(PSD)图。显示指定通道的功率谱密度。"
            "支持按频段分析、多通道叠加。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "绘制的通道列表。例如: ['Oz', 'Pz']。留空则绘制所有通道",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [0.5, 100],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [0.5, 100]",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_connectivity",
            description="绘制连接性矩阵图。显示通道间的相干性或PLV连接矩阵。"
            "用于可视化脑功能网络连接。图形保存为 PNG 文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分析的通道列表。例如: ['Fz', 'Cz', 'Pz']。留空则分析所有通道",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出图片的绝对路径",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["coherence", "plv"],
                        "default": "coherence",
                        "description": "连接性度量: coherence(相干性), plv(相位锁定值)",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [8, 13],
                        "description": "频率范围[最低Hz, 最高Hz]。默认: [8, 13] Alpha 频段",
                    },
                    "title": {"type": "string", "description": "图形标题"},
                },
                "required": ["output_path"],
            },
        ),
        # ===== 第 7 类：源定位 =====
        Tool(
            name="eeglab_source_localization",
            description="源定位分析（偶极子拟合）。使用 EEGLAB 内置的 Dipfit 工具对 ICA 成分进行偶极子拟合，"
            "估计脑内信号源的位置。需要先运行 ICA 分解。"
            "输出偶极子的 MNI 坐标、残差方差等。专业建议: 拟合前需确保通道位置正确; "
            "残差方差 < 15% 表示拟合良好。需要 Dipfit 插件（EEGLAB 内置）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要拟合的 IC 成分索引列表。留空则拟合所有成分",
                    },
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "头模型类型: bem(边界元模型,推荐) 或 spherical(球模型,快速)",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "模板脑: mni(MNI305,默认) 或 colin27(Colin27 高分辨率)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_source_settings",
            description="Dipfit 模型设置。配置头模型、模板脑、通道位置文件等参数。"
            "专业建议: 在运行源定位前应先设置正确的参数; "
            "BEM 模型更精确但计算更慢; 球模型快速但精度较低。",
            inputSchema={
                "type": "object",
                "properties": {
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "头模型类型: bem(边界元模型) 或 spherical(球模型)",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "模板脑: mni(MNI305) 或 colin27(Colin27)",
                    },
                    "chanfile": {
                        "type": "string",
                        "description": "通道位置文件路径。留空使用默认",
                    },
                    "mrifile": {
                        "type": "string",
                        "description": "MRI 模板文件路径。留空使用默认",
                    },
                },
                "required": [],
            },
        ),
        # ===== 第 8 类：组分析与 Pipeline =====
        Tool(
            name="eeglab_study_create",
            description="创建 EEGLAB STUDY 用于组级别分析。可从 BIDS 目录或多个 .set 文件创建。"
            "专业建议: STUDY 是 EEGLAB 进行组级别分析的基础; "
            "创建后需定义实验设计才能进行统计检验。",
            inputSchema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "BIDS 数据集根目录路径。与 dataset_paths 二选一",
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY 名称",
                    },
                    "dataset_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "EEG 数据文件路径列表。与 bids_path 二选一",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_study_design",
            description="定义 STUDY 实验设计。设置自变量及其水平，用于后续统计检验。"
            "专业建议: 必须在统计检验前定义设计; "
            "可定义多个自变量（如组别×条件）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "design_name": {
                        "type": "string",
                        "default": "Design1",
                        "description": "设计名称",
                    },
                    "variable_name": {
                        "type": "string",
                        "default": "condition",
                        "description": "自变量名称。例如: 'condition', 'group'",
                    },
                    "variable_values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["target", "standard"],
                        "description": "自变量水平。例如: ['control', 'patient'] 或 ['target', 'standard']",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_study_statistics",
            description="STUDY 统计检验。使用聚类置换检验进行组级别统计推断。"
            "专业建议: 聚类置换检验可有效控制多重比较; "
            "常用阈值: p < 0.05, 聚类阈值 FDR 或 FWE 校正。",
            inputSchema={
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "enum": ["erp", "spectrum", "ersp"],
                        "default": "erp",
                        "description": "统计检验的测量类型: erp(ERP波形), spectrum(频谱), ersp(时频)",
                    },
                    "alpha": {
                        "type": "number",
                        "default": 0.05,
                        "description": "显著性水平。默认: 0.05",
                    },
                    "correction": {
                        "type": "string",
                        "enum": ["fdr", "bonferroni", "cluster", "none"],
                        "default": "fdr",
                        "description": "多重比较校正方法: fdr(FDR), bonferroni(Bonferroni), cluster(聚类), none(无校正)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_pipeline",
            description="一键流程生成。根据分析类型自动生成完整的预处理和分析流程。"
            "支持 ERP 分析流程、静息态分析流程和时频分析流程。"
            "专业建议: ERP 流程: 滤波→ASR→重参考→ICA→ICLabel→去伪迹→插值→分段→基线→保存; "
            "静息态流程: 滤波→ASR→重参考→ICA→ICLabel→去伪迹→频谱分析→保存。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["erp", "resting", "timefreq"],
                        "description": "流程类型: erp(ERP分析), resting(静息态), timefreq(时频分析)",
                    },
                    "data_path": {"type": "string", "description": "输入数据文件路径"},
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录路径。留空则使用工作目录",
                    },
                    "highpass": {
                        "type": "number",
                        "default": 1.0,
                        "description": "高通滤波截止频率(Hz)。默认: 1.0 (ICA 前推荐)",
                    },
                    "lowpass": {
                        "type": "number",
                        "default": 40.0,
                        "description": "低通滤波截止频率(Hz)。默认: 40.0",
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "分段用的事件类型。pipeline_type 为 erp 或 timefreq 时使用",
                    },
                    "epoch_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-0.2, 0.8],
                        "description": "分段时间窗[起始秒, 结束秒]。默认: [-0.2, 0.8]",
                    },
                    "baseline_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-200, 0],
                        "description": "基线校正窗口[起始ms, 结束ms]。默认: [-200, 0]",
                    },
                    "ica_algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "picard",
                        "description": "ICA 算法。默认: picard",
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "ASR 突发伪迹检测阈值。5=激进, 20=保守, 40=温和",
                    },
                },
                "required": ["pipeline_type", "data_path"],
            },
        ),
        # ===== 第 8 类：报告生成 =====
        Tool(
            name="eeglab_generate_report",
            description="生成标准 EEG 研究分析报告。根据分析结果（记录信息、预处理参数、分析参数、图片、结果等）自动生成 Markdown 或 HTML 格式的完整研究报告。遵循 official-report-field-matrix.md 字段要求。",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "报告输出文件路径。例如: /path/to/report.md 或 /path/to/report.html",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "html"],
                        "default": "markdown",
                        "description": "报告格式。默认: markdown",
                    },
                    "title": {
                        "type": "string",
                        "description": "报告标题",
                    },
                    "author": {
                        "type": "string",
                        "description": "报告作者",
                    },
                    "abstract": {
                        "type": "string",
                        "description": "摘要",
                    },
                    "recording": {
                        "type": "object",
                        "description": "记录和采集信息（input_path, sampling_rate, channels, event_count 等）",
                    },
                    "preprocessing": {
                        "type": "object",
                        "description": "预处理参数（filter, line_noise, rereference, ica_algorithm 等）",
                    },
                    "analysis": {
                        "type": "object",
                        "description": "分析参数（erp, spectral, timefreq, connectivity, source）",
                    },
                    "figures": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "caption": {"type": "string"},
                                "description": {"type": "string"},
                            },
                        },
                        "description": "生成的图片列表，每个包含 path, caption, description",
                    },
                    "results": {
                        "type": "object",
                        "description": "分析结果",
                    },
                    "discussion": {
                        "type": "string",
                        "description": "讨论",
                    },
                    "limitations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "局限性列表",
                    },
                    "gate_results": {
                        "type": "object",
                        "description": "官方 gate 状态",
                    },
                    "override_used": {
                        "type": "boolean",
                        "description": "是否使用了 override",
                    },
                    "override_reason": {
                        "type": "string",
                        "description": "override 原因",
                    },
                    "appendix": {
                        "type": "object",
                        "description": "附录（software, plugins, generated_files）",
                    },
                },
                "required": ["output_path"],
            },
        ),
    ]
    all_tools = annotate_tools(tools + workflow_tools())
    registry_errors = validate_tool_definitions(all_tools)
    if registry_errors:
        raise RuntimeError("Tool registry mismatch: " + "; ".join(registry_errors))
    return all_tools
