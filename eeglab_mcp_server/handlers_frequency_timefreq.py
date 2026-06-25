"""Frequency, time-frequency, and connectivity handlers."""

from __future__ import annotations

import json

from mcp.types import TextContent

try:
    from .runtime import matlab, matlab_string, _arr, _cell, _maybe_init
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, matlab_string, _arr, _cell, _maybe_init


async def _eeglab_spectral(args: dict) -> list[TextContent]:
    """频谱/功率谱密度分析。"""
    channels = args.get("channels", [])
    freq_range = args.get("freq_range", [0.5, 100])
    band_power = args.get("band_power", True)

    if channels:
        chan_str = _cell(channels)
        # Bug fix: pop_spectopo 正确签名
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    # Correct pop_spectopo signature: pop_spectopo(EEG, percent, freqrange, ...)
    code = f"""
{_maybe_init()}
[spectra, freqs] = pop_spectopo(EEG, 1, {chan_code}'freqrange', [{freq_range[0]}, {freq_range[1]}]);
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.num_freq_bins = length(freqs);
result.freq_resolution = freqs(2) - freqs(1);
"""

    if band_power:
        code += """
bands = struct();
band_names = {'delta', 'theta', 'alpha', 'beta', 'gamma'};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
total_power = 0;
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_pow = mean(spectra(fmask,:), 1);
        abs_pow = mean(band_pow);
        bands.(band_names{b}).absolute_power = abs_pow;
        bands.(band_names{b}).freq_range = band_ranges(b,:);
        total_power = total_power + abs_pow;
    end
end
for b = 1:length(band_names)
    if isfield(bands, band_names{b})
        bands.(band_names{b}).relative_power_percent = bands.(band_names{b}).absolute_power / total_power * 100;
    end
end
result.band_power = bands;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_timefreq(args: dict) -> list[TextContent]:
    """时频分析。"""
    channels = args.get("channels", [])
    freq_range = args.get("freq_range", [3, 80])
    cycles = args.get("cycles", [3, 10])
    baseline = args.get("baseline", [-200, 0])

    if channels:
        chan_str = _cell(channels)
        chan_code = f"'chanlist', {chan_str}, "
    else:
        chan_code = ""

    cycles_str = _arr(cycles)

    # Bug fix: pop_newtimef 正确调用
    code = f"""
{_maybe_init()}
[ERSP, ITC, times, freqs, specs] = pop_newtimef(EEG, 1, 1:EEG.nbchan, ...
    [EEG.xmin*1000 EEG.xmax*1000], ...
    [3 0.5], ...
    {chan_code}...
    'freqs', [{freq_range[0]}, {freq_range[1]}], ...
    'cycles', {cycles_str}, ...
    'baseline', [{baseline[0]}, {baseline[1]}]);
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.freq_resolution = length(freqs);
result.time_points = length(times);
result.method = 'wavelet';
result.baseline = [{baseline[0]}, {baseline[1]}];
result.cycles = {cycles_str};
bands = struct();
band_names = {{'delta', 'theta', 'alpha', 'beta', 'gamma'}};
band_ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
for b = 1:length(band_names)
    fmask = freqs >= band_ranges(b,1) & freqs <= band_ranges(b,2);
    if any(fmask)
        band_ersp = mean(ERSP(fmask,:), 1);
        bands.(band_names{{b}}).mean_ersp = mean(band_ersp);
        bands.(band_names{{b}}).max_ersp = max(band_ersp);
        bands.(band_names{{b}}).freq_range = band_ranges(b,:);
        if size(ITC, 1) == size(ERSP, 1)
            band_itc = mean(ITC(fmask,:), 1);
            bands.(band_names{{b}}).mean_itc = mean(band_itc);
        end
    end
end
result.band_ersp = bands;
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_connectivity(args: dict) -> list[TextContent]:
    """功能连接分析。"""
    channels = args.get("channels", [])
    method = args.get("method", "coherence")
    freq_range = args.get("freq_range", [8, 13])
    method_lit = matlab_string(method)

    if channels:
        chan_str = _cell(channels)
    else:
        # Default to first two channels if none specified
        chan_str = "{'1', '2'}"

    # Use pop_newcrossf for coherence between channel pairs
    # or compute connectivity matrix manually
    code = f"""
{_maybe_init()}
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

% Compute connectivity using pop_newcrossf for each pair
for i = 1:length(chan_indices)
    for j = i+1:length(chan_indices)
        num1 = chan_indices(i);
        num2 = chan_indices(j);
        if num1 > 0 && num2 > 0 && num1 <= nchans && num2 <= nchans
            try
                if strcmp({method_lit}, 'coher')
                    % Linear coherence
                    [ coh ] = pop_newcrossf(EEG, 1, num1, num2, ...
                        [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
                        'freqs', [{freq_range[0]}, {freq_range[1]}], ...
                        'type', 'coher', ...
                        'plotersp', 'off', 'plotphase', 'off', 'plotboot', 'off');
                else
                    % Phase coherence (PLV)
                    [ coh ] = pop_newcrossf(EEG, 1, num1, num2, ...
                        [EEG.xmin*1000 EEG.xmax*1000], [3 0.5], ...
                        'freqs', [{freq_range[0]}, {freq_range[1]}], ...
                        'type', 'phasecoher', ...
                        'plotersp', 'off', 'plotphase', 'off', 'plotboot', 'off');
                end
                % Average coherence across frequencies
                if ~isempty(coh)
                    conn_matrix(num1, num2) = mean(coh(:));
                    conn_matrix(num2, num1) = mean(coh(:));
                end
            catch ME
                % If pop_newcrossf fails, use manual FFT-based coherence
                data1 = EEG.data(num1, :);
                data2 = EEG.data(num2, :);
                [Pxx, f] = pwelch(data1, [], [], [], EEG.srate);
                [Pyy, ~] = pwelch(data2, [], [], [], EEG.srate);
                [Pxy, ~] = cpsd(data1, data2, [], [], [], EEG.srate);
                fmask = f >= {freq_range[0]} & f <= {freq_range[1]};
                coh_val = abs(mean(Pxy(fmask) ./ sqrt(Pxx(fmask) .* Pyy(fmask))));
                conn_matrix(num1, num2) = coh_val;
                conn_matrix(num2, num1) = coh_val;
            end
        end
    end
end

result.method = {method_lit};
result.freq_range = [{freq_range[0]}, {freq_range[1]}];
result.num_channels = nchans;
result.channel_labels = chan_labels;
if any(conn_matrix(:) ~= 0)
    result.mean_connectivity = mean(conn_matrix(conn_matrix ~= 0));
    result.max_connectivity = max(conn_matrix(:));
    result.min_connectivity = min(conn_matrix(conn_matrix ~= 0));
    result.connectivity_matrix = conn_matrix;
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
