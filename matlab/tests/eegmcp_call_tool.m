function result = eegmcp_call_tool(template, varargin)
%EEGMCP_CALL_TOOL Run a tool call, capture its command window output and decode the JSON.
%   Each extra argument is a char vector, quoted as a MATLAB string literal
%   into TEMPLATE the way the MATLAB MCP Core Server passes arguments.
args = cellfun(@(a) ['"' strrep(a, '"', '""') '"'], varargin, 'UniformOutput', false);
command = sprintf(template, args{:});
output = evalc(command);
start = strfind(output, '{');
if isempty(start)
    error('eegmcp:test', '%s printed no JSON:\n%s', command, output);
end
result = jsondecode(output(start(1):end));
end
