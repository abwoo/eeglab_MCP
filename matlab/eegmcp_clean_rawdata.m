function eegmcp_clean_rawdata(options)
%EEGMCP_CLEAN_RAWDATA Remove bad channels and artifacts with ASR (MCP tool eeglab_clean_rawdata).
%   Runs pop_clean_rawdata (clean_rawdata plugin) on continuous data:
%   drift highpass [0.25 0.75] Hz, flatline, channel-correlation and
%   line-noise channel rejection, ASR burst detection with burst rejection
%   on (bad bursts are removed, not repaired) and window rejection.
%   Removed channels are kept in EEG.chaninfo.removedchans for later
%   interpolation. High-risk tool: the clean_rawdata gate runs first.

try
    opts = eegmcp_options(options);
    keys = {'flatline_criterion', 'channel_criterion', 'line_noise_criterion', ...
        'burst_criterion', 'window_criterion'};
    errors = eegmcp_b1_check(opts, [keys', repmat({'positive'}, numel(keys), 1)]);
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_clean_rawdata', errors);
        return
    end
    flatline = double(eegmcp_opt(opts, 'flatline_criterion', 5));
    channel_crit = double(eegmcp_opt(opts, 'channel_criterion', 0.8));
    line_noise_crit = double(eegmcp_opt(opts, 'line_noise_criterion', 4));
    burst_crit = double(eegmcp_opt(opts, 'burst_criterion', 20));
    window_crit = double(eegmcp_opt(opts, 'window_criterion', 0.25));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct('thresholds_recorded', any(cellfun(@(k) isfield(opts, k), keys)));
    derived = eegmcp_b1_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_clean_rawdata', opts, derived);
    if blocked
        return
    end

    if dataset.trials > 1
        eegmcp_fail('epoched_data', 'clean_rawdata needs continuous data; this dataset is epoched.', ...
            'Run eeglab_clean_rawdata before eeglab_epoch.');
        return
    end
    if exist('pop_clean_rawdata', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'pop_clean_rawdata (clean_rawdata plugin) is not on the MATLAB path.', ...
            'Install the clean_rawdata plugin from the EEGLAB plugin manager.');
        return
    end

    labels_before = {};
    if ~isempty(dataset.chanlocs)
        labels_before = {dataset.chanlocs.labels};
    end
    pnts_before = dataset.pnts;
    com = '';
    evalc(['[dataset, com] = pop_clean_rawdata(dataset, ''FlatlineCriterion'', flatline, ' ...
        '''ChannelCriterion'', channel_crit, ''LineNoiseCriterion'', line_noise_crit, ' ...
        '''Highpass'', [0.25 0.75], ''BurstCriterion'', burst_crit, ''BurstRejection'', ''on'', ' ...
        '''WindowCriterion'', window_crit, ''Distance'', ''Euclidian'', ' ...
        '''WindowCriterionTolerances'', [-Inf 7]);']);
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.status = 'success';
    result.flatline_criterion = flatline;
    result.channel_criterion = channel_crit;
    result.line_noise_criterion = line_noise_crit;
    result.burst_criterion = burst_crit;
    result.window_criterion = window_crit;
    result.nbchan = dataset.nbchan;
    result.srate = dataset.srate;
    result.pnts = dataset.pnts;
    result.trials = dataset.trials;
    if ~isempty(labels_before) && ~isempty(dataset.chanlocs)
        result.removed_channels = setdiff(labels_before, {dataset.chanlocs.labels}, 'stable');
    else
        result.removed_channels = {};
    end
    result.retained_data_fraction = dataset.pnts / pnts_before;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('clean_rawdata_failed', err.message, ...
        'Check that the data are continuous and the thresholds are not too aggressive.');
end
end
