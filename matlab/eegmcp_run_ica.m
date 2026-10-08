function eegmcp_run_ica(options)
%EEGMCP_RUN_ICA Run an ICA decomposition on the current dataset (MCP tool eeglab_run_ica).
%   Options (JSON object): algorithm ("runica"|"picard", default "runica"),
%   pca_components (integer, default: channel count), extended (boolean,
%   default true), max_steps (integer, default 512), plus the gate options
%   method_context, override_gate and override_reason. Adds ICA weights to
%   the current dataset; the channel data are not changed.

try
    opts = eegmcp_options(options);
    algorithm = eegmcp_opt(opts, 'algorithm', 'runica');
    pca = eegmcp_opt(opts, 'pca_components', []);
    extended = eegmcp_opt(opts, 'extended', true);
    max_steps = eegmcp_opt(opts, 'max_steps', 512);

    errors = {};
    if ~ischar(algorithm) || ~any(strcmp(algorithm, {'runica', 'picard'}))
        errors{end + 1} = 'algorithm must be one of: runica, picard';
    end
    if ~isempty(pca) && ~is_positive_integer(pca)
        errors{end + 1} = 'pca_components must be an integer greater than 0';
    end
    if ~(islogical(extended) && isscalar(extended))
        errors{end + 1} = 'extended must be boolean';
    end
    if ~is_positive_integer(max_steps)
        errors{end + 1} = 'max_steps must be an integer greater than 0';
    end
    errors = eegmcp_b2_override_errors(opts, errors);
    if eegmcp_b2_invalid('eeglab_run_ica', errors)
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end
    if ~isempty(pca) && pca > dataset.nbchan
        eegmcp_fail('invalid_arguments', sprintf('pca_components (%d) exceeds the channel count (%d).', ...
            pca, dataset.nbchan), 'Pass a pca_components value no larger than the channel count.');
        return
    end

    % As _preflight_context_from_arguments: pca_components counts as a rank review.
    derived = struct('rank_reference_reviewed', ~isempty(pca) && pca ~= 0);
    derived = eegmcp_b2_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_run_ica', opts, derived);
    if blocked
        return
    end

    if strcmp(algorithm, 'picard') && exist('picard', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'The picard plugin is not installed.', ...
            'Install the picard EEGLAB plugin, or use algorithm "runica".');
        return
    end

    if strcmp(algorithm, 'runica')
        args = {'icatype', 'runica', 'extended', double(extended), 'maxsteps', max_steps};
    else
        % picard names its iteration limit maxiter; Picard-O (mode ortho)
        % separates sub- and super-Gaussian sources like extended Infomax.
        if extended
            mode = 'ortho';
        else
            mode = 'standard';
        end
        args = {'icatype', 'picard', 'maxiter', max_steps, 'mode', mode};
    end
    if ~isempty(pca)
        args = [args, {'pca', pca}];
    end
    evalc('dataset = pop_runica(dataset, args{:});');
    if isempty(dataset.icaweights)
        eegmcp_fail('run_ica_failed', 'pop_runica returned no ICA weights.', ...
            'Check the data rank and the ICA options, then retry.');
        return
    end
    evalc('eegmcp_commit(dataset);');

    result.status = 'success';
    result.algorithm = algorithm;
    result.ncomponents = size(dataset.icaweights, 1);
    result.extended = extended;
    result.max_steps = max_steps;
    if ~isempty(pca)
        result.pca_components = pca;
    end
    result.next_step = 'Call eeglab_classify_ica to label the components with ICLabel.';
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('run_ica_failed', err.message, ...
        'Check the data rank (use pca_components after average reference) and the ICA options.');
end
end

function ok = is_positive_integer(value)
ok = isnumeric(value) && isscalar(value) && isreal(value) && isfinite(value) && ...
    value == round(value) && value >= 1;
end
