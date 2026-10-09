function eegmcp_validate_options(opts, spec)
%EEGMCP_VALIDATE_OPTIONS Reject malformed research options before using them.
errors = eegmcp_b1_check(opts, spec);
errors = [errors, eegmcp_b1_override_errors(opts)];
if ~isempty(errors)
    error('eegmcp:arguments', '%s', strjoin(errors, '; '));
end
end
