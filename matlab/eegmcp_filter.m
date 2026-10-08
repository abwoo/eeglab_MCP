function eegmcp_filter(options)
%EEGMCP_FILTER Filter the current dataset (MCP tool eeglab_filter).
%   Bandpass, highpass and lowpass filtering use pop_eegfiltnew (FIR,
%   Hamming window). Notch filtering uses pop_cleanline at notch_freq and,
%   when notch_harmonics is true, at its harmonics below the Nyquist
%   frequency. High-risk tool: the derivative_processing gate runs first.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'filter_type'})
        return
    end
    errors = eegmcp_b1_check(opts, { ...
        'filter_type', 'string', {'bandpass', 'highpass', 'lowpass', 'notch'}; ...
        'low_cutoff', 'positive', []; 'high_cutoff', 'positive', []; 'notch_freq', 'positive', []; ...
        'notch_harmonics', 'boolean', []});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if isempty(errors)
        filter_type = char(opts.filter_type);
        needs = struct('bandpass', {{'low_cutoff', 'high_cutoff'}}, 'highpass', {{'low_cutoff'}}, ...
            'lowpass', {{'high_cutoff'}}, 'notch', {{'notch_freq'}});
        required = needs.(filter_type);
        for k = 1:numel(required)
            if ~eegmcp_b1_present(opts, required{k})
                errors{end + 1} = sprintf('%s needs %s', filter_type, required{k}); %#ok<AGROW>
            end
        end
        if eegmcp_b1_present(opts, 'low_cutoff') && eegmcp_b1_present(opts, 'high_cutoff') && ...
                opts.low_cutoff >= opts.high_cutoff
            errors{end + 1} = 'low_cutoff must be less than high_cutoff';
        end
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_filter', errors);
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = eegmcp_b1_output_context(opts, struct('parameters_recorded', true));
    [gate, blocked] = eegmcp_gate('eeglab_filter', opts, derived);
    if blocked
        return
    end

    nyquist = dataset.srate / 2;
    low_cutoff = [];
    high_cutoff = [];
    if any(strcmp(filter_type, {'bandpass', 'highpass'}))
        low_cutoff = opts.low_cutoff;
    end
    if any(strcmp(filter_type, {'bandpass', 'lowpass'}))
        high_cutoff = opts.high_cutoff;
    end
    cutoffs = [low_cutoff, high_cutoff];
    if strcmp(filter_type, 'notch')
        cutoffs = opts.notch_freq;
    end
    if any(cutoffs >= nyquist)
        eegmcp_fail('invalid_arguments', sprintf(['Filter frequencies must be below the Nyquist ' ...
            'frequency (%g Hz).'], nyquist), 'Lower the cutoff frequencies, then retry.');
        return
    end

    com = '';
    result.status = 'success';
    result.filter_type = filter_type;
    if strcmp(filter_type, 'notch')
        if exist('pop_cleanline', 'file') ~= 2
            eegmcp_fail('plugin_missing', 'pop_cleanline (cleanline plugin) is not on the MATLAB path.', ...
                'Install the cleanline plugin, or use a bandpass filter instead.');
            return
        end
        notch_freq = opts.notch_freq;
        freqs = notch_freq;
        if isequal(eegmcp_opt(opts, 'notch_harmonics', true), true)
            harmonics = notch_freq * (2:4);
            freqs = [freqs, harmonics(harmonics < nyquist)];
        end
        evalc(['[dataset, com] = pop_cleanline(dataset, ''linefreqs'', freqs, ''bandwidth'', 2, ' ...
            '''tau'', 100, ''winsize'', 4);']);
        result.notch_freqs = freqs;
    else
        args = {};
        if ~isempty(low_cutoff)
            args = [args, {'locutoff', low_cutoff}];
        end
        if ~isempty(high_cutoff)
            args = [args, {'hicutoff', high_cutoff}];
        end
        evalc('[dataset, com] = pop_eegfiltnew(dataset, args{:});');
        result.low_cutoff = low_cutoff;
        result.high_cutoff = high_cutoff;
    end
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.nbchan = dataset.nbchan;
    result.srate = dataset.srate;
    result.pnts = dataset.pnts;
    result.trials = dataset.trials;
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('filter_failed', err.message, ...
        'Check the cutoffs against the sampling rate and that the firfilt plugin is installed.');
end
end
