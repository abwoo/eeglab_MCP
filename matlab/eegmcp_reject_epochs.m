function eegmcp_reject_epochs(options)
%EEGMCP_REJECT_EPOCHS Reject artifact trials of epoched data (MCP tool eeglab_reject_epochs).
%   Options (JSON object): method ("threshold"|"joint_probability",
%   default "threshold"), threshold ([low, high] microvolts, default
%   [-100, 100]), channels (list of labels, default all), jp_threshold
%   (number of standard deviations, default 3), plus the gate options
%   method_context, override_gate and override_reason. Marks trials with
%   pop_eegthresh or pop_jointprob and removes them with pop_rejepoch.

try
    opts = eegmcp_options(options);
    method = eegmcp_opt(opts, 'method', 'threshold');
    threshold = eegmcp_opt(opts, 'threshold', [-100, 100]);
    channels = eegmcp_opt(opts, 'channels', {});
    jp_threshold = eegmcp_opt(opts, 'jp_threshold', 3);

    errors = {};
    if ~ischar(method) || ~any(strcmp(method, {'threshold', 'joint_probability'}))
        errors{end + 1} = 'method must be one of: threshold, joint_probability';
    end
    checked = struct();
    checked.threshold = threshold;
    errors = eegmcp_b2_pair_errors(checked, 'threshold', errors);
    if ~(isnumeric(jp_threshold) && isscalar(jp_threshold) && isreal(jp_threshold) && ...
            isfinite(jp_threshold) && jp_threshold > 0)
        errors{end + 1} = 'jp_threshold must be a finite number greater than 0';
    end
    if ~(iscell(channels) || ischar(channels) || isstring(channels))
        errors{end + 1} = 'channels must be a list of channel labels';
    end
    errors = eegmcp_b2_override_errors(opts, errors);
    if eegmcp_b2_invalid('eeglab_reject_epochs', errors)
        return
    end
    threshold = double(threshold(:)');

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct('parameters_recorded', true);
    derived = eegmcp_b2_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_reject_epochs', opts, derived);
    if blocked
        return
    end

    if dataset.trials <= 1
        eegmcp_fail('not_epoched', 'Trial rejection needs epoched data.', 'Call eeglab_epoch first.');
        return
    end
    [chan_idx, unknown] = eegmcp_b2_channels(dataset, channels);
    if ~isempty(unknown)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(unknown, ', ')], ...
            'Use channel labels from eeglab_info.');
        return
    end

    trials_before = dataset.trials;
    result.status = 'success';
    result.method = method;
    if strcmp(method, 'threshold')
        % Mark only (reject = 0), then remove the marked trials below.
        evalc(['[~, rejected] = pop_eegthresh(dataset, 1, chan_idx, threshold(1), threshold(2), ' ...
            'dataset.xmin, dataset.xmax, 0, 0);']);
        result.threshold = threshold;
    else
        % Clear cached statistics so pop_jointprob recomputes them for these trials.
        marked = dataset;
        marked.stats.jp = [];
        marked.stats.jpE = [];
        evalc('marked = pop_jointprob(marked, 1, chan_idx, jp_threshold, jp_threshold, 0, 0, 0, [], 0);');
        rejected = find(marked.reject.rejjp);
        result.jp_threshold = jp_threshold;
    end
    rejected = unique(double(rejected(:)'));

    if numel(rejected) >= trials_before
        eegmcp_fail('all_trials_rejected', sprintf('All %d trials exceed the rejection criterion.', ...
            trials_before), 'Loosen the threshold or check the data scaling; the dataset was not changed.');
        return
    end
    if ~isempty(rejected)
        evalc('dataset = pop_rejepoch(dataset, rejected, 0);');
    end
    evalc('eegmcp_commit(dataset);');

    if isempty(dataset.chanlocs)
        result.channels = eegmcp_b2_list(chan_idx);
    else
        result.channels = {dataset.chanlocs(chan_idx).labels};
    end
    result.trials_before = trials_before;
    result.rejected_trials = eegmcp_b2_list(rejected);
    result.num_rejected = numel(rejected);
    result.remaining_trials = dataset.trials;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('reject_epochs_failed', err.message, ...
        'Check that the data are epoched and the channels and thresholds are valid.');
end
end
