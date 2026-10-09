function eegmcp_connectivity(options)
%EEGMCP_CONNECTIVITY Sensor-level coherence or phase locking value between channels (MCP tool eeglab_connectivity).
%   coherence: magnitude-squared coherence from Hann-tapered FFT segments
%   (the epochs, or 2 s non-overlapping windows of continuous data),
%   averaged over the frequency bins inside freq_range.
%   plv: phase locking value of the band-limited analytic signal
%   (FFT band-pass inside freq_range), pooled over samples and epochs.
%   Returns the channel-by-channel matrix and its off-diagonal summary.
%   Read-only.

try
    opts = eegmcp_options(options);
    [freq_range, message] = eegmcp_b3_pair(opts, 'freq_range', [8 13], false);
    if isempty(message) && freq_range(1) < 0
        message = 'freq_range must not be negative';
    end
    method = eegmcp_text(eegmcp_opt(opts, 'method', 'coherence'));
    if isempty(message) && ~any(strcmp(method, {'coherence', 'plv'}))
        message = 'method must be one of coherence, plv';
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
    if isfield(opts, 'method') && ~isempty(opts.method)
        derived.method = method;
        derived.connectivity_limits_recorded = true;
    end
    [gate, blocked] = eegmcp_gate('eeglab_connectivity', opts, derived);
    if blocked
        return
    end

    [chans, missing] = eegmcp_b3_channels(dataset, eegmcp_opt(opts, 'channels', {}));
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end
    if numel(chans) < 2
        eegmcp_fail('invalid_arguments', 'Connectivity needs at least 2 channels.', ...
            'Pass two or more channels, or leave channels empty for all channels.');
        return
    end
    if freq_range(1) >= dataset.srate / 2
        eegmcp_fail('invalid_arguments', sprintf(['freq_range starts at or above the Nyquist ' ...
            'frequency (%g Hz).'], dataset.srate / 2), 'Lower freq_range, then retry.');
        return
    end

    segments = make_segments(dataset, chans);
    seg_len = size(segments, 2);
    freqs = (0:seg_len - 1) * dataset.srate / seg_len;
    band = freqs >= freq_range(1) & freqs <= freq_range(2) & freqs <= dataset.srate / 2;
    if ~any(band)
        eegmcp_fail('invalid_arguments', sprintf(['freq_range contains no frequency bin ' ...
            '(resolution %g Hz).'], dataset.srate / seg_len), 'Widen freq_range, then retry.');
        return
    end

    if strcmp(method, 'coherence')
        matrix = coherence_matrix(segments, band);
    else
        matrix = plv_matrix(segments, band);
    end

    nchan = numel(chans);
    pairs = triu(true(nchan), 1);
    values = matrix(pairs);
    result.status = 'success';
    result.method = method;
    result.freq_range = freq_range;
    result.analysed_freq_range = [min(freqs(band)), max(freqs(band))];
    result.freq_resolution = sum(band);
    result.freq_resolution_hz = dataset.srate / seg_len;
    result.n_segments = size(segments, 3);
    result.segment_length_s = seg_len / dataset.srate;
    result.channels = eegmcp_b3_labels(dataset, chans);
    result.n_pairs = numel(values);
    result.mean_connectivity = mean(values);
    result.max_connectivity = max(values);
    result.min_connectivity = min(values);
    [~, strongest] = max(values);
    [row, col] = find(pairs);
    result.strongest_pair = struct('channels', {result.channels([row(strongest), col(strongest)])}, ...
        'value', values(strongest));
    result.connectivity_matrix = num2cell(matrix, 2)';
    result.limitations = {['Sensor-level connectivity is inflated by volume conduction and a ' ...
        'common reference; it does not show causal or source-level interactions.']};
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('connectivity_failed', err.message, 'Check the channels and freq_range, then retry.');
end
end

function segments = make_segments(dataset, chans)
% Channels x samples x segments, each segment demeaned.
data = double(dataset.data(chans, :, :));
if dataset.trials > 1
    segments = data;
else
    seg_len = min(2 * round(dataset.srate), dataset.pnts);
    nseg = floor(dataset.pnts / seg_len);
    segments = reshape(data(:, 1:nseg * seg_len), numel(chans), seg_len, nseg);
end
segments = segments - mean(segments, 2);
segments(isnan(segments)) = 0;
end

function matrix = coherence_matrix(segments, band)
[nchan, seg_len, nseg] = size(segments);
taper = reshape(0.5 - 0.5 * cos(2 * pi * (0:seg_len - 1) / max(1, seg_len - 1)), 1, seg_len);
spectra = fft(segments .* taper, [], 2);
spectra = spectra(:, band, :);           % channels x band bins x segments
nbins = size(spectra, 2);
matrix = zeros(nchan);
for f = 1:nbins
    x = reshape(spectra(:, f, :), nchan, nseg);
    cross = x * x';                       % summed cross-spectra over segments
    auto = real(diag(cross));
    matrix = matrix + abs(cross) .^ 2 ./ max(auto * auto', eps);
end
matrix = matrix / nbins;
matrix(1:nchan + 1:end) = 1;
end

function matrix = plv_matrix(segments, band)
[nchan, seg_len, nseg] = size(segments);
spectra = fft(segments, [], 2);
gain = zeros(1, seg_len);
positive = band & (1:seg_len) > 1 & (1:seg_len) <= floor(seg_len / 2) + 1;
gain(positive) = 2;
analytic = ifft(spectra .* gain, [], 2);
phase = analytic ./ max(abs(analytic), eps);
phase = reshape(phase, nchan, seg_len * nseg);
matrix = abs(phase * phase') / (seg_len * nseg);
matrix(1:nchan + 1:end) = 1;
end
