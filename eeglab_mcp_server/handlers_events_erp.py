"""Event, epoch, and ERP handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json

from mcp.types import TextContent

try:
    from .runtime import matlab, matlab_string, _cell, _error_response, _maybe_init
    from .schemas import validate_analysis_windows
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, matlab_string, _cell, _error_response, _maybe_init
    from schemas import validate_analysis_windows


async def _eeglab_reject_epochs(args: dict) -> list[TextContent]:
    """试次拒绝。"""
    method = args.get("method", "threshold")
    threshold = args.get("threshold", [-100, 100])
    channels = args.get("channels", [])
    jp_threshold = args.get("jp_threshold", 3)

    if method == "threshold":
        if channels:
            chan_str = _cell(channels)
            chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
        else:
            chan_code = "chan_idx = 1:EEG.nbchan;"

        # Bug fix: pop_eegthresh 中 Python None -> MATLAB []
        reject_code = f"""
{chan_code}
EEG = pop_eegthresh(EEG, [], EEG, 1, chan_idx, {threshold[0]}, {threshold[1]}, 0, 0);
result.method = 'threshold';
result.threshold = [{threshold[0]}, {threshold[1]}];
result.remaining_trials = EEG.trials;
result.rejected_trials = EEG.trials;
"""
    else:  # joint_probability
        if channels:
            chan_str = _cell(channels)
            chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
        else:
            chan_code = "chan_idx = 1:EEG.nbchan;"

        reject_code = f"""
{chan_code}
EEG = pop_jointprob(EEG, [], EEG, 1, chan_idx, {jp_threshold}, {jp_threshold});
result.method = 'joint_probability';
result.jp_threshold = {jp_threshold};
result.remaining_trials = EEG.trials;
"""

    code = f"""
{_maybe_init()}
{reject_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_get_events(args: dict) -> list[TextContent]:
    """获取事件信息。"""
    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG)
    result.status = 'error';
    result.error = '当前没有加载 EEG 数据，请先调用 eeglab_load_data';
elseif ~isfield(EEG, 'event') || isempty(EEG.event)
    result.num_events = 0;
    result.event_types = {{}};
    result.event_counts = struct();
else
    event_types = unique({{EEG.event.type}});
    result.num_events = length(EEG.event);
    result.event_types = event_types;
    for i = 1:length(event_types)
        cnt = sum(strcmp({{EEG.event.type}}, event_types{{i}}));
        result.event_counts.(event_types{{i}}) = cnt;
    end
    if isfield(EEG.event, 'latency')
        result.latency_range = [min([EEG.event.latency]), max([EEG.event.latency])];
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_epoch(args: dict) -> list[TextContent]:
    """分段 + 基线校正。"""
    event_types = args.get("event_types", [])
    pre_stim = args.get("pre_stimulus", -0.2)
    post_stim = args.get("post_stimulus", 0.8)
    bl_start = args.get("baseline_start", -0.2)
    bl_end = args.get("baseline_end", 0)
    window_errors = validate_analysis_windows(
        epoch_window=[pre_stim, post_stim],
        baseline_window_ms=[bl_start * 1000, bl_end * 1000],
    )
    if window_errors:
        return _error_response(
            "invalid_analysis_window",
            f"分段/基线窗口不合法: {'; '.join(window_errors)}",
            next_step="确保 baseline_start/baseline_end 落在 pre_stimulus/post_stimulus 时间窗内。",
            details={"errors": window_errors},
        )

    if event_types:
        events_str = _cell(event_types)
    else:
        events_str = "{'all'}"

    # Bug fix: pop_epoch epochinfo 参数值应该是 'on' 而非 'yes'
    # Bug fix: 基线参数使用用户指定的 bl_start*1000 而非 EEG.xmin*1000
    code = f"""
{_maybe_init()}
EEG = pop_epoch(EEG, {events_str}, [{pre_stim}, {post_stim}], 'epochinfo', 'on');
baseline_requested = [{bl_start * 1000}, {bl_end * 1000}];
baseline_points = find(EEG.times >= baseline_requested(1) & EEG.times <= baseline_requested(2));
if isempty(baseline_points)
    error('No baseline samples found inside requested baseline window');
end
EEG = pop_rmbase(EEG, [], baseline_points);
result.trials = EEG.trials;
result.xmin = EEG.xmin;
result.xmax = EEG.xmax;
result.pnts = EEG.pnts;
result.baseline_requested = baseline_requested;
result.baseline_applied = [EEG.times(baseline_points(1)), EEG.times(baseline_points(end))];
result.baseline_points = [baseline_points(1), baseline_points(end)];
result.event_types = {events_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_erp_analysis(args: dict) -> list[TextContent]:
    """ERP 分析。"""
    channels = args.get("channels", [])
    time_window = args.get("time_window", [])
    peak_detection = args.get("peak_detection", True)
    conditions = args.get("conditions", [])

    if channels:
        chan_str = _cell(channels)
        chan_code = f"""
chan_labels = {chan_str};
[~, chan_idx] = ismember(chan_labels, {{EEG.chanlocs.labels}});
chan_idx = chan_idx(chan_idx > 0);
if isempty(chan_idx)
    error('No requested channels were found in EEG.chanlocs');
end
"""
    else:
        chan_code = "chan_idx = 1:EEG.nbchan;"

    if time_window and len(time_window) == 2:
        tw_code = f"time_mask = EEG.times >= {time_window[0]} & EEG.times <= {time_window[1]};"
        tw_vals = f"[{time_window[0]}, {time_window[1]}]"
    else:
        tw_code = "time_mask = true(size(EEG.times));"
        tw_vals = "[EEG.xmin*1000, EEG.xmax*1000]"

    # 按条件分组
    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"""
