function items = eegmcp_cellstr(value)
%EEGMCP_CELLSTR Turn an option value into a 1xN cell array of char.
%   Accepts a JSON array of strings or numbers, or a comma-separated string.

if isempty(value)
    items = {};
elseif ischar(value) || isstring(value)
    items = strtrim(strsplit(char(value), ','));
    items = items(~cellfun(@isempty, items));
elseif iscell(value)
    items = cellfun(@eegmcp_text, value(:)', 'UniformOutput', false);
elseif isnumeric(value) || islogical(value)
    items = arrayfun(@(v) num2str(v), value(:)', 'UniformOutput', false);
else
    error('eegmcp:options', 'expected a list of names');
end
end
