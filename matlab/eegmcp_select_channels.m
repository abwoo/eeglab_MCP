function eegmcp_select_channels(options)
%EEGMCP_SELECT_CHANNELS Keep or remove channels of the current dataset (MCP tool eeglab_select_channels).
%   Pass exactly one of channels (labels to keep) and exclude_channels
%   (labels to remove). Labels match without regard to case. Uses
%   pop_select, which stores removed channels in EEG.chaninfo.removedchans
%   so eeglab_interpolate_channels can restore them later.

try
    opts = eegmcp_options(options);
    errors = eegmcp_b1_check(opts, {'channels', 'strings'; 'exclude_channels', 'strings'});
    if isempty(errors) && eegmcp_b1_present(opts, 'channels') == eegmcp_b1_present(opts, 'exclude_channels')
        errors{end + 1} = 'channels and exclude_channels are mutually exclusive, specify exactly one';
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_select_channels', errors);
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    keep = eegmcp_b1_present(opts, 'channels');
    if keep
        names = eegmcp_cellstr(opts.channels);
    else
        names = eegmcp_cellstr(opts.exclude_channels);
    end
    [indices, missing] = eegmcp_b1_channels(dataset, names);
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end
    if ~keep && numel(indices) >= dataset.nbchan
        eegmcp_fail('invalid_arguments', 'exclude_channels would remove every channel.', ...
            'Keep at least one channel.');
        return
    end

    com = '';
    result.status = 'success';
    if keep
        evalc('[dataset, com] = pop_select(dataset, ''channel'', indices);');
        result.action = 'select';
        result.selected_channels = names;
    else
        evalc('[dataset, com] = pop_select(dataset, ''rmchannel'', indices);');
        result.action = 'exclude';
        result.excluded_channels = names;
    end
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.nbchan = dataset.nbchan;
    result.channel_labels = {dataset.chanlocs.labels};
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('select_channels_failed', err.message, 'Check the channel labels with eeglab_info.');
end
end
