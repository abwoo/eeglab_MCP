function run_eegmcp_cloud_suite(eeglab_root, binary, toolbox)
%RUN_EEGMCP_CLOUD_SUITE Run independent suites and retain every failure.
stages = {'run_eegmcp_gate_tests', 'run_eegmcp_tests', 'run_eegmcp_b1_tests', ...
    'run_eegmcp_b2_tests', 'run_eegmcp_b3_tests', 'run_eegmcp_research_tests'};
failures = {};
for k = 1:numel(stages)
    try
        if k == 1
            feval(stages{k});
        else
            feval(stages{k}, eeglab_root);
        end
    catch err
        failures{end + 1} = [stages{k} ': ' getReport(err, 'extended', 'hyperlinks', 'off')]; %#ok<AGROW>
        fprintf(2, '%s\n', failures{end});
    end
end
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
for mode = {'live', 'request'}
    try
        init = eegmcp_call_tool('eegmcp_init(%s)', eeglab_root);
        assert(strcmp(init.status, 'success'), 'Cloud MATLAB initialization failed.');
        loaded = eegmcp_call_tool('eegmcp_load_data(%s)', fullfile(eeglab_root, 'sample_data', 'eeglab_data.set'));
        assert(strcmp(loaded.status, 'success'), 'Cloud MATLAB sample loading failed.');
        if strcmp(mode{1}, 'request')
            run_eegmcp_cloud_mcp(binary, toolbox, eeglab_root, 'request', ...
                fullfile(root, 'matlab', 'tests', 'fixtures', 'cloud-event.json'));
        else
            run_eegmcp_cloud_mcp(binary, toolbox, eeglab_root);
        end
    catch err
        failures{end + 1} = [mode{1} ': ' getReport(err, 'extended', 'hyperlinks', 'off')]; %#ok<AGROW>
        fprintf(2, '%s\n', failures{end});
    end
end
if ~isempty(failures)
    error('eegmcp:test', '%d independent cloud suites failed. See the failures above.', numel(failures));
end
fprintf('All MATLAB suites and official MCP cloud requests passed.\n');
end
