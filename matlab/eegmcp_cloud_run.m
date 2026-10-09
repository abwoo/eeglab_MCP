function eegmcp_cloud_run(eeglab_root, mode, event_file)
%EEGMCP_CLOUD_RUN Serve MCP in a licensed GitHub MATLAB batch job.
%   The HTTP listener binds only to the runner loopback interface. MATLAB
%   dispatches reviewed tools directly, retaining EEG/STUDY in this session.
if nargin < 2
    mode = 'live';
end
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root, 'matlab'));
folder = fullfile(getenv('RUNNER_TEMP'), 'eeglab-mcp-results');
if ~isfolder(folder)
    mkdir(folder);
end
output = fullfile(folder, ['mcp-' mode '-result.json']);
if isfile(output)
    delete(output);
end
listener = java.net.ServerSocket(0, 1, java.net.InetAddress.getByName('127.0.0.1'));
listener.setSoTimeout(500);
close_listener = onCleanup(@() listener.close());
endpoint = sprintf('http://127.0.0.1:%d/mcp', listener.getLocalPort());
args = {'node', fullfile(root, 'scripts', 'verify_mcp.mjs'), 'native', mode, output, eeglab_root, endpoint};
builder = java.lang.ProcessBuilder(args);
if nargin > 2
    builder.environment().put('GITHUB_EVENT_PATH', event_file);
end
builder.redirectErrorStream(true);
builder.redirectOutput(java.io.File(fullfile(folder, ['mcp-' mode '-harness.log'])));
process = builder.start();
stop_client = onCleanup(@() process.destroy());
catalog = jsondecode(fileread(fullfile(root, 'matlab', 'eeglab-mcp-tools.json')));
session_id = char(java.util.UUID.randomUUID());
initialized = false;
started = tic;
while process.isAlive()
    if toc(started) > 300
        error('eegmcp:cloud', 'MCP cloud client exceeded its execution deadline.');
    end
    try
        socket = listener.accept();
    catch err
        if contains(err.message, 'SocketTimeoutException')
            continue
        end
        rethrow(err)
    end
    close_socket = onCleanup(@() socket.close());
    socket.setSoTimeout(10000);
    initialized = eegmcp_http_request(socket, endpoint, catalog, session_id, initialized);
    clear close_socket
end
if ~isfile(output)
    error('eegmcp:cloud', 'MCP client produced no result.');
end
result = jsondecode(fileread(output));
if process.exitValue() ~= 0 || ~strcmp(result.status, 'success')
    error('eegmcp:cloud', 'MCP cloud request failed: %s', jsonencode(result));
end
if nargin > 2
    assert(strcmp(result.response.status, 'success'), 'Cloud ERP request failed.');
    assert(isfile(result.response.outputs.output_path), 'Cloud ERP derivative is missing.');
end
fprintf('ok: native MATLAB MCP Streamable HTTP, mode=%s, tools=%d\n', mode, result.custom_tool_count);
clear stop_client close_listener
end
