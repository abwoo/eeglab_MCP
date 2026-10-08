function [value, message] = eegmcp_b3_bool(opts, name, default)
%EEGMCP_B3_BOOL Read a boolean option. MESSAGE is '' unless the value is not true/false.

message = '';
value = eegmcp_opt(opts, name, default);
if (islogical(value) || isnumeric(value)) && isscalar(value)
    value = logical(value);
else
    message = sprintf('%s must be true or false', name);
    value = default;
end
end
