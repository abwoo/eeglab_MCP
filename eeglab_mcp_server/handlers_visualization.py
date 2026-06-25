"""Visualization handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json
import os

from mcp.types import TextContent

try:
    from .runtime import matlab, matlab_string, _arr, _cell, _maybe_init
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, matlab_string, _arr, _cell, _maybe_init


async def _eeglab_topoplot(args: dict) -> list[TextContent]:
    """绘制头皮地形图。"""
    output_path = args["output_path"]
    time_point = args.get("time_point")
    time_window = args.get("time_window")
    channels = args.get("channels", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chaninfo', {chan_str}, "
    else:
        chan_code = ""

    if time_point is not None:
        time_code = f"'time', {time_point}, "
    elif time_window and len(time_window) == 2:
        time_code = f"'time', [{time_window[0]}, {time_window[1]}], "
    else:
        time_code = ""

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_topoplot(EEG, {time_code}{chan_code}{title_code}'style', 'straight', 'electrodes', 'on');
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_erp(args: dict) -> list[TextContent]:
    """绘制 ERP 波形图。"""
    channels = args["channels"]
    output_path = args["output_path"]
    conditions = args.get("conditions", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    chan_str = _cell(channels)

    if conditions:
        cond_str = _cell(conditions)
        cond_code = f"'conditions', {cond_str}, "
    else:
        cond_code = ""

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
if exist('pop_ploterp', 'file')
    figure('Visible', 'off');
    pop_ploterp(EEG, 'channels', {chan_str}, {cond_code}{title_code}'overlay', 'on');
    saveas(gcf, {output_path_lit});
    close(gcf);
    result.method = 'pop_ploterp';
else
    error('pop_ploterp function is not available. Please update EEGLAB to the latest version or use eeglab_erp_analysis to get numerical results.');
end
result.output_path = {output_path_lit};
result.channels = {chan_str};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_timefreq(args: dict) -> list[TextContent]:
    """绘制时频图。"""
    channel = args["channel"]
    output_path = args["output_path"]
    plot_ersp = args.get("plot_ersp", True)
    plot_itc = args.get("plot_itc", True)
    title = args.get("title", "")
    freq_range = args.get("freq_range", [3, 80])
    cycles = args.get("cycles", [3, 10])
    baseline = args.get("baseline", [-200, 0])
    channel_lit = matlab_string(channel)
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    title_code = f"'title', {matlab_string(title)}, " if title else ""
    cycles_str = _arr(cycles)

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_newtimef(EEG, 1, {channel_lit}, [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
    'freqs', [{freq_range[0]}, {freq_range[1]}], 'cycles', {cycles_str}, ...
    'baseline', [{baseline[0]}, {baseline[1]}], ...
    'plotersp', '{"on" if plot_ersp else "off"}', ...
    'plotitc', '{"on" if plot_itc else "off"}', ...
    {title_code}'pad', 0);
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
result.channel = {channel_lit};
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.cycles = {cycles_str};
result.baseline = [{baseline[0]}, {baseline[1]}];
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_components(args: dict) -> list[TextContent]:
    """绘制 ICA 成分图。"""
    output_path = args["output_path"]
    component_indices = args.get("component_indices", [])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if component_indices:
        comp_str = _arr(component_indices)
    else:
        comp_str = "1:min(10, size(EEG.icaweights, 1))"

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    figure('Visible', 'off');
    pop_topoplot(EEG, 'components', {comp_str}, {title_code}'plotrad', 0.7);
    saveas(gcf, {output_path_lit});
    close(gcf);
    result.output_path = {output_path_lit};
    result.components = {comp_str};
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_psd(args: dict) -> list[TextContent]:
    """绘制功率谱密度(PSD)图。"""
    output_path = args["output_path"]
    channels = args.get("channels", [])
    freq_range = args.get("freq_range", [0.5, 100])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_spectopo(EEG, 1, {chan_code}'freqrange', [{freq_range[0]}, {freq_range[1]}], {title_code}'title', 'Power Spectral Density');
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
if exist('channels', 'var') && ~isempty(channels)
    result.channels = {chan_str if channels else '[]'};
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_plot_connectivity(args: dict) -> list[TextContent]:
    """绘制连接性矩阵图。"""
    output_path = args["output_path"]
    channels = args.get("channels", [])
    method = args.get("method", "coherence")
    freq_range = args.get("freq_range", [8, 13])
    title = args.get("title", "")
    output_path_lit = matlab_string(output_path)
    method_lit = matlab_string(method)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if channels:
        chan_str = _cell(channels)
    else:
        chan_str = "{'1', '2'}"

    code = f"""
{_maybe_init()}
% Compute connectivity matrix using FFT-based coherence
nchans = EEG.nbchan;
conn_matrix = zeros(nchans, nchans);

% Get channel indices
chan_labels = {{{chan_str}}};
chan_indices = zeros(1, length(chan_labels));
for c = 1:length(chan_labels)
    found = false;
    for ch = 1:nchans
        if isfield(EEG.chanlocs, 'labels') && strcmpi(EEG.chanlocs(ch).labels, chan_labels{{c}})
            chan_indices(c) = ch;
            found = true;
            break;
        end
    end
    if ~found
        chan_indices(c) = str2double(chan_labels{{c}});
    end
end

% Compute connectivity for each pair
for i = 1:length(chan_indices)
    for j = i+1:length(chan_indices)
        num1 = chan_indices(i);
        num2 = chan_indices(j);
        if num1 > 0 && num2 > 0 && num1 <= nchans && num2 <= nchans
            data1 = EEG.data(num1, :);
            data2 = EEG.data(num2, :);
            [Pxx, f] = pwelch(data1, [], [], [], EEG.srate);
            [Pyy, ~] = pwelch(data2, [], [], [], EEG.srate);
            [Pxy, ~] = cpsd(data1, data2, [], [], [], EEG.srate);
            fmask = f >= {freq_range[0]} & f <= {freq_range[1]};
            if strcmp({method_lit}, 'coher')
                coh_val = abs(mean(Pxy(fmask) ./ sqrt(Pxx(fmask) .* Pyy(fmask))));
            else
                % PLV approximation
                coh_val = abs(mean(exp(1i * angle(Pxy(fmask)))));
            end
            conn_matrix(num1, num2) = coh_val;
            conn_matrix(num2, num1) = coh_val;
        end
    end
end

% Plot connectivity matrix
figure('Visible', 'off');
imagesc(conn_matrix);
colorbar;
colormap('jet');
xlabel('Channel');
ylabel('Channel');
if length(chan_indices) <= 20
    set(gca, 'XTick', chan_indices, 'XTickLabel', chan_labels);
    set(gca, 'YTick', chan_indices, 'YTickLabel', chan_labels);
end
title({matlab_string(f'{method} Connectivity ({freq_range[0]}-{freq_range[1]} Hz)')});
saveas(gcf, {output_path_lit});
close(gcf);

result.output_path = {output_path_lit};
result.method = {method_lit};
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.mean_connectivity = mean(conn_matrix(conn_matrix ~= 0));
result.max_connectivity = max(conn_matrix(:));
result.connectivity_matrix = conn_matrix;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
