"""Preprocessing handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json

from mcp.types import TextContent

try:
    from .runtime import (
        cfg,
        matlab,
        matlab_string,
        _arr,
        _cell,
        _error_response,
        _maybe_init,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import (
        cfg,
        matlab,
        matlab_string,
        _arr,
        _cell,
        _error_response,
        _maybe_init,
    )


async def _eeglab_filter(args: dict) -> list[TextContent]:
    """Filter the data."""
    filter_type = args["filter_type"]
    low_cutoff = args.get("low_cutoff")
    high_cutoff = args.get("high_cutoff")
    notch_freq = args.get("notch_freq")
    notch_harmonics = args.get("notch_harmonics", True)

    if filter_type == "notch":
        if not notch_freq:
            return _error_response(
                "missing_required_argument",
                "notch filtering requires the notch_freq parameter",
                next_step="pass notch_freq, for example 50 or 60, when calling eeglab_filter.",
                details={"missing": ["notch_freq"]},
            )
        freqs = [notch_freq]
        if notch_harmonics:
            for h in range(2, 5):
                hf = notch_freq * h
                if hf < cfg.MATLAB_TIMEOUT:  # reasonable upper bound
                    freqs.append(hf)
        freqs_str = _arr(freqs)
        filter_code = f"""
EEG = pop_cleanline(EEG, 'linefreqs', {freqs_str}, 'bandwidth', 2, 'tau', 100, 'winsize', 4);
result.filter_type = 'notch';
result.notch_freqs = {freqs_str};
"""
    else:
        if filter_type == "bandpass" and (low_cutoff is None or high_cutoff is None):
            return _error_response(
                "missing_required_argument",
                "bandpass filtering requires both low_cutoff and high_cutoff",
                next_step="supply low_cutoff and high_cutoff, then retry.",
            )
        if filter_type == "highpass" and low_cutoff is None:
            return _error_response(
                "missing_required_argument",
                "highpass filtering requires low_cutoff",
                next_step="supply low_cutoff, then retry.",
            )
        if filter_type == "lowpass" and high_cutoff is None:
            return _error_response(
                "missing_required_argument",
                "lowpass filtering requires high_cutoff",
                next_step="supply high_cutoff, then retry.",
            )

        # pop_eegfiltnew in current EEGLAB/firfilt uses locutoff/hicutoff.
        lo = low_cutoff if low_cutoff else "[]"
        hi = high_cutoff if high_cutoff else "[]"
        filter_code = f"""
EEG = pop_eegfiltnew(EEG, 'locutoff', {lo}, 'hicutoff', {hi});
result.filter_type = '{filter_type}';
result.low_cutoff = {lo};
result.high_cutoff = {hi};
"""

    code = f"""
{_maybe_init()}
{filter_code}
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_resample(args: dict) -> list[TextContent]:
    """Resample the data."""
    new_srate = args["new_srate"]

    code = f"""
{_maybe_init()}
EEG = pop_resample(EEG, {new_srate});
result.new_srate = EEG.srate;
result.nbchan = EEG.nbchan;
result.pnts = EEG.pnts;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_reref(args: dict) -> list[TextContent]:
    """Re-reference the data."""
    ref_type = args["ref_type"]
    ref_channel = args.get("ref_channel", "")
    ref_channel_lit = matlab_string(ref_channel)

    if ref_type == "average":
        reref_code = """
EEG = pop_reref(EEG, []);
result.ref_type = 'average';
result.ref_description = "average reference over all channels (note: this reduces the data rank by 1, so set pca=nchan-1 for ICA)";
"""
    elif ref_type == "channel":
        if not ref_channel:
            return _error_response(
                "missing_required_argument",
                "single-channel reference requires the ref_channel parameter",
                next_step="pass ref_channel, for example Cz, when calling eeglab_reref.",
                details={"missing": ["ref_channel"]},
            )
        reref_code = f"""
EEG = pop_reref(EEG, {ref_channel_lit});
result.ref_type = 'channel';
result.ref_channel = {ref_channel_lit};
"""
    elif ref_type == "rest":
        reref_code = """
EEG = pop_reref(EEG, [], 'keepref', 'on');
result.ref_type = 'rest';
result.ref_description = "REST reference";
"""
    else:
        return _error_response(
            "invalid_arguments",
            f"unsupported reference type: {ref_type}",
            next_step="ref_type must be average, channel or rest.",
        )

    code = f"""
{_maybe_init()}
{reref_code}
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_select_channels(args: dict) -> list[TextContent]:
    """Select or exclude channels."""
    channels = args.get("channels", [])
    exclude_channels = args.get("exclude_channels", [])

    if channels:
        chan_str = _cell(channels)
        select_code = f"""
EEG = pop_select(EEG, 'channel', {chan_str});
result.action = 'select';
result.selected_channels = {chan_str};
"""
    elif exclude_channels:
        excl_str = _cell(exclude_channels)
        select_code = f"""
EEG = pop_select(EEG, 'nochannel', {excl_str});
result.action = 'exclude';
result.excluded_channels = {excl_str};
"""
    else:
        return _error_response(
            "missing_required_argument",
            "specify channels or exclude_channels",
            next_step="pass the channel list to keep or to exclude, then retry.",
        )

    code = f"""
{_maybe_init()}
{select_code}
result.nbchan = EEG.nbchan;
result.channel_labels = {{EEG.chanlocs.labels}};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_interpolate_channels(args: dict) -> list[TextContent]:
    """Interpolate channels."""
    ref_chanlocs = args.get("ref_chanlocs", "")
    method = args.get("method", "spherical")
    ref_chanlocs_lit = matlab_string(ref_chanlocs)
    method_lit = matlab_string(method)

    if ref_chanlocs == "urchanlocs":
        interp_code = f"""
