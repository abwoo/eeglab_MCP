function initialized = eegmcp_http_request(socket, endpoint, catalog, session_id, initialized)
%EEGMCP_HTTP_REQUEST Handle one MCP Streamable HTTP request on runner loopback.
input = socket.getInputStream();
line = read_line(input);
parts = strsplit(line, ' ');
headers = containers.Map('KeyType', 'char', 'ValueType', 'char');
line = read_line(input);
while ~isempty(line)
    colon = strfind(line, ':');
    if isempty(colon)
        reply(socket, 400, rpc_error(NaN, -32600, 'Invalid HTTP header.'), '');
        return
    end
    headers(lower(strtrim(line(1:colon(1) - 1)))) = strtrim(line(colon(1) + 1:end));
    line = read_line(input);
end
length = str2double(header(headers, 'content-length', '0'));
if ~isfinite(length) || length < 0 || length > 1048576 || fix(length) ~= length
    reply(socket, 400, rpc_error(NaN, -32600, 'Invalid content length.'), '');
    return
end
bytes = zeros(1, length, 'uint8');
for k = 1:length
    value = input.read();
    if value < 0
        error('eegmcp:http', 'Incomplete HTTP body.');
    end
    bytes(k) = value;
end
if numel(parts) ~= 3 || ~strcmp(parts{2}, '/mcp')
    reply(socket, 404, rpc_error(NaN, -32600, 'Unknown endpoint.'), '');
    return
end
origin = header(headers, 'origin', '');
if ~isempty(origin) && ~strcmp(origin, extractBefore(endpoint, '/mcp'))
    reply(socket, 403, rpc_error(NaN, -32600, 'Origin is not allowed.'), '');
    return
end
if strcmp(parts{1}, 'DELETE')
    if ~strcmp(header(headers, 'mcp-session-id', ''), session_id)
        reply(socket, 404, rpc_error(NaN, -32600, 'Unknown session.'), '');
    else
        initialized = false;
        reply(socket, 204, [], '');
    end
    return
elseif ~strcmp(parts{1}, 'POST')
    % This server uses JSON responses and does not offer an SSE stream.
    reply(socket, 405, rpc_error(NaN, -32600, 'Use POST for MCP messages.'), '');
    return
end
if ~startsWith(lower(header(headers, 'content-type', '')), 'application/json')
    reply(socket, 415, rpc_error(NaN, -32600, 'Expected application/json.'), '');
    return
end
try
    message = jsondecode(native2unicode(bytes, 'UTF-8'));
catch
    reply(socket, 200, rpc_error(NaN, -32700, 'Invalid JSON.'), '');
    return
end
if ~isstruct(message) || ~isscalar(message) || ~isfield(message, 'method') || ...
        ~ischar(message.method) || ~isfield(message, 'jsonrpc') || ~strcmp(message.jsonrpc, '2.0')
    reply(socket, 200, rpc_error(NaN, -32600, 'Expected a JSON-RPC 2.0 request.'), '');
    return
end
id = eegmcp_opt(message, 'id', NaN);
if strcmp(message.method, 'initialize')
    params = eegmcp_opt(message, 'params', struct());
    protocol = eegmcp_opt(params, 'protocolVersion', '2025-06-18');
    if ~any(strcmp(protocol, {'2025-06-18', '2025-03-26'}))
        protocol = '2025-06-18';
    end
    result = struct('protocolVersion', protocol, 'capabilities', struct('tools', struct('listChanged', false)), ...
        'serverInfo', struct('name', 'eeglab-matlab-mcp', 'version', '1.0.0'));
    initialized = true;
    reply(socket, 200, struct('jsonrpc', '2.0', 'id', id, 'result', result), session_id);
    return
end
if ~initialized || ~strcmp(header(headers, 'mcp-session-id', ''), session_id)
    reply(socket, 404, rpc_error(id, -32600, 'Unknown session.'), '');
    return
end
protocol = header(headers, 'mcp-protocol-version', '2025-03-26');
if ~any(strcmp(protocol, {'2025-06-18', '2025-03-26'}))
    reply(socket, 400, rpc_error(id, -32600, 'Unsupported protocol version.'), '');
    return
end
if ~isfield(message, 'id')
    reply(socket, 202, [], session_id);
    return
end
try
    result = eegmcp_rpc_dispatch(message, catalog);
    response = struct('jsonrpc', '2.0', 'id', id, 'result', result);
catch err
    code = -32603;
    if strcmp(err.identifier, 'eegmcp:rpc_method')
        code = -32601;
    elseif strcmp(err.identifier, 'eegmcp:rpc_params')
        code = -32602;
    end
    response = rpc_error(id, code, err.message);
end
reply(socket, 200, response, session_id);
end

function value = header(headers, key, default)
value = default;
if isKey(headers, key)
    value = headers(key);
end
end

function line = read_line(input)
bytes = uint8([]);
while true
    value = input.read();
    if value < 0 || value == 10
        break
    end
    bytes(end + 1) = value; %#ok<AGROW>
    if numel(bytes) > 8192
        error('eegmcp:http', 'HTTP header line is too long.');
    end
end
line = strtrim(char(bytes));
end

function response = rpc_error(id, code, message)
response = struct('jsonrpc', '2.0', 'id', id, 'error', struct('code', code, 'message', message));
end

function reply(socket, status, response, session_id)
body = uint8([]);
if ~isempty(response)
    body = unicode2native(jsonencode(response), 'UTF-8');
end
headers = sprintf('HTTP/1.1 %d MCP\r\nContent-Type: application/json\r\nContent-Length: %d\r\nConnection: close\r\n', status, numel(body));
if ~isempty(session_id)
    headers = [headers sprintf('Mcp-Session-Id: %s\r\n', session_id)];
end
bytes = [unicode2native([headers sprintf('\r\n')], 'UTF-8'), body];
output = socket.getOutputStream();
output.write(typecast(bytes, 'int8'));
output.flush();
end
