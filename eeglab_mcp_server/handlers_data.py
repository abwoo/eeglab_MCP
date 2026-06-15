"""Data-management handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json
import os

from mcp.types import TextContent

try:
    from .runtime import cfg, matlab, matlab_string, _maybe_init, _eeglab_init_code
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import cfg, matlab, matlab_string, _maybe_init, _eeglab_init_code


async def _eeglab_init(args: dict) -> list[TextContent]:
    """初始化 EEGLAB 环境。"""
    eeglab_path = args.get("eeglab_path", "")
    if eeglab_path:
        cfg.EEGLAB_PATH = eeglab_path
        os.environ["EEGLAB_PATH"] = eeglab_path
        matlab.eeglab_initialized = False

    init_code = _eeglab_init_code()
    code = f"""
{init_code}
try
    v = eeg_getversion;
    result.version = v;
    result.eeglabpath = which('eeglab');
catch
    result.version = 'unknown';
    result.eeglabpath = 'not found';
end
"""

    result = await matlab.execute(code)
    is_success = result.get("status") == "success"
    matlab.eeglab_initialized = is_success

    output = {
        "status": result.get("status", "unknown"),
        "message": "EEGLAB 初始化成功" if is_success else "EEGLAB 初始化失败",
        "eeglab_version": result.get("version", "unknown"),
        "eeglab_path": result.get("eeglabpath", "unknown"),
        "custom_path": eeglab_path or cfg.EEGLAB_PATH or "未设置",
    }
    if result.get("status") == "error":
        output["error"] = result.get("error", "")

    return [TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]


async def _eeglab_load_data(args: dict) -> list[TextContent]:
    """加载 EEG 数据文件。"""
    filepath = args["filepath"]
    filename = args.get("filename", "")
    filepath_lit = matlab_string(filepath)
    filename_lit = matlab_string(filename)

    if filename:
        load_code = f"""
[fpath, ~, ~] = fileparts({filepath_lit});
EEG = pop_loadset('filename', {filename_lit}, 'filepath', fpath);
"""
    else:
        load_code = f"""
[fpath, fname, fext] = fileparts({filepath_lit});
if strcmp(fext, '.edf') || strcmp(fext, '.bdf')
    EEG = pop_biosig({filepath_lit});
elseif strcmp(fext, '.vhdr')
    EEG = pop_loadbv(fpath, [fname fext]);
elseif strcmp(fext, '.cnt')
    EEG = pop_loadcnt({filepath_lit});
else
    EEG = pop_loadset('filename', [fname fext], 'filepath', fpath);
end
"""

    code = f"""
{_maybe_init()}
{load_code}
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
result.xmin = EEG.xmin;
result.xmax = EEG.xmax;
result.duration_sec = EEG.pnts / EEG.srate;
result.setname = EEG.setname;
result.channel_labels = {{EEG.chanlocs.labels}};
if isfield(EEG, 'event') && ~isempty(EEG.event)
    event_types = unique({{EEG.event.type}});
    result.event_types = event_types;
    result.num_events = length(EEG.event);
else
    result.event_types = {{}};
    result.num_events = 0;
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_save_data(args: dict) -> list[TextContent]:
    """保存 EEG 数据到文件。"""
    filepath = args["filepath"]
    filename = args.get("filename", "")
    filepath_lit = matlab_string(filepath)
    filename_lit = matlab_string(filename)

    if filename:
        save_code = f"""
[fpath, ~, ~] = fileparts({filepath_lit});
EEG = pop_saveset(EEG, 'filename', {filename_lit}, 'filepath', fpath);
result.saved_path = fullfile(fpath, {filename_lit});
"""
    else:
        save_code = f"""
[fpath, fname, fext] = fileparts({filepath_lit});
EEG = pop_saveset(EEG, 'filename', [fname fext], 'filepath', fpath);
result.saved_path = {filepath_lit};
"""

    code = f"""
{_maybe_init()}
{save_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_import_bids(args: dict) -> list[TextContent]:
    """导入 BIDS 格式数据集。"""
    bids_path = args["bids_path"]
    study_name = args.get("study_name", "MyStudy")
    bids_path_lit = matlab_string(bids_path)
    study_name_lit = matlab_string(study_name)

    code = f"""
{_maybe_init()}
[STUDY, ALLEEG] = pop_importbids({bids_path_lit}, 'studyName', {study_name_lit}, 'bidsevent', 'on', 'bidschanloc', 'on');
result.study_name = {study_name_lit};
result.num_datasets = length(ALLEEG);
result.subjects = {{STUDY.subject}};
EEG = ALLEEG(1);
result.first_dataset.nbchan = EEG.nbchan;
result.first_dataset.srate = EEG.srate;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_info(args: dict) -> list[TextContent]:
    """获取当前 EEG 数据集的详细信息。"""
    include_ch = args.get("include_channels", True)
    include_ev = args.get("include_events", True)
    include_ica = args.get("include_ica", True)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG)
    result.status = 'error';
    result.error = '当前没有加载 EEG 数据，请先调用 eeglab_load_data';
