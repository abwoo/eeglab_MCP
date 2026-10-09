function eegmcp_study_design(options)
%EEGMCP_STUDY_DESIGN Define a categorical design in the active STUDY.
global STUDY ALLEEG
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'design_name', 'string'; 'variable_name', 'string'; ...
        'variable_values', 'strings'; 'paired', 'boolean'});
    values = eegmcp_cellstr(eegmcp_opt(opts, 'variable_values', {}));
    variable = eegmcp_opt(opts, 'variable_name', 'condition');
    if numel(values) < 2
        error('eegmcp:arguments', 'variable_values must contain at least two explicit design levels.');
    end
    if isempty(STUDY) || isempty(ALLEEG)
        eegmcp_fail('no_study', 'No STUDY is active.', 'Call eeglab_study_create first.');
        return
    end
    derived = struct('project_scale', 'multi_subject', 'variable_name', variable, 'variable_values', {values});
    [gate, blocked] = eegmcp_gate('eeglab_study_design', opts, derived);
    if blocked
        return
    end
    pairing = 'off';
    if eegmcp_opt(opts, 'paired', true)
        pairing = 'on';
    end
    design_name = eegmcp_opt(opts, 'design_name', 'Design1');
    updated = STUDY;
    evalc(['updated = std_makedesign(STUDY, ALLEEG, 1, ''name'', design_name, ' ...
        '''variable1'', variable, ''values1'', values, ''vartype1'', ''categorical'', ''pairing1'', pairing);']);
    STUDY = updated;
    result = struct('status', 'success', 'design_name', design_name, 'variable_name', variable, ...
        'variable_values', {values}, 'paired', strcmp(pairing, 'on'));
    eegmcp_emit(eegmcp_with_gate(result, gate));
catch err
    eegmcp_workflow_fail(err, 'study_design_failed');
end
end
