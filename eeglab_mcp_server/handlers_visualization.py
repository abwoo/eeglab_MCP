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
figure('Visible', 'off');
pop_ploterp(EEG, 'channels', {chan_str}, {cond_code}{title_code}'overlay', 'on');
saveas(gcf, {output_path_lit});
close(gcf);
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
    channel_lit = matlab_string(channel)
    output_path_lit = matlab_string(output_path)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    title_code = f"'title', {matlab_string(title)}, " if title else ""

    code = f"""
{_maybe_init()}
figure('Visible', 'off');
pop_newtimef(EEG, 1, {channel_lit}, [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
    'freqs', [3 80], 'cycles', [3 10], ...
    'plotersp', '{"on" if plot_ersp else "off"}', ...
    'plotitc', '{"on" if plot_itc else "off"}', ...
    {title_code}'pad', 0);
saveas(gcf, {output_path_lit});
close(gcf);
result.output_path = {output_path_lit};
result.channel = {channel_lit};
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
    pop_topoplot(EEG, {title_code}'components', {comp_str});
    saveas(gcf, {output_path_lit});
    close(gcf);
    result.output_path = {output_path_lit};
    result.components = {comp_str};
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
