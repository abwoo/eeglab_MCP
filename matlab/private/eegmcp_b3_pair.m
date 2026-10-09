function [value, message] = eegmcp_b3_pair(opts, name, default, allow_equal)
%   Validate option types before scientific operations.
%   Returns DEFAULT when the option is absent. MESSAGE is '' when the value
%   is valid, else the validation error (two finite numbers, ascending, or
%   non-decreasing when ALLOW_EQUAL is true).

message = '';
value = eegmcp_opt(opts, name, default);
if ~(isnumeric(value) || islogical(value)) || numel(value) ~= 2
    message = sprintf('%s must be a list of exactly 2 numbers', name);
    return
end
value = double(value(:)');
if ~all(isfinite(value))
    message = sprintf('%s must contain only finite numbers', name);
elseif allow_equal && value(1) > value(2)
    message = sprintf('%s start must be less than or equal to end', name);
elseif ~allow_equal && value(1) >= value(2)
    message = sprintf('%s start must be less than end', name);
end
end
