function eegmcp_import_bids(options)
%EEGMCP_IMPORT_BIDS Import a BIDS dataset as an EEGLAB STUDY (MCP tool eeglab_import_bids).
%   Runs pop_importbids (EEG-BIDS plugin) with BIDS events and channel
%   locations on. EEG-BIDS writes the .set files and the .study file to
%   bids_path/derivatives/eeglab. The STUDY and ALLEEG globals are replaced
%   and the first dataset becomes the current dataset. High-risk tool: the
%   bids_import gate runs first; it needs plugin_eegbids_available (or
%   plugins_available listing EEG-BIDS) in method_context, or an override.

global EEG ALLEEG CURRENTSET STUDY CURRENTSTUDY
try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'bids_path'})
        return
    end
    errors = eegmcp_b1_check(opts, {'bids_path', 'string'; 'study_name', 'string'});
    errors = [errors, eegmcp_b1_override_errors(opts)];
    if isempty(errors) && ~eegmcp_b1_present(opts, 'bids_path')
        errors{end + 1} = 'bids_path must not be empty';
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_import_bids', errors);
        return
    end
    bids_path = strtrim(char(opts.bids_path));
    study_name = char(eegmcp_opt(opts, 'study_name', 'MyStudy'));
    if isempty(strtrim(study_name))
        study_name = 'MyStudy';
    end

    derived = struct('project_scale', 'bids_study', 'bids_path', bids_path);
    derived.plugin_eegbids_available = plugin_listed(eegmcp_opt(opts, 'method_context', struct()));
    derived = eegmcp_b1_output_context(opts, derived);
    [gate, blocked] = eegmcp_gate('eeglab_import_bids', opts, derived);
    if blocked
        return
    end

    if ~isfolder(bids_path)
        eegmcp_fail('bids_path_not_found', ['BIDS folder not found: ' bids_path], ...
            'Pass the absolute path of the BIDS dataset root (the folder with dataset_description.json).');
        return
    end
    if exist('pop_importbids', 'file') ~= 2
        eegmcp_fail('plugin_missing', 'pop_importbids (EEG-BIDS plugin) is not on the MATLAB path.', ...
            'Install the EEG-BIDS plugin from the EEGLAB plugin manager.');
        return
    end

    new_study = [];
    new_alleeg = [];
    evalc(['[new_study, new_alleeg] = pop_importbids(bids_path, ''studyName'', study_name, ' ...
        '''bidsevent'', ''on'', ''bidschanloc'', ''on'');']);
    if isempty(new_alleeg)
        eegmcp_fail('bids_import_empty', 'pop_importbids imported no datasets.', ...
            'Check that the folder follows the BIDS EEG layout (sub-*/eeg/*_eeg.*).');
        return
    end

    STUDY = new_study;
    CURRENTSTUDY = 1;
    ALLEEG = new_alleeg;
    first = ALLEEG(1);
    if ischar(first.data)
        evalc('first = eeg_checkset(first, ''loaddata'');');
    end
    EEG = first;
    CURRENTSET = 1;

    subjects = {};
    if isfield(STUDY, 'datasetinfo') && isfield(STUDY.datasetinfo, 'subject')
        subjects = unique(cellfun(@eegmcp_text, {STUDY.datasetinfo.subject}, 'UniformOutput', false));
    end
    result.status = 'success';
    result.study_name = study_name;
    if isfield(STUDY, 'filename') && ~isempty(STUDY.filename)
        result.study_file = fullfile(STUDY.filepath, STUDY.filename);
    end
    result.num_datasets = numel(ALLEEG);
    result.subjects = subjects;
    result.first_dataset = struct('nbchan', EEG.nbchan, 'srate', EEG.srate, 'pnts', EEG.pnts, ...
        'trials', EEG.trials, 'setname', EEG.setname);
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('import_bids_failed', err.message, ...
        'Check the BIDS layout (for example with the BIDS validator) and the EEG-BIDS plugin.');
end
end

function listed = plugin_listed(ctx)
% plugin_eegbids_available as server.py derives it from method_context.
listed = false;
if ~isstruct(ctx) || ~isscalar(ctx)
    return
end
if isfield(ctx, 'plugin_eegbids_available')
    value = ctx.plugin_eegbids_available;
    if (islogical(value) || isnumeric(value)) && isscalar(value)
        listed = value ~= 0;
    else
        listed = ~isempty(value);
    end
end
if ~listed && isfield(ctx, 'plugins_available')
    plugins = ctx.plugins_available;
    if iscell(plugins)
        names = cellfun(@eegmcp_text, plugins(:)', 'UniformOutput', false);
        listed = any(strcmp(names, 'EEG-BIDS')) || any(strcmp(names, 'pop_importbids'));
    elseif ischar(plugins)
        listed = contains(plugins, 'EEG-BIDS') || contains(plugins, 'pop_importbids');
    end
end
end
