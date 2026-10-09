function run_eegmcp_b2_tests(eeglab_root)
%RUN_EEGMCP_B2_TESTS Test the ICA, artifact, epoch and ERP tools on the EEGLAB sample dataset.
%   RUN_EEGMCP_B2_TESTS(EEGLAB_ROOT) covers eeglab_run_ica,
%   eeglab_classify_ica, eeglab_flag_components, eeglab_remove_components,
%   eeglab_reject_epochs, eeglab_epoch, eeglab_erp_analysis,
%   eeglab_sort_epochs and eeglab_average_erp. ICA is kept fast with a
%   4-component PCA reduction and a small step limit.

addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');

r = eegmcp_call_tool('eegmcp_init(%s)', eeglab_root);
eegmcp_check(strcmp(r.status, 'success'), 'eeglab_init succeeds', r);
load_sample(sample);

% ---------------------------------------------------------------- ICA
r = eegmcp_call_tool('eegmcp_run_ica(%s)', '');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_run_ica is gated without method_context', r);

r = eegmcp_call_tool('eegmcp_run_ica(%s)', '{"algorithm":"fastica"}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_run_ica rejects an unknown algorithm', r);

r = eegmcp_call_tool('eegmcp_run_ica(%s)', '{"max_steps":0}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_run_ica rejects max_steps 0', r);

