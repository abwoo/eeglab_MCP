function run_eegmcp_cloud_mcp(binary, toolbox, eeglab_root, mode, event_file)
%RUN_EEGMCP_CLOUD_MCP Share this GitHub MATLAB session with the official server.
%   The Node harness speaks JSON-RPC only; every tool executes in MATLAB.
if nargin < 4
    mode = 'live';
end
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(fullfile(root, 'matlab'));
matlab.addons.toolbox.installToolbox(toolbox, true);
shareMATLABSession();
output_dir = fullfile(getenv('RUNNER_TEMP'), 'eeglab-mcp-results');
if ~isfolder(output_dir)
    mkdir(output_dir);
end
output = fullfile(output_dir, ['mcp-' mode '-result.json']);
if isfile(output)
    delete(output);
end
args = {'node', fullfile(root, 'scripts', 'verify_mcp.mjs'), binary, mode, output, eeglab_root};
builder = java.lang.ProcessBuilder(args);
if nargin > 4
    builder.environment().put('GITHUB_EVENT_PATH', event_file);
end
builder.redirectErrorStream(true);
builder.redirectOutput(java.io.File(fullfile(output_dir, ['mcp-' mode '-harness.log'])));
process = builder.start();
cleanup = onCleanup(@() process.destroy());
started = tic;
while process.isAlive()
    % Yield to MATLAB's connector event queue while the external MCP client runs.
    drawnow;
    pause(0.1);
    if toc(started) > 300
        error('eegmcp:test', 'Official MCP request timed out in the cloud MATLAB session.');
    end
end
result = jsondecode(fileread(output));
if process.exitValue() ~= 0 || ~strcmp(result.status, 'success')
    error('eegmcp:test', 'Official MCP harness failed: %s', jsonencode(result));
end
fprintf('ok: official MathWorks MCP transport, mode=%s, tools=%d\n', mode, result.custom_tool_count);
clear cleanup
end
