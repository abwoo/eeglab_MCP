function errors = eegmcp_b1_override_errors(opts)
%EEGMCP_B1_OVERRIDE_ERRORS Check the gate options shared by every high-risk tool.
%   override_gate must be a boolean, and override_reason must be given when
%   override_gate is true, as validate_tool_contracts in schemas.py requires.

errors = eegmcp_b1_check(opts, {'override_gate', 'boolean'; 'override_reason', 'string'});
if isempty(errors) && isequal(eegmcp_opt(opts, 'override_gate', false), true) && ...
        ~eegmcp_b1_present(opts, 'override_reason')
    errors{end + 1} = 'override_reason is required when override_gate is true';
end
if isfield(opts, 'method_context') && ~isempty(opts.method_context) && ...
        ~(isstruct(opts.method_context) && isscalar(opts.method_context))
    errors{end + 1} = 'method_context must be object';
end
end
