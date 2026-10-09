function result = eegmcp_plan(opts, workflow)
%EEGMCP_PLAN Build a conservative research plan from explicit recording facts.
eegmcp_validate_options(opts, {'analysis_type', 'string'; 'research_goal', 'string'; ...
    'event_types', 'strings'; 'event_semantics', 'object'; 'data_shape', 'string'; ...
    'project_scale', 'string'; 'has_channel_locations', 'boolean'; 'method_context', 'object'});
analysis_type = lower(eegmcp_opt(opts, 'analysis_type', 'auto'));
allowed = {'auto', 'erp', 'resting', 'spectral', 'timefreq', 'ica', 'source', 'study', 'connectivity', 'qc'};
if ~any(strcmp(analysis_type, allowed))
    error('eegmcp:arguments', 'analysis_type is not a supported research branch.');
end
audit_opts = struct('event_types', {eegmcp_cellstr(eegmcp_opt(opts, 'event_types', {}))}, ...
    'event_descriptions', eegmcp_opt(opts, 'event_semantics', struct()));
audit = eegmcp_run_step('eegmcp_event_semantics_audit', jsonencode(audit_opts));
confirmed = audit.summary.confirmed_analysis_events;
if strcmp(analysis_type, 'auto')
    if ~isempty(confirmed)
        analysis_type = 'erp';
    elseif strcmp(eegmcp_opt(opts, 'data_shape', ''), 'continuous')
        analysis_type = 'resting';
    else
        analysis_type = 'qc';
    end
end
methods = struct('erp', 'epoch', 'resting', 'spectral', 'spectral', 'spectral', 'timefreq', 'timefreq', ...
    'ica', 'run_ica', 'source', 'source', 'study', 'study', 'connectivity', 'connectivity', 'qc', 'acquisition_provenance');
ctx = eegmcp_opt(opts, 'method_context', struct());
fields = fieldnames(opts);
for k = 1:numel(fields)
    if ~isfield(ctx, fields{k}) && ~strcmp(fields{k}, 'method_context')
        ctx.(fields{k}) = opts.(fields{k});
    end
end
if ~isempty(confirmed)
    ctx.confirmed_condition_events = confirmed;
end
gate = eegmcp_preflight_eval(methods.(analysis_type), '', ctx, 'hard', '');
questions = {};
if isempty(eegmcp_opt(opts, 'research_goal', ''))
    questions{end + 1} = 'What research hypothesis and output are required?';
end
if isempty(eegmcp_opt(opts, 'project_scale', ''))
    questions{end + 1} = 'What are the subject/session structure and design variables?';
end
if any(strcmp(analysis_type, {'erp', 'timefreq'})) && isempty(confirmed)
    questions{end + 1} = 'Which event codes are confirmed condition triggers?';
end
summary = struct('analysis_type_resolved', analysis_type, 'analysis_event_types', {confirmed}, ...
    'clarifying_questions', {questions}, 'default_assumptions', {{'Unknown marker meanings remain unconfirmed.'}}, ...
    'gate_results', {{gate}}, 'source_claim_ids', {gate.source_claim_ids}, ...
    'blocking_conditions', {cellfun(@(r) r.text, gate.critical_missing_requirements, 'UniformOutput', false)}, ...
    'qc_gates', {{'preserve_raw_input', 'audit_recording_metadata', 'confirm_event_semantics', ...
    'check_plugins', 'record_processing_parameters', 'write_derivative_outputs'}}, ...
    'project_phases', {{'intake', 'read_only_qc', 'preflight', 'preprocessing', 'analysis', 'protocol_export'}});
result = eegmcp_workflow_result(workflow, opts, summary);
end
