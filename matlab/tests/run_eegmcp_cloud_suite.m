function run_eegmcp_cloud_suite(eeglab_root)
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
if ~isempty(failures)
    error('eegmcp:test', '%d independent cloud suites failed. See the failures above.', numel(failures));
end
fprintf('All native MATLAB suites passed.\n');
end