EEG = pop_interp(EEG, EEG.urchanlocs, {method_lit});
result.action = 'interpolate_urchanlocs';
"""
    elif ref_chanlocs:
        interp_code = f"""
EEG = pop_interp(EEG, {ref_chanlocs_lit}, {method_lit});
result.action = 'interpolate_from_file';
result.ref_chanlocs = {ref_chanlocs_lit};
"""
    else:
        interp_code = f"""
EEG = pop_interp(EEG, [], {method_lit});
result.action = 'interpolate_current';
"""

    code = f"""
{_maybe_init()}
{interp_code}
result.method = {method_lit};
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_edit_channels(args: dict) -> list[TextContent]:
    """Edit channel information."""
    action = args["action"]

    if action == "load_loc":
        loc_file = args.get("loc_file", "")
        if not loc_file:
            return _error_response(
                "missing_required_argument",
                "the load_loc action requires the loc_file parameter",
                next_step="pass the path of a .loc/.ced channel location file, then retry.",
                details={"missing": ["loc_file"]},
            )
        loc_file_lit = matlab_string(loc_file)
        edit_code = f"""
EEG = pop_chanedit(EEG, 'load', {{{loc_file_lit}}});
result.action = 'load_loc';
result.loc_file = {loc_file_lit};
"""
    elif action == "rename":
        rename_map = args.get("rename_map", {})
        if not rename_map:
            return _error_response(
                "missing_required_argument",
                "the rename action requires the rename_map parameter",
                next_step="pass a mapping of old channel names to new channel names, then retry.",
                details={"missing": ["rename_map"]},
            )
        rename_cmds = ""
        for old_name, new_name in rename_map.items():
            rename_cmds += (
                f"EEG = pop_chanedit(EEG, 'changename', {{{matlab_string(old_name)}, {matlab_string(new_name)}}});\n"
            )
        edit_code = f"""
{rename_cmds}
result.action = 'rename';
result.rename_map = struct();
"""
        for old_name, new_name in rename_map.items():
            edit_code += f"result.rename_map.({matlab_string(old_name)}) = {matlab_string(new_name)};\n"
    else:
        return _error_response(
            "invalid_arguments",
            f"unsupported action: {action}",
            next_step="action must be load_loc or rename.",
        )

    code = f"""
{_maybe_init()}
{edit_code}
result.nbchan = EEG.nbchan;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_clean_line_noise(args: dict) -> list[TextContent]:
    """Remove line noise with the dedicated tool."""
    line_freq = args.get("line_freq", 50)
    bandwidth = args.get("bandwidth", 2)
    tau = args.get("tau", 100)
    winsize = args.get("winsize", 4)

    code = f"""
{_maybe_init()}
EEG = pop_cleanline(EEG, 'linefreqs', [{line_freq}], 'bandwidth', {bandwidth}, 'tau', {tau}, 'winsize', {winsize});
result.line_freq = {line_freq};
result.bandwidth = {bandwidth};
result.tau = {tau};
result.winsize = {winsize};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_clean_rawdata(args: dict) -> list[TextContent]:
    """Remove artifacts with ASR."""
    flatline = args.get("flatline_criterion", 5)
    channel_crit = args.get("channel_criterion", 0.8)
    line_noise_crit = args.get("line_noise_criterion", 4)
    burst_crit = args.get("burst_criterion", 20)
    window_crit = args.get("window_criterion", 0.25)

    code = f"""
{_maybe_init()}
EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion', {flatline}, 'ChannelCriterion', {channel_crit}, 'LineNoiseCriterion', {line_noise_crit}, 'Highpass', [0.25 0.75], 'BurstCriterion', {burst_crit}, 'BurstRejection', 'on', 'WindowCriterion', {window_crit}, 'Distance', 'Euclidian', 'WindowCriterionTolerances', [-Inf 7]);
result.flatline_criterion = {flatline};
result.channel_criterion = {channel_crit};
result.line_noise_criterion = {line_noise_crit};
result.burst_criterion = {burst_crit};
result.window_criterion = {window_crit};
result.nbchan = EEG.nbchan;
result.srate = EEG.srate;
result.pnts = EEG.pnts;
result.trials = EEG.trials;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
