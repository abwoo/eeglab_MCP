function values = eegmcp_numeric(value, name)
%EEGMCP_NUMERIC Turn an option value into a numeric row vector.

if isnumeric(value) || islogical(value)
    values = double(value(:)');
elseif ischar(value) || isstring(value)
    values = str2num(char(value)); %#ok<ST2NM> accepts "1 2" and "[1, 2]"
    if isempty(value) || ~isempty(values)
        values = values(:)';
    else
        error('eegmcp:options', '%s must be a list of numbers', name);
    end
elseif iscell(value) && all(cellfun(@(v) isnumeric(v) && isscalar(v), value))
    values = cellfun(@double, value(:)');
else
    error('eegmcp:options', '%s must be a list of numbers', name);
end
end
