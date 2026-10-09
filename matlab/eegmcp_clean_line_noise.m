function eegmcp_clean_line_noise(options)
%EEGMCP_CLEAN_LINE_NOISE Remove line noise with CleanLine (MCP tool eeglab_clean_line_noise).
%   Runs pop_cleanline (cleanline plugin) at line_freq, which fits and
%   removes sinusoids adaptively in sliding windows of winsize seconds.
%   High-risk tool: the line_noise gate runs first.

try
    opts = eegmcp_options(options);
    errors = eegmcp_b1_check(opts, {'line_freq', 'positive'; 'bandwidth', 'positive'; ...
        'tau', 'positive'; 'winsize', 'positive'});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_clean_line_noise', errors);
        return
    end
    line_freq = double(eegmcp_opt(opts, 'line_freq', 50));
    bandwidth = double(eegmcp_opt(opts, 'bandwidth', 2));
    tau = double(eegmcp_opt(opts, 'tau', 100));
    winsize = double(eegmcp_opt(opts, 'winsize', 4));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct();
    if eegmcp_b1_present(opts, 'line_freq')
        derived.line_freq = line_freq;
    end
    if eegmcp_b1_present(opts, 'bandwidth') || eegmcp_b1_present(opts, 'tau') || ...
            eegmcp_b1_present(opts, 'winsize')
        derived.line_noise_method = 'clean_line_noise';
        derived.line_noise_parameters_recorded = eegmcp_b1_present(opts, 'line_freq');
    end
    derived.parameters_recorded = true;
    derived = eegmcp_b1_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_clean_line_noise', opts, derived);
    if blocked
        return
    end

    if line_freq >= dataset.srate / 2
        eegmcp_fail('invalid_arguments', sprintf(['line_freq must be below the Nyquist frequency ' ...
            '(%g Hz).'], dataset.srate / 2), 'Check line_freq against the sampling rate.');
        return
    end
    if winsize > dataset.pnts / dataset.srate
        eegmcp_fail('invalid_arguments', sprintf(['winsize must not exceed the epoch or recording ' ...
            'length (%g s).'], dataset.pnts / dataset.srate), 'Lower winsize, then retry.');
        return
    end
    if exist('pop_cleanline', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'pop_cleanline (cleanline plugin) is not on the MATLAB path.', ...
            'Install the cleanline plugin from the EEGLAB plugin manager.');
        return
    end

    com = '';
    evalc(['[dataset, com] = pop_cleanline(dataset, ''linefreqs'', line_freq, ''bandwidth'', bandwidth, ' ...
        '''tau'', tau, ''winsize'', winsize);']);
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.status = 'success';
    result.line_freq = line_freq;
    result.bandwidth = bandwidth;
    result.tau = tau;
    result.winsize = winsize;
    result.nbchan = dataset.nbchan;
    result.srate = dataset.srate;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('clean_line_noise_failed', err.message, ...
        'Check line_freq and winsize against the data, and that the cleanline plugin is installed.');
end
end
