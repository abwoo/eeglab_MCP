function eegmcp_average_erp(options)
%EEGMCP_AVERAGE_ERP Average ERP amplitudes by condition (MCP tool eeglab_average_erp).
%   Options (JSON object): conditions (list of event types; trials are
%   grouped by their time-locking event; default all trials together),
%   channels (list of labels, default all). Reports, per channel, the mean
%   over time of the trial-averaged ERP. Read-only: the dataset is not
%   changed.

try
    opts = eegmcp_options(options);
    channels = eegmcp_opt(opts, 'channels', {});
    conditions = eegmcp_opt(opts, 'conditions', {});
    errors = {};
    if ~(iscell(channels) || ischar(channels) || isstring(channels))
        errors{end + 1} = 'channels must be a list of channel labels';
    end
    if ~(iscell(conditions) || ischar(conditions) || isstring(conditions) || isnumeric(conditions))
        errors{end + 1} = 'conditions must be a list of event types';
    end
    if eegmcp_b2_invalid('eeglab_average_erp', errors)
        return
    end
    conditions = eegmcp_cellstr(conditions);

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

    result.status = 'success';
    if isempty(dataset.chanlocs) || ~isfield(dataset.chanlocs, 'labels')
        result.channels = arrayfun(@(k) sprintf('E%d', k), chan_idx, 'UniformOutput', false);
    else
        result.channels = {dataset.chanlocs(chan_idx).labels};
    end
    if isempty(conditions)
        avg_erp = mean(double(dataset.data(chan_idx, :, :)), 3);
        result.mean_amplitude = eegmcp_b2_list(mean(avg_erp, 2));
        result.num_trials = dataset.trials;
    else
        result.conditions = conditions;
        result.erp = struct();
        for c = 1:numel(conditions)
            trials = eegmcp_b2_condition_trials(dataset, conditions{c});
            entry = struct();
            entry.condition = conditions{c};
            entry.num_trials = numel(trials);
            if isempty(trials)
                entry.mean_amplitude = {};
            else
                avg_erp = mean(double(dataset.data(chan_idx, :, trials)), 3);
                entry.mean_amplitude = eegmcp_b2_list(mean(avg_erp, 2));
            end
            result.erp.(matlab.lang.makeValidName(conditions{c})) = entry;
        end
    end
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('average_erp_failed', err.message, 'Check that the data are epoched and the channels exist.');
end
end
