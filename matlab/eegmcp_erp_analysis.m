function eegmcp_erp_analysis(options)
%EEGMCP_ERP_ANALYSIS Summarize ERP amplitudes and peaks (MCP tool eeglab_erp_analysis).
%   Options (JSON object): channels (list of labels, default all),
%   time_window ([start, end] ms, default the whole epoch), peak_detection
%   (boolean, default true; peaks are reported when time_window is set),
%   conditions (list of event types; trials are grouped by their
%   time-locking event). Read-only: the dataset is not changed.

try
    opts = eegmcp_options(options);
    channels = eegmcp_opt(opts, 'channels', {});
    time_window = eegmcp_opt(opts, 'time_window', []);
    peak_detection = eegmcp_opt(opts, 'peak_detection', true);
    conditions = eegmcp_cellstr(eegmcp_opt(opts, 'conditions', {}));

    errors = {};
    errors = eegmcp_b2_pair_errors(opts, 'time_window', errors);
    if ~(islogical(peak_detection) && isscalar(peak_detection))
        errors{end + 1} = 'peak_detection must be boolean';
    end
    if ~(iscell(channels) || ischar(channels) || isstring(channels))
        errors{end + 1} = 'channels must be a list of channel labels';
    end
    if eegmcp_b2_invalid('eeglab_erp_analysis', errors)
        return
    end
    time_window = double(time_window(:)');
    if ~isempty(time_window) && eegmcp_b2_window_failed('eeglab_erp_analysis', ...
            eegmcp_window_errors([], [], time_window))
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end
    [chan_idx, unknown] = eegmcp_b2_channels(dataset, channels);
    if ~isempty(unknown)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(unknown, ', ')], ...
            'Use channel labels from eeglab_info.');
        return
    end
    if ~isempty(conditions) && dataset.trials <= 1
        eegmcp_fail('not_epoched', 'Grouping by condition needs epoched data.', 'Call eeglab_epoch first.');
        return
    end

    if isempty(time_window)
        time_mask = true(size(dataset.times));
        result_window = [dataset.xmin, dataset.xmax] * 1000;
    else
        time_mask = dataset.times >= time_window(1) & dataset.times <= time_window(2);
        result_window = time_window;
    end
    if ~any(time_mask)
        eegmcp_fail('invalid_analysis_window', 'No samples fall inside time_window.', ...
            sprintf('Use a time_window inside [%g, %g] ms.', dataset.xmin * 1000, dataset.xmax * 1000));
        return
    end
    peak_times = dataset.times(time_mask);
    want_peaks = peak_detection && ~isempty(time_window);
    labels = channel_labels(dataset, chan_idx);

    erp_data = mean(double(dataset.data(chan_idx, time_mask, :)), 3);
    result.status = 'success';
    result.channels = labels;
    result.time_window = result_window;
    result.num_trials = dataset.trials;
    result.mean_amplitude = eegmcp_b2_list(mean(erp_data, 2));

    if ~isempty(conditions)
        result.conditions = conditions;
        result.erp = struct();
        for c = 1:numel(conditions)
            field = matlab.lang.makeValidName(conditions{c});
            trials = eegmcp_b2_condition_trials(dataset, conditions{c});
            entry = struct();
            entry.condition = conditions{c};
            entry.num_trials = numel(trials);
            if isempty(trials)
                entry.mean_amplitude = {};
            else
                erp_cond = mean(double(dataset.data(chan_idx, time_mask, trials)), 3);
                entry.mean_amplitude = eegmcp_b2_list(mean(erp_cond, 2));
                if want_peaks
                    entry.peaks = peaks_of(erp_cond, labels, peak_times);
                end
            end
            result.erp.(field) = entry;
        end
    elseif want_peaks
        result.peaks = peaks_of(erp_data, labels, peak_times);
    end
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('erp_analysis_failed', err.message, 'Check that the data are epoched and the channels exist.');
end
end

function labels = channel_labels(dataset, chan_idx)
if isempty(dataset.chanlocs) || ~isfield(dataset.chanlocs, 'labels')
    labels = arrayfun(@(k) sprintf('E%d', k), chan_idx, 'UniformOutput', false);
else
    labels = {dataset.chanlocs(chan_idx).labels};
end
end

function peaks = peaks_of(erp, labels, peak_times)
% Largest positive and negative value of each channel's average, with latency in ms.
peaks = struct();
for i = 1:numel(labels)
    [max_val, max_idx] = max(erp(i, :));
    [min_val, min_idx] = min(erp(i, :));
    entry = struct();
    entry.positive_peak_amplitude = max_val;
    entry.positive_peak_latency = peak_times(max_idx);
    entry.negative_peak_amplitude = min_val;
    entry.negative_peak_latency = peak_times(min_idx);
    peaks.(matlab.lang.makeValidName(labels{i})) = entry;
end
end
