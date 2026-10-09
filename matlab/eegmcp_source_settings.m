function eegmcp_source_settings(options)
%EEGMCP_SOURCE_SETTINGS Configure the DIPFIT head model of the current dataset (MCP tool eeglab_source_settings).
%   Runs pop_dipfit_settings with the standard BEM (MNI) or the BESA
%   four-shell spherical template, an MNI or Colin27 template MRI, and an
%   optional channel file and MRI file, then coregisters the channels to
%   the template when DIPFIT has no stored transform for the montage.
%   Stores the settings in EEG.dipfit of the current dataset. Needs the
%   DIPFIT and FieldTrip-lite plugins.

try
    opts = eegmcp_options(options);
    [head_model, template, derived, message] = eegmcp_b3_source_opts(opts);
    chanfile = eegmcp_text(eegmcp_opt(opts, 'chanfile', ''));
    mrifile = eegmcp_text(eegmcp_opt(opts, 'mrifile', ''));
    if isempty(message) && ~isempty(strtrim(chanfile)) && ~isfile(chanfile) && exist(chanfile, 'file') ~= 2
        message = ['chanfile not found: ' chanfile];
    end
    if isempty(message) && ~isempty(strtrim(mrifile)) && ~isfile(mrifile) && exist(mrifile, 'file') ~= 2
        message = ['mrifile not found: ' mrifile];
    end
    if ~isempty(message)
        eegmcp_fail('invalid_arguments', message, 'Adjust the options, then retry.');
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    [gate, blocked] = eegmcp_gate('eeglab_source_settings', opts, derived);
    if blocked
        return
    end

    [dataset, settings, problem] = eegmcp_b3_dipfit(dataset, head_model, template, strtrim(chanfile), ...
        strtrim(mrifile));
    if ~isempty(problem)
        eegmcp_fail('plugin_missing', problem, 'Install the missing EEGLAB plugin, then retry.');
        return
    end
    eegmcp_commit(dataset);

    result = settings;
    result.status = 'success';
    result.ica_computed = isfield(dataset, 'icaweights') && ~isempty(dataset.icaweights);
    result.next_step = ['Check the coregistration (coord_transform), then call ' ...
        'eeglab_source_localization.'];
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('source_settings_failed', err.message, ...
        'Check the channel locations and the DIPFIT template files, then retry.');
end
end
