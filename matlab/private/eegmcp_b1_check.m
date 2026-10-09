function errors = eegmcp_b1_check(opts, spec)
%   Validate option types before scientific operations.
%   SPEC is an N-by-2 or N-by-3 cell array of {name, type, allowed}. TYPE is
%   'number', 'positive' (a finite number greater than 0), 'string',
%   'boolean', 'strings' (a list of names or a comma-separated string) or
%   'object'. ALLOWED is an optional cell array of allowed strings. Options
%   that are absent or null are skipped. Returns a cell array of messages.

errors = {};
for k = 1:size(spec, 1)
    name = spec{k, 1};
    if ~isfield(opts, name) || (isnumeric(opts.(name)) && isempty(opts.(name)))
        continue
    end
    value = opts.(name);
    switch spec{k, 2}
        case {'number', 'positive'}
            if ~(isnumeric(value) && isscalar(value) && isreal(value))
                errors{end + 1} = sprintf('%s must be number', name); %#ok<AGROW>
            elseif ~isfinite(value)
                errors{end + 1} = sprintf('%s must be a finite number', name); %#ok<AGROW>
            elseif strcmp(spec{k, 2}, 'positive') && value <= 0
                errors{end + 1} = sprintf('%s must be a finite number greater than 0', name); %#ok<AGROW>
            end
        case 'string'
            if ~(ischar(value) || (isstring(value) && isscalar(value)))
                errors{end + 1} = sprintf('%s must be string', name); %#ok<AGROW>
            elseif size(spec, 2) > 2 && ~isempty(spec{k, 3}) && ~any(strcmp(char(value), spec{k, 3}))
                errors{end + 1} = sprintf('%s must be one of: %s', name, strjoin(spec{k, 3}, ', ')); %#ok<AGROW>
            end
        case 'boolean'
            if ~(islogical(value) && isscalar(value))
                errors{end + 1} = sprintf('%s must be boolean', name); %#ok<AGROW>
            end
        case 'strings'
            if ~(ischar(value) || isstring(value) || ...
                    (iscell(value) && all(cellfun(@(v) ischar(v) || isstring(v), value(:)))))
                errors{end + 1} = sprintf('every item of %s must be string', name); %#ok<AGROW>
            end
        case 'object'
            if ~(isstruct(value) && isscalar(value))
                errors{end + 1} = sprintf('%s must be object', name); %#ok<AGROW>
            end
    end
end
end
