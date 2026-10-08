function errors = eegmcp_b2_pair_errors(opts, name, errors, allow_equal)
%EEGMCP_B2_PAIR_ERRORS Check an optional [start, end] option of two finite numbers.
%   As the minItems/maxItems schema check plus _ascending_pair in schemas.py.

if nargin < 4
    allow_equal = false;
end
if ~isfield(opts, name) || (isnumeric(opts.(name)) && isempty(opts.(name)))
    return
end
value = opts.(name);
if ~(isnumeric(value) && isreal(value)) || islogical(value)
    errors{end + 1} = [name ' must be a list of 2 numbers'];
    return
end
if numel(value) ~= 2
    errors{end + 1} = [name ' must have exactly 2 items'];
    return
end
if ~all(isfinite(value))
    errors{end + 1} = [name ' must contain only finite numbers'];
elseif allow_equal && value(1) > value(2)
    errors{end + 1} = [name ' start must be less than or equal to end'];
elseif ~allow_equal && value(1) >= value(2)
    errors{end + 1} = [name ' start must be less than end'];
end
end
