function eegmcp_reref(options)
%EEGMCP_REREF Re-reference the current dataset (MCP tool eeglab_reref).
%   ref_type "average" uses pop_reref with an empty reference (average of
%   all channels; this lowers the data rank by 1). "channel" references to
%   ref_channel; a comma-separated list such as "M1,M2" uses the mean of the
%   listed channels, which are then removed from the data as pop_reref does
%   by default. "rest" needs the REST plugin. High-risk tool: the
%   derivative_processing gate runs first.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'ref_type'})
        return
    end
    errors = eegmcp_b1_check(opts, {'ref_type', 'string', {'average', 'channel', 'rest'}; ...
        'ref_channel', 'string', []});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if isempty(errors) && strcmp(opts.ref_type, 'channel') && ~eegmcp_b1_present(opts, 'ref_channel')
        errors{end + 1} = 'ref_channel is needed when ref_type is channel';
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_reref', errors);
        return
    end
    ref_type = char(opts.ref_type);

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = eegmcp_b1_output_context(opts, struct('parameters_recorded', true));
    [gate, blocked] = eegmcp_gate('eeglab_reref', opts, derived);
    if blocked
        return
    end

    com = '';
    result.status = 'success';
    result.ref_type = ref_type;
    switch ref_type
        case 'average'
            evalc('[dataset, com] = pop_reref(dataset, []);');
            result.ref_description = ['average reference over all channels (this reduces the data ' ...
                'rank by 1, so set pca=nchan-1 for ICA)'];
        case 'channel'
            names = eegmcp_cellstr(opts.ref_channel);
            [indices, missing] = eegmcp_b1_channels(dataset, names);
            if ~isempty(missing)
                eegmcp_fail('unknown_channels', ['Reference channels not found: ' strjoin(missing, ', ')], ...
                    'Call eeglab_info to list the channel labels.');
                return
            end
            if numel(indices) >= dataset.nbchan
                eegmcp_fail('invalid_arguments', 'The reference cannot use every channel.', ...
                    'Use ref_type "average" for an average reference.');
                return
            end
            evalc('[dataset, com] = pop_reref(dataset, indices);');
            result.ref_channel = strjoin(names, ',');
            result.ref_description = ['reference to the mean of ' strjoin(names, ', ') ...
                '; the reference channels were removed from the data'];
        case 'rest'
            if exist('pop_REST_reref', 'file') ~= 2
                eegmcp_fail('plugin_missing', 'REST re-referencing needs the REST plugin (pop_REST_reref).', ...
                    'Install the REST plugin, or use ref_type "average".');
            else
                eegmcp_fail('not_supported', ['REST re-referencing needs a lead field and is not run from ' ...
                    'this tool.'], 'Run pop_REST_reref from the EEGLAB menu, or use ref_type "average".');
            end
            return
    end
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.nbchan = dataset.nbchan;
    if isfield(dataset, 'chanlocs') && ~isempty(dataset.chanlocs)
        result.channel_labels = {dataset.chanlocs.labels};
    end
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('reref_failed', err.message, 'Check ref_type and ref_channel against eeglab_info.');
end
end