r = eegmcp_call_tool('eegmcp_run_ica(%s)', '{"override_gate":true}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'override_gate needs override_reason', r);

if exist('picard', 'file') ~= 2
    r = eegmcp_call_tool('eegmcp_run_ica(%s)', ...
        '{"algorithm":"picard","override_gate":true,"override_reason":"CI test"}');
    eegmcp_check(is_code(r, 'plugin_missing'), 'eeglab_run_ica reports a missing picard plugin', r);
end

r = eegmcp_call_tool('eegmcp_run_ica(%s)', ['{"pca_components":4,"max_steps":64,' ...
    '"method_context":{"data_shape":"continuous","bad_channel_policy_defined":true}}']);
eegmcp_check(is_success(r) && r.ncomponents == 4, 'eeglab_run_ica computes 4 components', r);
eegmcp_check(strcmp(r.official_gate.gate_status, 'pass'), 'eeglab_run_ica gate passes with context', r);

r = eegmcp_call_tool('eegmcp_info()');
eegmcp_check(r.ica_computed, 'the ICA weights are stored in the current dataset', r);

% ---------------------------------------------------------------- ICLabel
r = eegmcp_call_tool('eegmcp_classify_ica(%s)', '');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_classify_ica is gated without method_context', r);

r = eegmcp_call_tool('eegmcp_classify_ica(%s)', ...
    '{"method_context":{"has_ica":true,"plugins_available":["ICLabel"]}}');
eegmcp_check(is_success(r) && r.n_components == 4, 'eeglab_classify_ica labels 4 components', r);
eegmcp_check(ischar(r.classifications.comp_1.predicted_class), 'eeglab_classify_ica predicts a class', r);

r = eegmcp_call_tool('eegmcp_flag_components(%s)', '{"brain_range":[0.5,0.2]}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_flag_components rejects a reversed range', r);

r = eegmcp_call_tool('eegmcp_flag_components(%s)', '{"eye_range":[0.8,1]}');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_flag_components is gated without method_context', r);

r = eegmcp_call_tool('eegmcp_flag_components(%s)', ...
    '{"brain_range":[0,0.2],"eye_range":[0.8,1],"override_gate":true,"override_reason":"CI test"}');
eegmcp_check(is_success(r) && r.num_flagged >= 0 && r.num_flagged <= 4, 'eeglab_flag_components flags components', r);
eegmcp_check(r.override_used, 'eeglab_flag_components records the override', r);

% ---------------------------------------------------------------- remove components
r = eegmcp_call_tool('eegmcp_remove_components(%s)', '{"component_indices":[1]}');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_remove_components is gated without method_context', r);

r = eegmcp_call_tool('eegmcp_remove_components(%s)', '{"component_indices":[1],"auto_remove_brain_threshold":0.3}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_remove_components needs exactly one selection', r);

context = '"method_context":{"has_ica":true,"component_reviewed":true,"derivative_output_planned":true}';
r = eegmcp_call_tool('eegmcp_remove_components(%s)', ['{"component_indices":[9],' context '}']);
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_remove_components rejects a missing component', r);

r = eegmcp_call_tool('eegmcp_remove_components(%s)', ['{"auto_remove_brain_threshold":0,' context '}']);
eegmcp_check(is_success(r) && r.num_removed == 0, 'a zero Brain threshold removes nothing', r);

r = eegmcp_call_tool('eegmcp_remove_components(%s)', ['{"component_indices":[1],' context '}']);
eegmcp_check(is_success(r) && r.num_removed == 1 && r.remaining_channels == 32, ...
    'eeglab_remove_components removes component 1', r);

% ---------------------------------------------------------------- epoching
load_sample(sample);
r = eegmcp_call_tool('eegmcp_reject_epochs(%s)', '{"override_gate":true,"override_reason":"CI test"}');
eegmcp_check(is_code(r, 'not_epoched'), 'eeglab_reject_epochs needs epoched data', r);

r = eegmcp_call_tool('eegmcp_epoch(%s)', '{"event_types":["square"]}');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_epoch is gated without confirmed condition events', r);

r = eegmcp_call_tool('eegmcp_epoch(%s)', '{"baseline_start":-0.5}');
eegmcp_check(is_code(r, 'invalid_analysis_window'), 'eeglab_epoch rejects a baseline outside the epoch', r);

r = eegmcp_call_tool('eegmcp_epoch(%s)', ['{"event_types":["square"],"pre_stimulus":-0.2,' ...
    '"post_stimulus":0.8,"method_context":{"confirmed_condition_events":true}}']);
eegmcp_check(is_success(r) && r.trials >= 70 && r.trials <= 80, 'eeglab_epoch cuts the square epochs', r);
eegmcp_check(abs(r.xmin + 0.2) < 0.01 && r.baseline_applied(2) <= 0, 'eeglab_epoch applies the baseline', r);
ntrials = r.trials;

% ---------------------------------------------------------------- ERP summaries
r = eegmcp_call_tool('eegmcp_erp_analysis(%s)', '{"time_window":[450,250]}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_erp_analysis rejects a reversed time_window', r);

r = eegmcp_call_tool('eegmcp_erp_analysis(%s)', '{"channels":["NoSuchChannel"]}');
eegmcp_check(is_code(r, 'unknown_channels'), 'eeglab_erp_analysis rejects unknown channels', r);

r = eegmcp_call_tool('eegmcp_erp_analysis(%s)', '{"channels":["Cz","Pz"],"time_window":[250,450]}');
eegmcp_check(is_success(r) && numel(r.mean_amplitude) == 2 && isfield(r.peaks, 'Pz'), ...
    'eeglab_erp_analysis reports amplitudes and peaks', r);
latency = r.peaks.Pz.positive_peak_latency;
eegmcp_check(latency >= 250 && latency <= 450, 'peak latency lies inside time_window', r);

r = eegmcp_call_tool('eegmcp_erp_analysis(%s)', ...
    '{"channels":["Cz"],"time_window":[250,450],"conditions":["square","rt"]}');
eegmcp_check(is_success(r) && r.erp.square.num_trials == ntrials && r.erp.rt.num_trials == 0, ...
    'eeglab_erp_analysis groups trials by time-locking event', r);
eegmcp_check(isfield(r.erp.square, 'peaks'), 'eeglab_erp_analysis reports peaks per condition', r);

r = eegmcp_call_tool('eegmcp_average_erp(%s)', '');
eegmcp_check(is_success(r) && r.num_trials == ntrials && numel(r.mean_amplitude) == 32, ...
    'eeglab_average_erp averages all trials and channels', r);

r = eegmcp_call_tool('eegmcp_average_erp(%s)', '{"conditions":["square"],"channels":["Cz","Fz"]}');
eegmcp_check(is_success(r) && r.erp.square.num_trials == ntrials && numel(r.erp.square.mean_amplitude) == 2, ...
    'eeglab_average_erp averages by condition', r);

% ---------------------------------------------------------------- trial rejection
r = eegmcp_call_tool('eegmcp_reject_epochs(%s)', '{}');
eegmcp_check(is_code(r, 'official_gate_blocked'), 'eeglab_reject_epochs is gated without method_context', r);

r = eegmcp_call_tool('eegmcp_reject_epochs(%s)', '{"method":"median"}');
eegmcp_check(is_code(r, 'invalid_arguments'), 'eeglab_reject_epochs rejects an unknown method', r);

reject_context = '"method_context":{"raw_input_preserved":true,"derivative_output_planned":true}';
r = eegmcp_call_tool('eegmcp_reject_epochs(%s)', ['{"threshold":[-1000,1000],' reject_context '}']);
eegmcp_check(is_success(r) && r.trials_before == ntrials && ...
    r.remaining_trials == ntrials - r.num_rejected, 'eeglab_reject_epochs rejects by threshold', r);
eegmcp_check(strcmp(r.official_gate.gate_status, 'pass'), 'eeglab_reject_epochs gate passes with context', r);
ntrials = r.remaining_trials;

r = eegmcp_call_tool('eegmcp_reject_epochs(%s)', ...
    '{"method":"joint_probability","jp_threshold":5,"channels":["Cz","Pz"],"override_gate":true,"override_reason":"CI test"}');
eegmcp_check(is_success(r) && r.remaining_trials == ntrials - r.num_rejected && r.remaining_trials > 0, ...
    'eeglab_reject_epochs rejects by joint probability', r);

% ---------------------------------------------------------------- sorting
r = eegmcp_call_tool('eegmcp_sort_epochs(%s)', '');
eegmcp_check(is_code(r, 'missing_required_argument'), 'eeglab_sort_epochs needs sort_by', r);

load_sample(sample);
r = eegmcp_call_tool('eegmcp_sort_epochs(%s)', '{"sort_by":"type"}');
eegmcp_check(is_code(r, 'not_epoched'), 'eeglab_sort_epochs needs epoched data', r);

r = eegmcp_call_tool('eegmcp_epoch(%s)', ['{"event_types":["square","rt"],' ...
    '"method_context":{"confirmed_condition_events":true}}']);
eegmcp_check(is_success(r) && r.trials > 80, 'eeglab_epoch cuts square and rt epochs', r);
ntrials = r.trials;

r = eegmcp_call_tool('eegmcp_sort_epochs(%s)', '{"sort_by":"no_such_field"}');
eegmcp_check(is_code(r, 'unknown_field'), 'eeglab_sort_epochs rejects an unknown event field', r);

r = eegmcp_call_tool('eegmcp_sort_epochs(%s)', '{"sort_by":"type"}');
eegmcp_check(is_success(r) && r.trials == ntrials && issorted(r.sorted_values), ...
    'eeglab_sort_epochs orders epochs by type', r);
eegmcp_check(strcmp(r.sorted_values{1}, 'rt') && strcmp(r.sorted_values{end}, 'square'), ...
    'rt epochs come before square epochs', r);

global EEG
eegmcp_check(strcmp(time_locking_type(EEG.epoch(1)), 'rt') && strcmp(time_locking_type(EEG.epoch(end)), 'square'), ...
    'the dataset epochs are reordered', struct('trials', EEG.trials));

r = eegmcp_call_tool('eegmcp_average_erp(%s)', '{"conditions":["rt","square"],"channels":["Cz"]}');
eegmcp_check(is_success(r) && r.erp.rt.num_trials + r.erp.square.num_trials == ntrials, ...
    'eeglab_average_erp splits the sorted trials by condition', r);

fprintf('All b2 tool tests passed.\n');
end

function load_sample(sample)
r = eegmcp_call_tool('eegmcp_load_data(%s)', sample);
eegmcp_check(strcmp(r.status, 'success'), 'the sample dataset loads', r);
end

function ok = is_success(r)
ok = isfield(r, 'status') && strcmp(r.status, 'success');
end

function ok = is_code(r, code)
ok = isfield(r, 'status') && strcmp(r.status, 'error') && isfield(r, 'code') && strcmp(r.code, code);
end

function value = time_locking_type(epoch)
value = epoch.eventtype;
if iscell(value)
    latencies = epoch.eventlatency;
    pick = find(cellfun(@(v) abs(v) < 1e-6, latencies), 1);
    if isempty(pick)
        pick = 1;
    end
    value = value{pick};
end
end
