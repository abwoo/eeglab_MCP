function eegmcp_spectral(options)
%EEGMCP_SPECTRAL Power spectral density and band power of the current dataset (MCP tool eeglab_spectral).
%   Computes the Welch power spectrum of each selected channel with
%   spectopo (1 s Hamming windows, plotting off; data discontinuities at
%   boundary events are respected) and, when band_power is true, the mean
%   absolute power (uV^2/Hz) and relative power (percent of the summed band
%   power) of the delta, theta, alpha, beta and gamma bands. Read-only.

try
    opts = eegmcp_options(options);
    [freq_range, message] = eegmcp_b3_pair(opts, 'freq_range', [0.5 100], false);
    if isempty(message) && freq_range(1) < 0
        message = 'freq_range must not be negative';
    end
    if isempty(message)
        [band_power, message] = eegmcp_b3_bool(opts, 'band_power', true);
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
    if isfield(opts, 'freq_range') && ~isempty(opts.freq_range)
        derived.freq_range = freq_range;
    end
    if isfield(opts, 'channels') && ~isempty(opts.channels)
        derived.channels = opts.channels;
    end
    if isfield(opts, 'band_power') && ~isempty(opts.band_power)
        derived.parameters_recorded = true;
    end
    [gate, blocked] = eegmcp_gate('eeglab_spectral', opts, derived);
    if blocked
        return
    end

    [chans, missing] = eegmcp_b3_channels(dataset, eegmcp_opt(opts, 'channels', {}));
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end
    nyquist = dataset.srate / 2;
    if freq_range(1) >= nyquist
        eegmcp_fail('invalid_arguments', sprintf(['freq_range starts at or above the Nyquist ' ...
            'frequency (%g Hz).'], nyquist), 'Lower freq_range, then retry.');
        return
    end

    data = double(dataset.data(chans, :, :));
    spec_args = {'plot', 'off', 'verbose', 'off'};
    if dataset.trials == 1 && isfield(dataset, 'event') && ~isempty(dataset.event) && ...
            isfield(dataset.event, 'type')
        bounds = eeg_findboundaries(dataset.event);
        if ~isempty(bounds)
            bounds = round([0, [dataset.event(bounds).latency] - 0.5, dataset.pnts]);
            spec_args = [spec_args, {'boundaries', bounds}];
        end
    end
    spectra = [];
    freqs = [];
    evalc('[spectra, freqs] = spectopo(data, dataset.pnts, dataset.srate, spec_args{:});');
    freqs = freqs(:)';
    power = 10 .^ (spectra / 10);   % dB -> uV^2/Hz, channels x frequencies

    in_range = freqs >= freq_range(1) & freqs <= freq_range(2);
    if ~any(in_range)
        eegmcp_fail('invalid_arguments', sprintf(['freq_range contains no spectral frequency ' ...
            '(resolution %g Hz).'], freqs(2) - freqs(1)), 'Widen freq_range, then retry.');
        return
    end
    warnings = {};
    if freq_range(2) > nyquist
        warnings{end + 1} = sprintf('freq_range above the Nyquist frequency (%g Hz) was ignored.', nyquist);
    end

    result.status = 'success';
    result.freq_range = freq_range;
    result.analysed_freq_range = [min(freqs(in_range)), max(freqs(in_range))];
    result.freq_resolution_hz = freqs(2) - freqs(1);
    result.n_freqs = sum(in_range);
    result.channels = eegmcp_b3_labels(dataset, chans);
    result.n_channels = numel(chans);
    result.data_shape = dataset_shape(dataset);
    result.method = 'spectopo (Welch, 1 s Hamming windows)';
    mean_power = mean(power(:, in_range), 1);
    [~, peak] = max(mean_power);
    in_freqs = freqs(in_range);
    result.peak_frequency_hz = in_freqs(peak);
    result.mean_spectrum_db = struct('freqs', in_freqs, 'power_db', 10 * log10(mean_power));

    if band_power
        names = {'delta', 'theta', 'alpha', 'beta', 'gamma'};
        ranges = [0.5 4; 4 8; 8 13; 13 30; 30 80];
        bands = struct();
        total = 0;
        for b = 1:numel(names)
            mask = in_range & freqs >= ranges(b, 1) & freqs <= ranges(b, 2);
            if any(mask)
                absolute = mean(mean(power(:, mask), 2));
                bands.(names{b}) = struct('freq_range', ranges(b, :), 'absolute_power', absolute, ...
                    'absolute_power_db', 10 * log10(absolute));
                total = total + absolute;
            end
        end
        present = fieldnames(bands);
        for b = 1:numel(present)
            bands.(present{b}).relative_power_percent = bands.(present{b}).absolute_power / total * 100;
        end
        result.band_power = bands;
        result.band_power_units = 'uV^2/Hz averaged over channels and band frequencies';
    end
    result.warnings = warnings;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('spectral_failed', err.message, 'Check the channels and freq_range, then retry.');
end
end

function shape = dataset_shape(dataset)
if dataset.trials > 1
    shape = 'epoched';
else
    shape = 'continuous';
end
end
