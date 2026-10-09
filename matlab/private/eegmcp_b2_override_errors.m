function errors = eegmcp_b2_override_errors(opts, errors)
%EEGMCP_B2_OVERRIDE_ERRORS Add the override contract error of a high-risk tool.
%   Validate option types before scientific operations.
%   non-empty override_reason.

if isequal(eegmcp_opt(opts, 'override_gate', false), true)
    reason = eegmcp_opt(opts, 'override_reason', '');
    if ~(ischar(reason) || isstring(reason)) || isempty(strtrim(char(reason)))
        errors{end + 1} = 'override_reason is required when override_gate is true';
    end
end
end
