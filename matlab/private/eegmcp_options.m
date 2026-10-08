function opts = eegmcp_options(text)
%EEGMCP_OPTIONS Decode a tool's options argument (a JSON object as text).
%   The MATLAB MCP Core Server only passes scalar arguments, so optional and
%   list-valued arguments travel in one JSON object. An empty string means
%   "no options". Errors with identifier eegmcp:options on invalid input.

text = strtrim(char(text));
if isempty(text)
    opts = struct();
    return
end
try
    opts = jsondecode(text);
catch err
    error('eegmcp:options', 'options is not valid JSON: %s', err.message);
end
if ~isstruct(opts) || ~isscalar(opts)
    error('eegmcp:options', 'options must be a JSON object, for example {"channels": ["Cz"]}.');
end
end
