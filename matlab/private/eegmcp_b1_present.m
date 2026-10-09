function present = eegmcp_b1_present(opts, name)
%EEGMCP_B1_PRESENT True when an option is set and not blank.
%   Null, a blank string, an empty list and an empty object count as absent.

present = false;
if ~isfield(opts, name)
    return
end
value = opts.(name);
if ischar(value) || isstring(value)
    present = ~isempty(strtrim(char(value)));
elseif isstruct(value)
    present = ~isempty(value) && (numel(value) > 1 || ~isempty(fieldnames(value)));
else
    present = ~isempty(value);
end
end
