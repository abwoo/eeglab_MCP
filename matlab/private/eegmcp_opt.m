function value = eegmcp_opt(opts, name, default)
%EEGMCP_OPT Read an option, or return DEFAULT when it is absent or null.

if isfield(opts, name) && ~(isnumeric(opts.(name)) && isempty(opts.(name)))
    value = opts.(name);
else
    value = default;
end
end
