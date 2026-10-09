function eegmcp_interpolate_channels(options)
%EEGMCP_INTERPOLATE_CHANNELS Interpolate missing channels (MCP tool eeglab_interpolate_channels).
%   ref_chanlocs "urchanlocs" restores the original channels: EEG.urchanlocs
%   when it holds channel coordinates, otherwise the channels removed
%   earlier (EEG.chaninfo.removedchans). A file path reads a channel
%   location file and interpolates the channels it lists that the dataset
%   lacks. Left empty, the removed channels are restored. Uses pop_interp
%   with method "spherical" (spherical splines) or "v4" (biharmonic
%   splines, slow). High-risk tool: the channel_locations gate runs first.

try
    opts = eegmcp_options(options);
    errors = eegmcp_b1_check(opts, {'ref_chanlocs', 'string', []; 'method', 'string', {'spherical', 'v4'}});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_interpolate_channels', errors);
        return
    end
    ref_chanlocs = strtrim(char(eegmcp_opt(opts, 'ref_chanlocs', '')));
    method = char(eegmcp_opt(opts, 'method', 'spherical'));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct();
    if eegmcp_b1_present(opts, 'ref_chanlocs')
        derived.ref_chanlocs = ref_chanlocs;
        derived.channel_location_repair_planned = true;
    end
    if eegmcp_b1_present(opts, 'method')
        derived.parameters_recorded = true;
    end
    derived = eegmcp_b1_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_interpolate_channels', opts, derived);
    if blocked
        return
    end

    if isempty(dataset.chanlocs) || ~isfield(dataset.chanlocs, 'X') || ...
            any(cellfun(@isempty, {dataset.chanlocs.X}))
        eegmcp_fail('no_channel_locations', 'Interpolation needs X/Y/Z locations for every channel.', ...
            'Load channel locations with eeglab_edit_channels (action load_loc) first.');
        return
    end

    removed = [];
    if isfield(dataset, 'chaninfo') && isfield(dataset.chaninfo, 'removedchans') && ...
            isstruct(dataset.chaninfo.removedchans)
        removed = dataset.chaninfo.removedchans;
    end
    if strcmpi(ref_chanlocs, 'urchanlocs')
        action = 'interpolate_urchanlocs';
        if isfield(dataset, 'urchanlocs') && isstruct(dataset.urchanlocs) && ...
                ~isempty(dataset.urchanlocs) && isfield(dataset.urchanlocs, 'X') && ...
                ~any(cellfun(@isempty, {dataset.urchanlocs.X}))
            target = dataset.urchanlocs;
            source_expr = 'EEG.urchanlocs';
        else
            target = removed;
            source_expr = 'EEG.chaninfo.removedchans';
        end
    elseif ~isempty(ref_chanlocs)
        action = 'interpolate_from_file';
        if ~isfile(ref_chanlocs)
            eegmcp_fail('file_not_found', ['Channel location file not found: ' ref_chanlocs], ...
                'Pass the absolute path of a channel location file, or "urchanlocs".');
            return
        end
        target = [];
        evalc('target = readlocs(ref_chanlocs);');
        source_expr = sprintf('readlocs(''%s'')', strrep(ref_chanlocs, '''', ''''''));
    else
        action = 'interpolate_removed';
        target = removed;
        source_expr = 'EEG.chaninfo.removedchans';
    end

    current = {dataset.chanlocs.labels};
    added = {};
    if isstruct(target) && ~isempty(target) && isfield(target, 'labels')
        added = setdiff({target.labels}, current, 'stable');
    end
    if isempty(added)
        eegmcp_fail('nothing_to_interpolate', 'No missing channels were found to interpolate.', ...
            ['Remove bad channels with eeglab_select_channels first, or pass a channel location ' ...
            'file that lists the missing channels.']);
        return
    end

    com = '';
    evalc('[dataset, com] = pop_interp(dataset, target, method);');
    if isempty(com)
        com = sprintf('EEG = pop_interp(EEG, %s, ''%s'');', source_expr, method);
    end
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.status = 'success';
    result.action = action;
    if ~isempty(ref_chanlocs)
        result.ref_chanlocs = ref_chanlocs;
    end
    result.method = method;
    result.interpolated_channels = added;
    result.nbchan = dataset.nbchan;
    result.channel_labels = {dataset.chanlocs.labels};
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('interpolate_failed', err.message, ...
        'Check that every channel, including the missing ones, has X/Y/Z locations.');
end
end
