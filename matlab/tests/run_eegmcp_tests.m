function run_eegmcp_tests(eeglab_root)
%RUN_EEGMCP_TESTS Call each MCP tool function and check the JSON it prints.
%   RUN_EEGMCP_TESTS(EEGLAB_ROOT) runs the tools against EEGLAB's sample
%   dataset (sample_data/eeglab_data.set) and errors on the first failure.

addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');

r = eegmcp_call_tool('eegmcp_init(%s)', eeglab_root);
eegmcp_check(strcmp(r.status, 'success'), 'eeglab_init succeeds', r);
eegmcp_check(~isempty(r.eeglab_version), 'eeglab_init reports a version', r);

r = eegmcp_call_tool('eegmcp_init(%s)', fullfile(tempdir, 'no_such_eeglab'));
eegmcp_check(strcmp(r.code, 'eeglab_path_not_found'), 'eeglab_init rejects a missing folder', r);

r = eegmcp_call_tool('eegmcp_info()');
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_info needs a loaded dataset', r);

r = eegmcp_call_tool('eegmcp_load_data(%s)', fullfile(tempdir, 'missing.set'));
eegmcp_check(strcmp(r.code, 'file_not_found'), 'eeglab_load_data rejects a missing file', r);

r = eegmcp_call_tool('eegmcp_load_data(%s)', sample);
eegmcp_check(strcmp(r.status, 'success'), 'eeglab_load_data loads the sample', r);
eegmcp_check(r.nbchan == 32 && r.srate == 128 && r.num_events == 154, 'sample has 32 channels, 128 Hz, 154 events', r);
eegmcp_check(numel(r.channel_labels) == 32, 'eeglab_load_data lists 32 channel labels', r);

r = eegmcp_call_tool('eegmcp_info()');
eegmcp_check(strcmp(r.status, 'success') && r.pnts == 30504, 'eeglab_info describes the sample', r);
eegmcp_check(strcmp(r.data_shape, 'continuous_or_single_trial'), 'sample is continuous', r);

r = eegmcp_call_tool('eegmcp_get_events()');
eegmcp_check(isequal(sort(r.event_types(:))', {'rt', 'square'}), 'event types are rt and square', r);
counts = containers.Map({r.event_counts.type}, {r.event_counts.count});
eegmcp_check(counts('square') == 80 && counts('rt') == 74, 'event counts are square 80, rt 74', r);

r = eegmcp_call_tool('eegmcp_qc_report()');
eegmcp_check(strcmp(r.status, 'success') && r.summary.nbchan == 32, 'eeglab_qc_report summarizes the sample', r);
eegmcp_check(iscell(r.risk_hints) || isempty(r.risk_hints), 'eeglab_qc_report lists risk hints', r);

% Numeric event types, common in imported files, must not break the tools.
global EEG
for k = 1:numel(EEG.event)
    EEG.event(k).type = 7;
end
r = eegmcp_call_tool('eegmcp_get_events()');
eegmcp_check(strcmp(r.status, 'success') && isequal(r.event_types, {'7'}), 'numeric event types are reported as text', r);

fprintf('All eegmcp tool tests passed.\n');
end
