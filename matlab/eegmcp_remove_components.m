function eegmcp_remove_components(options)
%EEGMCP_REMOVE_COMPONENTS Remove ICA components from the data (MCP tool eeglab_remove_components).
%   Options (JSON object): component_indices (list of integers counted
%   from 1) or auto_remove_brain_threshold (number between 0 and 1;
%   components whose ICLabel Brain probability is below it are removed),
%   exactly one of them, plus the gate options method_context,
%   override_gate and override_reason. Wraps pop_subcomp.

try
    opts = eegmcp_options(options);
    indices = eegmcp_opt(opts, 'component_indices', []);
    threshold = eegmcp_opt(opts, 'auto_remove_brain_threshold', []);

    errors = {};
    has_indices = ~isempty(indices);
    has_threshold = ~isempty(threshold);
    if has_indices == has_threshold
        errors{end + 1} = ['component_indices and auto_remove_brain_threshold are mutually ' ...
            'exclusive, specify exactly one'];
    end
    if has_indices
        if ~isnumeric(indices) || ~isreal(indices) || any(~isfinite(indices(:))) || ...
                any(indices(:) ~= round(indices(:))) || any(indices(:) < 1)
            errors{end + 1} = 'component_indices indices must be positive integers starting at 1';
        else
            indices = unique(double(indices(:)'));
        end
    end
    if has_threshold && ~(isnumeric(threshold) && isscalar(threshold) && isreal(threshold) && ...
            isfinite(threshold) && threshold >= 0 && threshold <= 1)
        errors{end + 1} = 'auto_remove_brain_threshold must be between 0 and 1';
    end
    errors = eegmcp_b2_override_errors(opts, errors);
    if eegmcp_b2_invalid('eeglab_remove_components', errors)
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    % As _preflight_context_from_arguments: an explicit selection counts as reviewed.
    derived = struct('component_reviewed', has_indices || (has_threshold && threshold ~= 0));
    derived = eegmcp_b2_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_remove_components', opts, derived);
    if blocked
        return
    end

    if ~isfield(dataset, 'icaweights') || isempty(dataset.icaweights)
        eegmcp_fail('no_ica', 'ICA has not been run yet.', 'Call eeglab_run_ica first.');
        return
    end
    ncomp = size(dataset.icaweights, 1);

    result.status = 'success';
    if has_threshold
        classified = isfield(dataset.etc, 'ic_classification') && ...
            isfield(dataset.etc.ic_classification, 'ICLabel') && ...
            isfield(dataset.etc.ic_classification.ICLabel, 'classifications') && ...
            ~isempty(dataset.etc.ic_classification.ICLabel.classifications);
        if ~classified
            eegmcp_fail('not_classified', 'ICLabel classification has not been run yet.', ...
                'Call eeglab_classify_ica first.');
            return
        end
        brain_probs = dataset.etc.ic_classification.ICLabel.classifications(:, 1);
        indices = find(brain_probs < threshold)';
        result.auto_remove_brain_threshold = threshold;
    elseif any(indices > ncomp)
        eegmcp_fail('invalid_arguments', sprintf('component_indices must be between 1 and %d.', ncomp), ...
            'Pass indices of existing ICA components.');
        return
    end

    if isempty(indices)
        result.message = ['no components to remove (every component has a Brain probability ' ...
            'at or above the threshold)'];
        result.removed_components = {};
        result.num_removed = 0;
        result.remaining_channels = dataset.nbchan;
        result.remaining_components = ncomp;
    elseif numel(indices) >= ncomp
        eegmcp_fail('invalid_arguments', 'This would remove every ICA component.', ...
            'Keep at least one component; review the classification and pass fewer indices.');
        return
    else
        evalc('dataset = pop_subcomp(dataset, indices, 0);');
        evalc('eegmcp_commit(dataset);');
        result.removed_components = eegmcp_b2_list(indices);
        result.num_removed = numel(indices);
        result.remaining_channels = dataset.nbchan;
        result.remaining_components = size(dataset.icaweights, 1);
    end
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('remove_components_failed', err.message, ...
        'Check the component indices against the ICA decomposition of the dataset.');
end
end
