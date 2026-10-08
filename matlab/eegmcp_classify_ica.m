function eegmcp_classify_ica(options)
%EEGMCP_CLASSIFY_ICA Label ICA components with ICLabel (MCP tool eeglab_classify_ica).
%   Options (JSON object): only the gate options method_context,
%   override_gate and override_reason. Runs pop_iclabel with the default
%   network and stores the classification in EEG.etc.ic_classification.

try
    opts = eegmcp_options(options);
    if eegmcp_b2_invalid('eeglab_classify_ica', eegmcp_b2_override_errors(opts, {}))
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    [gate, blocked] = eegmcp_gate('eeglab_classify_ica', opts, eegmcp_b2_output_context(opts, struct()));
    if blocked
        return
    end

    if ~isfield(dataset, 'icaweights') || isempty(dataset.icaweights)
        eegmcp_fail('no_ica', 'ICA has not been run yet.', 'Call eeglab_run_ica first.');
        return
    end
    if exist('pop_iclabel', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'The ICLabel plugin is not installed.', ...
            'Install the ICLabel EEGLAB plugin, then retry.');
        return
    end

    evalc('dataset = pop_iclabel(dataset, ''default'');');
    evalc('eegmcp_commit(dataset);');

    classifications = dataset.etc.ic_classification.ICLabel.classifications;
    labels = {'Brain', 'Muscle', 'Eye', 'Heart', 'Line_Noise', 'Channel_Noise', 'Other'};
    n_components = size(classifications, 1);
    result.status = 'success';
    result.n_components = n_components;
    result.labels = labels;
    result.classifications = struct();
    for i = 1:n_components
        probs = double(classifications(i, :));
        [max_prob, max_idx] = max(probs);
        entry = struct();
        entry.predicted_class = labels{max_idx};
        entry.max_probability = max_prob;
        for j = 1:numel(labels)
            entry.(labels{j}) = probs(j);
        end
        result.classifications.(['comp_' num2str(i)]) = entry;
    end
    result.next_step = ['Review the labels, then call eeglab_flag_components or ' ...
        'eeglab_remove_components with the components to remove.'];
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('classify_ica_failed', err.message, ...
        'Check that ICLabel is installed, the dataset has channel locations and an ICA decomposition.');
end
end
