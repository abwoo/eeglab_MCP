function eegmcp_flag_components(options)
%EEGMCP_FLAG_COMPONENTS Flag ICA components from ICLabel probabilities (MCP tool eeglab_flag_components).
%   Options (JSON object): brain_range, muscle_range, eye_range,
%   heart_range, line_noise_range, channel_noise_range, other_range (each
%   [min, max] probabilities between 0 and 1; a component whose class
%   probability lies inside a range is flagged), plus the gate options
%   method_context, override_gate and override_reason. Runs ICLabel first
%   when the dataset has no classification. Sets EEG.reject.gcompreject;
%   the data are not changed.

try
    opts = eegmcp_options(options);
    names = {'brain_range', 'muscle_range', 'eye_range', 'heart_range', ...
        'line_noise_range', 'channel_noise_range', 'other_range'};
    errors = {};
    thresholds = nan(numel(names), 2);
    for k = 1:numel(names)
        before = numel(errors);
        errors = eegmcp_b2_pair_errors(opts, names{k}, errors, true);
        value = eegmcp_opt(opts, names{k}, []);
        if numel(errors) == before && ~isempty(value)
            if value(1) < 0 || value(2) > 1
                errors{end + 1} = [names{k} ' probability must be between 0 and 1']; %#ok<AGROW>
            else
                thresholds(k, :) = double(value(:)');
            end
        end
    end
    errors = eegmcp_b2_override_errors(opts, errors);
    if eegmcp_b2_invalid('eeglab_flag_components', errors)
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    [gate, blocked] = eegmcp_gate('eeglab_flag_components', opts, eegmcp_b2_output_context(opts, struct()));
    if blocked
        return
    end

    if ~isfield(dataset, 'icaweights') || isempty(dataset.icaweights)
        eegmcp_fail('no_ica', 'ICA has not been run yet.', 'Call eeglab_run_ica first.');
        return
    end
    classified = isfield(dataset, 'etc') && isfield(dataset.etc, 'ic_classification') && ...
        isfield(dataset.etc.ic_classification, 'ICLabel') && ...
        isfield(dataset.etc.ic_classification.ICLabel, 'classifications') && ...
        ~isempty(dataset.etc.ic_classification.ICLabel.classifications);
    if ~classified
        if exist('pop_iclabel', 'file') ~= 2
            eegmcp_fail('plugin_missing', 'The ICLabel plugin is not installed.', ...
                'Install the ICLabel EEGLAB plugin, then retry.');
            return
        end
        evalc('dataset = pop_iclabel(dataset, ''default'');');
    end
    if exist('pop_icflag', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'pop_icflag (ICLabel plugin) is not on the MATLAB path.', ...
            'Install the ICLabel EEGLAB plugin, then retry.');
        return
    end

    evalc('dataset = pop_icflag(dataset, thresholds);');
    evalc('eegmcp_commit(dataset);');

    if isfield(dataset, 'reject') && isfield(dataset.reject, 'gcompreject') && ~isempty(dataset.reject.gcompreject)
        flagged = find(dataset.reject.gcompreject);
    else
        flagged = [];
    end
    result.status = 'success';
    result.flag_thresholds = struct();
    for k = 1:numel(names)
        if all(isfinite(thresholds(k, :)))
            result.flag_thresholds.(names{k}) = thresholds(k, :);
        else
            result.flag_thresholds.(names{k}) = [];
        end
    end
    result.iclabel_run_here = ~classified;
    result.flagged_components = eegmcp_b2_list(flagged);
    result.num_flagged = numel(flagged);
    result.next_step = ['Review the flagged components, then call eeglab_remove_components ' ...
        'with component_indices to remove them.'];
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('flag_components_failed', err.message, ...
        'Check that ICLabel is installed and the dataset has an ICA decomposition.');
end
end
