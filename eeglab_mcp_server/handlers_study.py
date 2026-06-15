"""STUDY and bundled pipeline handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.types import TextContent

try:
    from .runtime import (
        cfg,
        matlab,
        matlab_cell,
        matlab_string,
        _cell,
        _eeglab_init_code,
        _error_response,
        _maybe_init,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import (
        cfg,
        matlab,
        matlab_cell,
        matlab_string,
        _cell,
        _eeglab_init_code,
        _error_response,
        _maybe_init,
    )


async def _eeglab_study_create(args: dict) -> list[TextContent]:
    """创建 STUDY。"""
    bids_path = args.get("bids_path", "")
    study_name = args.get("study_name", "MyStudy")
    dataset_paths = args.get("dataset_paths", [])
    study_name_lit = matlab_string(study_name)

    if bids_path:
        bids_path_lit = matlab_string(bids_path)
        create_code = f"""
[STUDY, ALLEEG] = pop_importbids({bids_path_lit}, 'studyName', {study_name_lit}, 'bidsevent', 'on', 'bidschanloc', 'on');
"""
    elif dataset_paths:
        paths_str = matlab_cell(dataset_paths)
        create_code = f"""
[STUDY, ALLEEG] = pop_studywizard('dataset',{paths_str},'studyName',{study_name_lit});
"""
    else:
        return _error_response(
            "missing_required_argument",
            "请指定 bids_path 或 dataset_paths",
            next_step="传入 BIDS 根目录或 .set 文件路径列表后重试。",
        )

    code = f"""
{_maybe_init()}
{create_code}
STUDY = pop_study(STUDY, ALLEEG, 'name', {study_name_lit}, 'commands', {{}});
result.study_name = {study_name_lit};
result.num_datasets = length(ALLEEG);
result.subjects = {{STUDY.subject}};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_study_design(args: dict) -> list[TextContent]:
    """定义 STUDY 实验设计。"""
    design_name = args.get("design_name", "Design1")
    variable_name = args.get("variable_name", "condition")
    variable_values = args.get("variable_values", ["target", "standard"])

    vals_str = _cell(variable_values)
    design_name_lit = matlab_string(design_name)
    variable_name_lit = matlab_string(variable_name)

    code = f"""
{_maybe_init()}
STUDY = std_makedesign(STUDY, ALLEEG, 1, ...
    'name', {design_name_lit}, ...
    'variable1', {variable_name_lit}, ...
    'values1', {vals_str}, ...
    'vartype1', 'categorical', ...
    'subjselect', STUDY.subject);
result.design_name = {design_name_lit};
result.variable_name = {variable_name_lit};
result.variable_values = {vals_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_study_statistics(args: dict) -> list[TextContent]:
    """STUDY 统计检验。"""
    measure = args.get("measure", "erp")
    alpha = args.get("alpha", 0.05)
    correction = args.get("correction", "fdr")
    measure_lit = matlab_string(measure)
    correction_lit = matlab_string(correction)

    # Map measure to pop_statparams
    measure_map = {
        "erp": "'measure', 'erp'",
        "spectrum": "'measure', 'power'",
        "ersp": "'measure', 'ersp'",
    }
    measure_str = measure_map.get(measure, "'measure', 'erp'")

    # Map correction method
    correction_map = {
        "fdr": "'corr', 'FDR'",
        "bonferroni": "'corr', 'Bonferroni'",
        "cluster": "'corr', 'cluster'",
        "none": "'corr', 'none'",
    }
    correction_str = correction_map.get(correction, "'corr', 'FDR'")

    code = f"""
{_maybe_init()}
STUDY = pop_statparams(STUDY, {measure_str}, {correction_str}, 'alpha', {alpha});
[STUDY, stats] = pop_stat(EEG, STUDY, ALLEEG);
result.measure = {measure_lit};
result.alpha = {alpha};
result.correction = {correction_lit};
if exist('stats', 'var') && ~isempty(stats)
    result.stat_summary = struct();
    if isfield(stats, 'pvalue')
        result.stat_summary.significant_channels = sum(stats.pvalue < {alpha});
        result.stat_summary.min_pvalue = min(stats.pvalue);
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_pipeline(args: dict) -> list[TextContent]:
    """一键流程生成。"""
    pipeline_type = args["pipeline_type"]
    data_path = args["data_path"]
    output_dir = args.get("output_dir", "")
    highpass = args.get("highpass", 1.0)
    lowpass = args.get("lowpass", 40.0)
    event_types = args.get("event_types", [])
    epoch_window = args.get("epoch_window", [-0.2, 0.8])
    baseline_window = args.get("baseline_window", [-200, 0])
    ica_algorithm = args.get("ica_algorithm", "picard")
    burst_criterion = args.get("burst_criterion", 20)

    if not output_dir:
        output_dir = str(Path(cfg.EEGLAB_WORK_DIR) / f"{pipeline_type}_pipeline")

    ext = Path(data_path).suffix.lower().lstrip(".")
    data_path_lit = matlab_string(data_path)
    output_dir_lit = matlab_string(output_dir)
    ica_algorithm_lit = matlab_string(ica_algorithm)

    # 加载数据
    if ext == "set":
        fp = Path(data_path)
        load_code = (
            f"EEG = pop_loadset('filename',{matlab_string(fp.name)},'filepath',{matlab_string(str(fp.parent))});\n"
        )
    else:
        load_code = f"EEG = pop_biosig({data_path_lit});\n"

    # 公共预处理步骤
    common_steps = f"""
%% 1. 加载数据
{load_code}
EEG = eeg_checkset(EEG);

%% 2. 降采样（如果采样率过高）
if EEG.srate > 500
    EEG = pop_resample(EEG, 250);
    EEG = eeg_checkset(EEG);
end

%% 3. 滤波
EEG = pop_eegfiltnew(EEG, 'locutoff', {highpass}, 'hicutoff', {lowpass});
EEG = eeg_checkset(EEG);

%% 4. ASR 伪迹去除
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion', 5, 'ChannelCriterion', 0.8, 'LineNoiseCriterion', 4, 'Highpass', [0.25 0.75], 'BurstCriterion', {burst_criterion}, 'BurstRejection', 'on', 'WindowCriterion', 0.25, 'Distance', 'Euclidian', 'WindowCriterionTolerances', [-Inf 7]);
EEG = eeg_checkset(EEG);

%% 5. 重参考（平均参考）
EEG = pop_reref(EEG, []);
EEG = eeg_checkset(EEG);

%% 6. ICA 分解
EEG = pop_runica(EEG, 'icatype', {ica_algorithm_lit}, 'extended', 1, 'pca', EEG.nbchan-1);
EEG = eeg_checkset(EEG);

%% 7. ICLabel 分类
EEG = pop_iclabel(EEG);
EEG = eeg_checkset(EEG);

%% 8. 标记和移除伪迹成分
EEG = pop_icflag(EEG, [NaN NaN; 0.9 1; 0.9 1; NaN NaN; NaN NaN; NaN NaN; NaN NaN]);
EEG = pop_subcomp(EEG, find(EEG.reject.gcompreject), 0);
EEG = eeg_checkset(EEG);

%% 9. 通道插值
EEG = pop_interp(EEG, EEG.urchanlocs, 'spherical');
EEG = eeg_checkset(EEG);

%% 10. 再次重参考
EEG = pop_reref(EEG, []);
EEG = eeg_checkset(EEG);
"""

    if pipeline_type == "erp":
        events = event_types if event_types else ["stimulus"]
        events_str = _cell(events)
        pipeline_code = f"""
{common_steps}
%% 11. 分段
EEG = pop_epoch(EEG, {events_str}, [{epoch_window[0]}, {epoch_window[1]}], 'epochinfo', 'on');
EEG = eeg_checkset(EEG);

%% 12. 基线校正
baseline_requested = [{baseline_window[0]}, {baseline_window[1]}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
EEG = eeg_checkset(EEG);

%% 13. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'erp_processed.set', 'filepath', output_dir);
result.pipeline_type = 'erp';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'erp_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'epoch', 'baseline', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.trials = EEG.trials;
disp('ERP pipeline complete.');
"""

    elif pipeline_type == "resting":
        pipeline_code = f"""
{common_steps}
%% 11. 频谱分析
[spectra, freqs] = pop_spectopo(EEG, 1, EEG.pnts, 'EEG', EEG, 'freqrange', [0.5, 45]);

%% 12. 计算各频段功率
bands = struct();
band_names = {{'delta', 'theta', 'alpha', 'beta', 'gamma'}};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 45];
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_pow = mean(10*log10(spectra(fmask,:)), 2);
        bands.(band_names{{b}}).mean_power = mean(band_pow);
        bands.(band_names{{b}}).freq_range = band_ranges(b,:);
    end
end

%% 13. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'resting_processed.set', 'filepath', output_dir);
save(fullfile(output_dir, 'spectra.mat'), 'spectra', 'freqs');
result.pipeline_type = 'resting';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'resting_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'spectral', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.band_power = bands;
disp('Resting-state pipeline complete.');
"""

    elif pipeline_type == "timefreq":
        events = event_types if event_types else ["stimulus"]
        events_str = _cell(events)
        pipeline_code = f"""
{common_steps}
%% 11. 分段
EEG = pop_epoch(EEG, {events_str}, [{epoch_window[0]}, {epoch_window[1]}], 'epochinfo', 'on');
EEG = eeg_checkset(EEG);

%% 12. 基线校正
baseline_requested = [{baseline_window[0]}, {baseline_window[1]}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
EEG = eeg_checkset(EEG);

%% 13. 时频分析
[ERSP, ITC, times, freqs] = pop_newtimef(EEG, 1, 1:EEG.nbchan, ...
    [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
    'freqs', [3 80], 'cycles', [3 10], ...
    'baseline', [{baseline_window[0]}, {baseline_window[1]}]);

%% 14. 保存
output_dir = {output_dir_lit};
mkdir(output_dir);
EEG = pop_saveset(EEG, 'filename', 'timefreq_processed.set', 'filepath', output_dir);
save(fullfile(output_dir, 'timefreq_results.mat'), 'ERSP', 'ITC', 'times', 'freqs');
result.pipeline_type = 'timefreq';
result.output_dir = output_dir;
result.output_file = fullfile(output_dir, 'timefreq_processed.set');
result.steps = {{'load', 'resample', 'filter', 'asr', 'reref', 'ica', 'iclabel', 'remove_artifacts', 'interpolate', 'reref', 'epoch', 'baseline', 'timefreq', 'save'}};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.trials = EEG.trials;
disp('Time-frequency pipeline complete.');
"""
    else:
        return _error_response(
            "invalid_arguments",
            f"不支持的流程类型: {pipeline_type}",
            next_step="pipeline_type 只能是 erp、resting 或 timefreq。",
        )

    code = f"""
{_eeglab_init_code()}
{pipeline_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
