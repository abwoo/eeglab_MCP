function eegmcp_timefreq(options)
%EEGMCP_TIMEFREQ ERSP and ITC of epoched data (MCP tool eeglab_timefreq).
%   Runs newtimef (Morlet wavelets, plotting off) on each selected channel
%   of the current epoched dataset and summarizes the event-related
%   spectral perturbation (dB, baseline-corrected) and the inter-trial
%   coherence per frequency band, averaged over channels. Read-only.

try
    opts = eegmcp_options(options);
    [freq_range, message] = eegmcp_b3_pair(opts, 'freq_range', [3 80], false);
    if isempty(message) && freq_range(1) <= 0
        message = 'freq_range must start above 0 Hz for wavelets';
    end
    if isempty(message)
        [baseline, message] = eegmcp_b3_pair(opts, 'baseline', [-200 0], true);
    end
    cycles = eegmcp_opt(opts, 'cycles', [3 10]);
    if isempty(message)
        if ~isnumeric(cycles) || ~any(numel(cycles) == [2 3]) || ~all(isfinite(cycles(:))) || cycles(1) <= 0
            message = 'cycles must be a list of 2 or 3 positive numbers';
        else
            cycles = double(cycles(:)');
        end
    end
    output_type = eegmcp_text(eegmcp_opt(opts, 'output_type', 'both'));
    if isempty(message) && ~any(strcmp(output_type, {'ersp', 'itc', 'both'}))
        message = 'output_type must be one of ersp, itc, both';
    end
    if ~isempty(message)
        eegmcp_fail('invalid_arguments', message, 'Adjust the options, then retry.');
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct();
    if isfield(opts, 'baseline') && ~isempty(opts.baseline)
        derived.baseline = baseline;
    end
    has_freq = isfield(opts, 'freq_range') && ~isempty(opts.freq_range);
    has_cycles = isfield(opts, 'cycles') && ~isempty(opts.cycles);
    if has_freq || has_cycles
        derived.freq_range = [];
        derived.cycles = [];
        if has_freq
            derived.freq_range = freq_range;
        end
        if has_cycles
            derived.cycles = cycles;
        end
    end
    [gate, blocked] = eegmcp_gate('eeglab_timefreq', opts, derived);
    if blocked
        return
    end

    if dataset.trials < 2
        eegmcp_fail('not_epoched', 'Time-frequency analysis needs epoched data.', ...
            'Call eeglab_epoch first.');
        return
    end
    if baseline(1) < dataset.xmin * 1000 || baseline(2) > dataset.xmax * 1000
        eegmcp_fail('invalid_analysis_window', sprintf(['baseline [%g %g] ms must fall inside the ' ...
            'epoch [%g %g] ms.'], baseline, [dataset.xmin dataset.xmax] * 1000), ...
            'Adjust baseline, then retry.');
        return
    end
    if freq_range(1) >= dataset.srate / 2
        eegmcp_fail('invalid_arguments', sprintf(['freq_range starts at or above the Nyquist ' ...
            'frequency (%g Hz).'], dataset.srate / 2), 'Lower freq_range, then retry.');
        return
    end
    [chans, missing] = eegmcp_b3_channels(dataset, eegmcp_opt(opts, 'channels', {}));
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end

    ersp_all = [];
    itc_all = [];
    for k = 1:numel(chans)
        [ersp, itc, times, freqs, used_freqs] = eegmcp_b3_newtimef(dataset, chans(k), freq_range, ...
            cycles, baseline);
        if k == 1
            ersp_all = zeros([size(ersp), numel(chans)]);
            itc_all = zeros([size(itc), numel(chans)]);
        end
        ersp_all(:, :, k) = ersp;
        itc_all(:, :, k) = itc;
    end
    ersp_mean = mean(ersp_all, 3);
    itc_mean = mean(itc_all, 3);
    want_ersp = any(strcmp(output_type, {'ersp', 'both'}));
    want_itc = any(strcmp(output_type, {'itc', 'both'}));

    result.status = 'success';
    result.method = 'wavelet';
    result.channels = eegmcp_b3_labels(dataset, chans);
    result.n_trials = dataset.trials;
    result.freq_range = freq_range;
    result.analysed_freq_range = [min(freqs), max(freqs)];
    result.freq_resolution = numel(freqs);
    result.time_points = numel(times);
    result.time_range_ms = [min(times), max(times)];
    result.baseline = baseline;
    result.cycles = cycles;
    result.output_type = output_type;
    warnings = {};
    if used_freqs(2) < freq_range(2)
        warnings{end + 1} = sprintf('The upper frequency was clipped to the Nyquist frequency (%g Hz).', ...
            used_freqs(2));
    end
    if numel(cycles) == 3
        warnings{end + 1} = 'newtimef takes [start end] cycles; the middle (step) value was not used.';
    end

    names = {'delta', 'theta', 'alpha', 'beta', 'gamma'};
    ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
    bands = struct();
    for b = 1:numel(names)
        mask = freqs >= ranges(b, 1) & freqs <= ranges(b, 2);
        if any(mask)
            entry = struct('freq_range', ranges(b, :));
            if want_ersp
                band_ersp = mean(ersp_mean(mask, :), 1);
                entry.mean_ersp = mean(band_ersp);
                entry.max_ersp = max(band_ersp);
                entry.min_ersp = min(band_ersp);
            end
            if want_itc
                band_itc = mean(itc_mean(mask, :), 1);
                entry.mean_itc = mean(band_itc);
                entry.max_itc = max(band_itc);
            end
            bands.(names{b}) = entry;
        end
    end
    result.band_ersp = bands;
    if want_ersp
        result.ersp_units = 'dB relative to baseline';
        [~, where] = max(abs(ersp_mean(:)));
        [fi, ti] = ind2sub(size(ersp_mean), where);
        result.peak_abs_ersp = struct('value_db', ersp_mean(fi, ti), ...
            'freq_hz', freqs(fi), 'time_ms', times(ti));
    end
    if want_itc
        [peak, where] = max(itc_mean(:));
        [fi, ti] = ind2sub(size(itc_mean), where);
        result.peak_itc = struct('value', peak, 'freq_hz', freqs(fi), 'time_ms', times(ti));
    end
    result.warnings = warnings;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('timefreq_failed', err.message, ['Check that the epochs are long enough for the ' ...
        'lowest frequency and its cycles (cycles / freq seconds), then retry.']);
end
end
