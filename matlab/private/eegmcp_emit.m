function eegmcp_emit(result)
%EEGMCP_EMIT Print a tool result as JSON in the command window.
%   The MATLAB MCP Core Server returns the command window output of a
%   custom tool, so every tool ends by printing exactly one JSON object.

if ~isfield(result, 'status')
    result.status = 'success';
end
fprintf('%s\n', jsonencode(result, 'PrettyPrint', true));
end