cond_names = {cond_str};
result.conditions = cond_names;
for c = 1:length(cond_names)
    cond_name = cond_names{{c}};
    cond_field = matlab.lang.makeValidName(char(cond_name));
    cond_trials = [];
    if isfield(EEG, 'epoch') && ~isempty(EEG.epoch)
        for ep = 1:length(EEG.epoch)
            ep_types = EEG.epoch(ep).eventtype;
            if ischar(ep_types)
                ep_types = {{ep_types}};
            elseif isnumeric(ep_types)
                ep_types = {{num2str(ep_types)}};
            end
            if any(strcmp(cellfun(@char, ep_types, 'UniformOutput', false), char(cond_name)))
                cond_trials(end+1) = ep; %#ok<AGROW>
            end
        end
    else
        cond_mask = strcmp({{EEG.event.type}}, cond_name);
        cond_trials = find(cond_mask);
    end
    if ~isempty(cond_trials)
        erp_cond = mean(EEG.data(chan_idx, time_mask, cond_trials), 3);
        result.erp.(cond_field).mean_amplitude = mean(erp_cond, 2);
        result.erp.(cond_field).num_trials = length(cond_trials);
"""
        if peak_detection and time_window:
            cond_code += f"""
        for i = 1:length(chan_idx)
            chan_label = EEG.chanlocs(chan_idx(i)).labels;
            chan_field = matlab.lang.makeValidName(char(chan_label));
            chan_erp = squeeze(erp_cond(i,:));
            [max_val, max_idx] = max(chan_erp);
            [min_val, min_idx] = min(chan_erp);
            peak_times = EEG.times(time_mask);
            result.erp.(cond_field).peaks.(chan_field).positive_peak_amplitude = max_val;
            result.erp.(cond_field).peaks.(chan_field).positive_peak_latency = peak_times(max_idx);
            result.erp.(cond_field).peaks.(chan_field).negative_peak_amplitude = min_val;
            result.erp.(cond_field).peaks.(chan_field).negative_peak_latency = peak_times(min_idx);
        end
"""
        cond_code += "    else\n        result.erp.(cond_field).mean_amplitude = [];\n        result.erp.(cond_field).num_trials = 0;\n    end\nend\n"
    else:
        cond_code = ""

    code = f"""
{_maybe_init()}
{chan_code}
{tw_code}
erp_data = mean(EEG.data(chan_idx, time_mask, :), 3);
result.channels = {{EEG.chanlocs(chan_idx).labels}};
result.time_window = {tw_vals};
result.mean_amplitude = mean(erp_data, 2);
{cond_code}
"""

    if peak_detection and time_window and not conditions:
        code += f"""
for i = 1:length(chan_idx)
    chan_label = EEG.chanlocs(chan_idx(i)).labels;
    chan_field = matlab.lang.makeValidName(char(chan_label));
    chan_erp = squeeze(erp_data(i,:));
    [max_val, max_idx] = max(chan_erp);
    [min_val, min_idx] = min(chan_erp);
    peak_times = EEG.times(time_mask);
    result.peaks.(chan_field).positive_peak_amplitude = max_val;
    result.peaks.(chan_field).positive_peak_latency = peak_times(max_idx);
    result.peaks.(chan_field).negative_peak_amplitude = min_val;
    result.peaks.(chan_field).negative_peak_latency = peak_times(min_idx);
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_sort_epochs(args: dict) -> list[TextContent]:
    """按条件排序试次。"""
    sort_by = args["sort_by"]
    sort_by_lit = matlab_string(sort_by)

    code = f"""
{_maybe_init()}
EEG = pop_sort(EEG, {sort_by_lit});
result.sorted_by = {sort_by_lit};
result.trials = EEG.trials;
if isfield(EEG, 'event') && ~isempty(EEG.event)
    event_types = unique({{EEG.event.type}});
    result.event_types = event_types;
    for i = 1:length(event_types)
        cnt = sum(strcmp({{EEG.event.type}}, event_types{{i}}));
        result.event_counts.(event_types{{i}}) = cnt;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_average_erp(args: dict) -> list[TextContent]:
    """ERP 平均。"""
    conditions = args.get("conditions", [])
    channels = args.get("channels", [])

    if channels:
        chan_str = _cell(channels)
        chan_code = f"chan_idx = strmatch({chan_str}, {{EEG.chanlocs.labels}});"
    else:
        chan_code = "chan_idx = 1:EEG.nbchan;"

    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"""
result.conditions = {cond_str};
for c = 1:length({cond_str})
    cond_name = {cond_str}{{c}};
    cond_mask = strcmp({{EEG.event.type}}, cond_name);
    cond_trials = find(cond_mask);
    if ~isempty(cond_trials)
        avg_erp = mean(EEG.data(chan_idx, :, cond_trials), 3);
        result.erp.(cond_name).mean_amplitude = squeeze(mean(avg_erp, 2));
        result.erp.(cond_name).num_trials = length(cond_trials);
    else
        result.erp.(cond_name).mean_amplitude = [];
        result.erp.(cond_name).num_trials = 0;
    end
end
"""
    else:
        cond_code = """
avg_erp = mean(EEG.data(chan_idx, :, :), 3);
result.mean_amplitude = squeeze(mean(avg_erp, 2));
result.num_trials = EEG.trials;
"""

    code = f"""
{_maybe_init()}
{chan_code}
result.channels = {{EEG.chanlocs(chan_idx).labels}};
{cond_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
