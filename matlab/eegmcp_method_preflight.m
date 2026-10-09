function eegmcp_method_preflight(options)
%EEGMCP_METHOD_PREFLIGHT Evaluate official prerequisites without changing EEG.
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'method', 'string', []; 'tool_name', 'string', []; ...
        'context', 'object', []; 'strictness', 'string', {'hard', 'advisory', 'strict', 'default'}; ...
        'override_reason', 'string', []});
    summary = eegmcp_preflight_eval(eegmcp_opt(opts, 'method', ''), eegmcp_opt(opts, 'tool_name', ''), ...
        eegmcp_opt(opts, 'context', struct()), eegmcp_opt(opts, 'strictness', 'hard'), ...
        eegmcp_opt(opts, 'override_reason', ''));
    eegmcp_emit(eegmcp_workflow_result('eeglab_method_preflight', opts, summary));
catch err
    eegmcp_workflow_fail(err, 'preflight_failed');
end
end