else
    result.nbchan = EEG.nbchan;
    result.srate = EEG.srate;
    result.pnts = EEG.pnts;
    result.trials = EEG.trials;
    result.xmin = EEG.xmin;
    result.xmax = EEG.xmax;
    result.duration_sec = EEG.pnts / EEG.srate;
    result.total_duration_min = EEG.pnts / EEG.srate / 60;
    result.setname = EEG.setname;
    result.filename = EEG.filename;
    result.filepath = EEG.filepath;
    result.saved = EEG.saved;
    result.recording = struct();
    result.recording.sampling_rate_hz = EEG.srate;
    result.recording.channel_count = EEG.nbchan;
    result.recording.points_per_epoch = EEG.pnts;
    result.recording.trials = EEG.trials;
    result.recording.xmin_sec = EEG.xmin;
    result.recording.xmax_sec = EEG.xmax;
    result.recording.epoch_duration_sec = EEG.pnts / EEG.srate;
    result.recording.total_data_duration_sec = EEG.pnts * max(1, EEG.trials) / EEG.srate;
    if EEG.trials > 1
        result.recording.data_shape = 'epoched';
    else
        result.recording.data_shape = 'continuous_or_single_trial';
    end
    result.recording.setname = EEG.setname;
    result.recording.filename = EEG.filename;
    result.recording.filepath = EEG.filepath;
    result.recording.saved_state = EEG.saved;
    if isfield(EEG, 'comments') && ~isempty(EEG.comments)
        result.recording.comments = EEG.comments;
        result.recording.has_comments = true;
    else
        result.recording.comments = '';
        result.recording.has_comments = false;
    end
    if isfield(EEG, 'ref') && ~isempty(EEG.ref)
        result.recording.reference = EEG.ref;
    end
    if isfield(EEG, 'etc') && ~isempty(EEG.etc)
        result.recording.has_etc_metadata = true;
    else
        result.recording.has_etc_metadata = false;
    end
    result.processing_history_available = isfield(EEG, 'history') && ~isempty(EEG.history);
"""

    if include_ch:
        code += """
    if isfield(EEG, 'chanlocs') && ~isempty(EEG.chanlocs)
        if isfield(EEG.chanlocs, 'labels')
            result.channel_labels = {EEG.chanlocs.labels};
        else
            result.channel_labels = {};
        end
        located = false(1, length(EEG.chanlocs));
        for ci = 1:length(EEG.chanlocs)
            has_xyz = isfield(EEG.chanlocs, 'X') && ~isempty(EEG.chanlocs(ci).X) && ...
                isfield(EEG.chanlocs, 'Y') && ~isempty(EEG.chanlocs(ci).Y) && ...
                isfield(EEG.chanlocs, 'Z') && ~isempty(EEG.chanlocs(ci).Z);
            has_polar = isfield(EEG.chanlocs, 'theta') && ~isempty(EEG.chanlocs(ci).theta) && ...
                isfield(EEG.chanlocs, 'radius') && ~isempty(EEG.chanlocs(ci).radius);
            located(ci) = has_xyz || has_polar;
        end
        result.channels_with_locations = sum(located);
        result.channels_missing_locations = max(0, EEG.nbchan - sum(located));
        result.has_channel_locations = sum(located) == EEG.nbchan && EEG.nbchan > 0;
        result.channel_location_coverage = sum(located) / max(1, EEG.nbchan);
        if isfield(EEG.chanlocs, 'ref')
            refs = unique({EEG.chanlocs.ref});
            result.reference = refs;
        end
    else
        result.channel_labels = {};
        result.channels_with_locations = 0;
        result.channels_missing_locations = EEG.nbchan;
        result.has_channel_locations = false;
        result.channel_location_coverage = 0;
    end
"""

    if include_ev:
        code += """
    if isfield(EEG, 'event') && ~isempty(EEG.event)
        event_types = unique({EEG.event.type});
        result.event_types = event_types;
        result.num_events = length(EEG.event);
        if isfield(EEG.event, 'latency')
            latencies = [EEG.event.latency];
            result.event_latency_range_samples = [min(latencies), max(latencies)];
            result.event_latency_range_sec = [min(latencies) / EEG.srate, max(latencies) / EEG.srate];
        end
        result.has_urevent_links = isfield(EEG.event, 'urevent');
        if isfield(EEG, 'urevent') && ~isempty(EEG.urevent)
            result.num_urevents = length(EEG.urevent);
        else
            result.num_urevents = 0;
        end
        for i = 1:length(event_types)
            cnt = sum(strcmp({EEG.event.type}, event_types{i}));
            result.event_counts.(event_types{i}) = cnt;
        end
    else
        result.event_types = {};
        result.num_events = 0;
        result.num_urevents = 0;
        result.has_urevent_links = false;
    end
"""

    if include_ica:
        code += """
    if isfield(EEG, 'icaweights') && ~isempty(EEG.icaweights)
        result.ica_computed = true;
        result.ica_ncomponents = size(EEG.icaweights, 1);
        if isfield(EEG, 'etc') && isfield(EEG.etc, 'ic_classification') && isfield(EEG.etc.ic_classification, 'ICLabel')
            result.ica_classified = true;
            classifications = EEG.etc.ic_classification.ICLabel.classifications;
            labels = {'Brain', 'Muscle', 'Eye', 'Heart', 'Line_Noise', 'Channel_Noise', 'Other'};
            [~, max_idx] = max(classifications, [], 2);
            result.ica_classification_summary = struct();
            for i = 1:length(labels)
                cnt = sum(max_idx == i);
                result.ica_classification_summary.(labels{i}) = cnt;
            end
        else
            result.ica_classified = false;
        end
    else
        result.ica_computed = false;
        result.ica_ncomponents = 0;
        result.ica_classified = false;
    end
"""

    code += "end\n"

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_history(args: dict) -> list[TextContent]:
    """获取操作历史记录。"""
    code = f"""
{_maybe_init()}
if exist('EEG', 'var') && isstruct(EEG) && isfield(EEG, 'history') && ~isempty(EEG.history)
    result.history = EEG.history;
else
    result.history = '无操作历史记录';
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
