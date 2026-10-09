function eegmcp_resample(options)
%EEGMCP_RESAMPLE Resample the current dataset (MCP tool eeglab_resample).
%   Uses pop_resample, which applies its own anti-aliasing filter. Apply a
%   lowpass filter below the new Nyquist frequency first when downsampling
%   for analysis. High-risk tool: the derivative_processing gate runs first.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'new_srate'})
        return
    end
    errors = [eegmcp_b1_check(opts, {'new_srate', 'positive'}), eegmcp_b1_override_errors(opts)];
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_resample', errors);
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = eegmcp_b1_output_context(opts, struct('parameters_recorded', true));
    [gate, blocked] = eegmcp_gate('eeglab_resample', opts, derived);
    if blocked
        return
    end

    new_srate = double(opts.new_srate);
    old_srate = dataset.srate;
    com = '';
    evalc('[dataset, com] = pop_resample(dataset, new_srate);');
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.status = 'success';
    result.old_srate = old_srate;
    result.new_srate = dataset.srate;
    result.nbchan = dataset.nbchan;
    result.pnts = dataset.pnts;
    result.trials = dataset.trials;
    if new_srate > old_srate
        result.warnings = {'The data were upsampled; upsampling adds no information.'};
    end
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('resample_failed', err.message, ...
        'Check new_srate; pop_resample needs the Signal Processing Toolbox or its fallback.');
end
end
