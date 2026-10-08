function eegmcp_edit_channels(options)
%EEGMCP_EDIT_CHANNELS Edit channel information (MCP tool eeglab_edit_channels).
%   action "load_loc" loads a channel location file (.loc/.locs/.ced/.sfp
%   and the other formats readlocs detects) with pop_chanedit; the file must
%   list one location per data channel. action "rename" renames channels
%   with rename_map, an object keyed by the old label whose values are the
%   new labels. High-risk tool: the channel_locations gate runs first.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'action'})
        return
    end
    errors = eegmcp_b1_check(opts, {'action', 'string', {'load_loc', 'rename'}; ...
        'loc_file', 'string'; 'rename_map', 'object'});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if isempty(errors)
        action = char(opts.action);
        if strcmp(action, 'load_loc') && ~eegmcp_b1_present(opts, 'loc_file')
            errors{end + 1} = 'loc_file is needed when action is load_loc';
        elseif strcmp(action, 'rename')
            if ~eegmcp_b1_present(opts, 'rename_map')
                errors{end + 1} = 'rename_map is needed when action is rename';
            else
                values = struct2cell(opts.rename_map);
                if ~all(cellfun(@(v) ischar(v) && ~isempty(strtrim(v)), values))
                    errors{end + 1} = 'rename_map must be a mapping of non-empty strings to non-empty strings';
                end
            end
        end
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_edit_channels', errors);
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct();
    if strcmp(action, 'load_loc') && eegmcp_b1_present(opts, 'loc_file')
        derived.loc_file = opts.loc_file;
        derived.channel_location_repair_planned = true;
    end
    if strcmp(action, 'rename') && eegmcp_b1_present(opts, 'rename_map')
        derived.rename_map = opts.rename_map;
        derived.channel_location_repair_planned = true;
    end
    derived.parameters_recorded = true;
    derived = eegmcp_b1_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_edit_channels', opts, derived);
    if blocked
        return
    end

    result.status = 'success';
    result.action = action;
    if strcmp(action, 'load_loc')
        loc_file = char(opts.loc_file);
        if ~isfile(loc_file)
            eegmcp_fail('file_not_found', ['Channel location file not found: ' loc_file], ...
                'Pass the absolute path of a .loc, .locs, .ced or .sfp file.');
            return
        end
        output = evalc('dataset = pop_chanedit(dataset, ''load'', {loc_file, ''filetype'', ''autodetect''});');
        if contains(output, 'changes will be ignored')
            eegmcp_fail('channel_count_mismatch', ...
                'The location file does not list one location per data channel; nothing was changed.', ...
                'Use a location file that matches the data channels.');
            return
        end
        com = sprintf('EEG = pop_chanedit(EEG, ''load'', {''%s'', ''filetype'', ''autodetect''});', ...
            strrep(loc_file, '''', ''''''));
        dataset = eegmcp_b1_hist(dataset, com);
        result.loc_file = loc_file;
    else
        % jsondecode turns keys into valid MATLAB names ("E-1" becomes "E_1"),
        % so each key is matched against the same transform of the labels.
        labels = {dataset.chanlocs.labels};
        valid_labels = cellfun(@(l) matlab.lang.makeValidName(l), labels, 'UniformOutput', false);
        keys = fieldnames(opts.rename_map);
        indices = zeros(1, numel(keys));
        missing = {};
        for k = 1:numel(keys)
            hit = find(strcmp(keys{k}, labels), 1);
            if isempty(hit)
                hit = find(strcmp(keys{k}, valid_labels), 1);
            end
            if isempty(hit)
                hit = find(strcmpi(keys{k}, labels), 1);
            end
            if isempty(hit)
                missing{end + 1} = keys{k}; %#ok<AGROW>
            else
                indices(k) = hit;
            end
        end
        if ~isempty(missing)
            eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
                'Call eeglab_info to list the channel labels.');
            return
        end
        renamed = struct();
        commands = cell(1, numel(keys));
        for k = 1:numel(keys)
            old_label = labels{indices(k)};
            new_label = strtrim(opts.rename_map.(keys{k}));
            dataset.chanlocs(indices(k)).labels = new_label;
            renamed.(keys{k}) = new_label;
            commands{k} = sprintf('EEG = pop_chanedit(EEG, ''changefield'', {%d, ''labels'', ''%s''}); %% was %s', ...
                indices(k), strrep(new_label, '''', ''''''), old_label);
        end
        new_labels = {dataset.chanlocs.labels};
        if numel(unique(new_labels)) < numel(new_labels)
            eegmcp_fail('duplicate_channel_labels', 'The rename would give two channels the same label.', ...
                'Choose unique new labels.');
            return
        end
        dataset = eegmcp_b1_hist(dataset, strjoin(commands, newline));
        result.rename_map = renamed;
    end
    eegmcp_commit(dataset);

    info = eegmcp_dataset_info(dataset);
    result.nbchan = dataset.nbchan;
    result.channel_labels = info.channel_labels;
    result.channels_with_locations = info.channels_with_locations;
    result.has_channel_locations = info.has_channel_locations;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('edit_channels_failed', err.message, ...
        'Check the location file format and that its channels match the data.');
end
end
