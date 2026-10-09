function eegmcp_study_create(options)
%EEGMCP_STUDY_CREATE Create a STUDY from explicit datasets without resaving raw data.
global STUDY ALLEEG EEG CURRENTSET CURRENTSTUDY
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'dataset_paths', 'strings'; 'subjects', 'strings'; ...
        'conditions', 'strings'; 'study_name', 'string'; 'bids_path', 'string'});
    paths = eegmcp_cellstr(eegmcp_opt(opts, 'dataset_paths', {}));
    bids = eegmcp_opt(opts, 'bids_path', '');
    if isempty(paths) == isempty(bids)
        error('eegmcp:arguments', 'Specify exactly one of dataset_paths and bids_path.');
    end
    derived = struct('dataset_paths', {paths}, 'bids_path', bids);
    [gate, blocked] = eegmcp_gate('eeglab_study_create', opts, derived);
    if blocked
        return
    end
    if ~isempty(bids)
        imported = eegmcp_run_step('eegmcp_import_bids', jsonencode(opts));
        if strcmp(imported.status, 'error')
            eegmcp_emit(imported);
            return
        end
    else
        subjects = eegmcp_cellstr(eegmcp_opt(opts, 'subjects', {}));
        conditions = eegmcp_cellstr(eegmcp_opt(opts, 'conditions', {}));
        if (~isempty(subjects) && numel(subjects) ~= numel(paths)) || ...
                (~isempty(conditions) && numel(conditions) ~= numel(paths))
            error('eegmcp:arguments', 'subjects and conditions must match dataset_paths in length.');
        end
        commands = cell(1, numel(paths));
        for k = 1:numel(paths)
            if ~isfile(paths{k})
                eegmcp_fail('file_not_found', ['Dataset not found: ' paths{k}], 'Use existing cloud .set files.');
                return
            end
            commands{k} = {'index', k, 'load', paths{k}};
            if ~isempty(subjects)
                commands{k} = [commands{k}, {'subject', subjects{k}}];
            end
            if ~isempty(conditions)
                commands{k} = [commands{k}, {'condition', conditions{k}}];
            end
        end
        new_study = []; new_alleeg = [];
        study_name = eegmcp_opt(opts, 'study_name', 'MyStudy');
        evalc(['[new_study, new_alleeg] = std_editset([], [], ''name'', study_name, ' ...
            '''commands'', commands, ''updatedat'', ''on'', ''savedat'', ''off'', ''resave'', ''off'');']);
        STUDY = new_study; ALLEEG = new_alleeg; EEG = ALLEEG(1); CURRENTSET = 1; CURRENTSTUDY = 1;
    end
    result = struct('status', 'success', 'study_name', STUDY.name, 'num_datasets', numel(ALLEEG), ...
        'subjects', {STUDY.subject}, 'raw_datasets_resaved', false);
    eegmcp_emit(eegmcp_with_gate(result, gate));
catch err
    eegmcp_workflow_fail(err, 'study_create_failed');
end
end
