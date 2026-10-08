function run_eegmcp_tests(eeglab_root)
%RUN_EEGMCP_TESTS Call each MCP tool function and check the JSON it prints.
%   RUN_EEGMCP_TESTS(EEGLAB_ROOT) runs the tools against EEGLAB's sample
%   dataset (sample_data/eeglab_data.set) and errors on the first failure.

addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');

r = call_tool('eegmcp_init(%s)', eeglab_root);
check(strcmp(r.status, 'success'), 'eeglab_init succeeds', r);
check(~isempty(r.eeglab_version), 'eeglab_init reports a version', r);

r = call_tool('eegmcp_init(%s)', fullfile(tempdir, 'no_such_eeglab'));
check(strcmp(r.code, 'eeglab_path_not_found'), 'eeglab_init rejects a missing folder', r);

r = call_tool('eegmcp_info()');
check(strcmp(r.code, 'no_dataset'), 'eeglab_info needs a loaded dataset', r);

r = call_tool('eegmcp_load_data(%s)', fullfile(tempdir, 'missing.set'));
check(strcmp(r.code, 'file_not_found'), 'eeglab_load_data rejects a missing file', r);

r = call_tool('eegmcp_load_data(%s)', sample);
check(strcmp(r.status, 'success'), 'eeglab_load_data loads the sample', r);
check(r.nbchan == 32 && r.srate == 128 && r.num_events == 154, 'sample has 32 channels, 128 Hz, 154 events', r);
check(numel(r.channel_labels) == 32, 'eeglab_load_data lists 32 channel labels', r);

r = call_tool('eegmcp_info()');
check(strcmp(r.status, 'success') && r.pnts == 30504, 'eeglab_info describes the sample', r);
check(strcmp(r.data_shape, 'continuous_or_single_trial'), 'sample is continuous', r);

r = call_tool('eegmcp_get_events()');
check(isequal(sort(r.event_types(:))', {'rt', 'square'}), 'event types are rt and square', r);
counts = containers.Map({r.event_counts.type}, {r.event_counts.count});
check(counts('square') == 80 && counts('rt') == 74, 'event counts are square 80, rt 74', r);

r = call_tool('eegmcp_qc_report()');
check(strcmp(r.status, 'success') && r.summary.nbchan == 32, 'eeglab_qc_report summarizes the sample', r);
check(iscell(r.risk_hints) || isempty(r.risk_hints), 'eeglab_qc_report lists risk hints', r);

% Numeric event types, common in imported files, must not break the tools.
global EEG
for k = 1:numel(EEG.event)
    EEG.event(k).type = 7;
end
r = call_tool('eegmcp_get_events()');
check(strcmp(r.status, 'success') && isequal(r.event_types, {'7'}), 'numeric event types are reported as text', r);

fprintf('All eegmcp tool tests passed.\n');
end

function result = call_tool(template, varargin)
% Run a tool call, capture its command window output and decode the JSON.
args = cellfun(@(a) ['"' strrep(a, '"', '""') '"'], varargin, 'UniformOutput', false);
command = sprintf(template, args{:});
output = evalc(command);
start = strfind(output, '{');
if isempty(start)
    error('eegmcp:test', '%s printed no JSON:\n%s', command, output);
end
result = jsondecode(output(start(1):end));
end

function check(condition, name, result)
if ~condition
    error('eegmcp:test', 'FAILED: %s\n%s', name, jsonencode(result, 'PrettyPrint', true));
end
fprintf('ok: %s\n', name);
end
