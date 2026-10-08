function run_eegmcp_b1_tests(eeglab_root)
%RUN_EEGMCP_B1_TESTS Tests of the data and preprocessing tools (batch b1).
%   RUN_EEGMCP_B1_TESTS(EEGLAB_ROOT) runs eeglab_save_data, import_bids,
%   history, filter, resample, reref, select_channels,
%   interpolate_channels, edit_channels, clean_line_noise and
%   clean_rawdata against EEGLAB's sample dataset and errors on the first
%   failure.

global EEG
addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');
locs = fullfile(eeglab_root, 'sample_data', 'eeglab_chan32.locs');
out_dir = fullfile(tempdir, 'eegmcp_b1_tests');
override = {'override_gate', true, 'override_reason', 'CI test'};
outputs_ok = struct('raw_input_preserved', true, 'derivative_output_planned', true);

r = eegmcp_call_tool('eegmcp_init(%s)', eeglab_root);
eegmcp_check(strcmp(r.status, 'success'), 'eeglab_init succeeds', r);

% ---- no dataset ----------------------------------------------------------
EEG = [];
r = eegmcp_call_tool('eegmcp_history()');
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_history needs a dataset', r);
r = call('eegmcp_filter', 'filter_type', 'highpass', 'low_cutoff', 1, override{:});
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_filter needs a dataset', r);
r = call('eegmcp_reref', 'ref_type', 'average', override{:});
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_reref needs a dataset', r);
r = call('eegmcp_interpolate_channels', 'method', 'spherical', override{:});
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_interpolate_channels needs a dataset', r);
r = call('eegmcp_edit_channels', 'action', 'load_loc', 'loc_file', locs, override{:});
eegmcp_check(strcmp(r.code, 'no_dataset'), 'eeglab_edit_channels needs a dataset', r);


% ---- history ---------------------------------------------------------------
load_sample(sample);
r = eegmcp_call_tool('eegmcp_history()');
eegmcp_check(strcmp(r.status, 'success') && isnumeric(r.num_entries), 'eeglab_history reads the history', r);

% ---- filter ----------------------------------------------------------------
r = eegmcp_call_tool('eegmcp_filter(%s)', '{}');
eegmcp_check(strcmp(r.code, 'missing_required_argument'), 'eeglab_filter needs filter_type', r);
r = call('eegmcp_filter', 'filter_type', 'bandpass', 'low_cutoff', 1);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_filter bandpass needs high_cutoff', r);
r = call('eegmcp_filter', 'filter_type', 'bandpass', 'low_cutoff', 40, 'high_cutoff', 1, override{:});
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_filter rejects reversed cutoffs', r);
r = call('eegmcp_filter', 'filter_type', 'comb');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_filter rejects an unknown filter_type', r);
r = call('eegmcp_filter', 'filter_type', 'highpass', 'low_cutoff', 1, 'override_gate', true);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'override_gate needs override_reason', r);
r = call('eegmcp_filter', 'filter_type', 'bandpass', 'low_cutoff', 1, 'high_cutoff', 40);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_filter is gate-blocked without context', r);
r = call('eegmcp_filter', 'filter_type', 'lowpass', 'high_cutoff', 100, override{:});
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_filter rejects a cutoff above Nyquist', r);
r = call('eegmcp_filter', 'filter_type', 'bandpass', 'low_cutoff', 1, 'high_cutoff', 40, override{:});
eegmcp_check(strcmp(r.status, 'success') && r.override_used, 'eeglab_filter bandpass runs with an override', r);
eegmcp_check(r.low_cutoff == 1 && r.high_cutoff == 40 && r.nbchan == 32, 'eeglab_filter reports the cutoffs', r);
r = call('eegmcp_filter', 'filter_type', 'highpass', 'low_cutoff', 0.5, 'method_context', outputs_ok);
eegmcp_check(strcmp(r.status, 'success') && ~strcmp(r.official_gate.gate_status, 'blocked'), ...
    'eeglab_filter highpass passes the gate with method_context', r);
r = eegmcp_call_tool('eegmcp_history()');
eegmcp_check(r.num_entries >= 2 && contains(r.history_text, 'pop_eegfiltnew'), 'eeglab_history lists the filters', r);

% ---- resample --------------------------------------------------------------
load_sample(sample);
r = call('eegmcp_resample', 'new_srate', -1);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_resample rejects a negative rate', r);
r = call('eegmcp_resample', 'new_srate', 64);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_resample is gate-blocked without context', r);
r = call('eegmcp_resample', 'new_srate', 64, override{:});
eegmcp_check(strcmp(r.status, 'success') && r.new_srate == 64 && r.old_srate == 128, ...
    'eeglab_resample resamples to 64 Hz', r);
eegmcp_check(EEG.srate == 64, 'the resampled dataset is the current dataset', r);

% ---- reref -----------------------------------------------------------------
load_sample(sample);
r = call('eegmcp_reref', 'ref_type', 'channel');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_reref channel needs ref_channel', r);
r = call('eegmcp_reref', 'ref_type', 'average');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_reref is gate-blocked without context', r);
r = call('eegmcp_reref', 'ref_type', 'channel', 'ref_channel', 'NoSuchChannel', override{:});
eegmcp_check(strcmp(r.code, 'unknown_channels'), 'eeglab_reref rejects an unknown channel', r);
r = call('eegmcp_reref', 'ref_type', 'average', override{:});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32, 'eeglab_reref average keeps 32 channels', r);
r = call('eegmcp_reref', 'ref_type', 'channel', 'ref_channel', 'Cz', override{:});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 31, 'eeglab_reref to Cz removes Cz', r);

% ---- select_channels -------------------------------------------------------
load_sample(sample);
r = call('eegmcp_select_channels', 'channels', {'Fz'}, 'exclude_channels', {'Cz'});
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_select_channels needs exactly one list', r);
r = eegmcp_call_tool('eegmcp_select_channels(%s)', '');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_select_channels needs a list', r);
r = call('eegmcp_select_channels', 'channels', {'Fz', 'NoSuchChannel'});
eegmcp_check(strcmp(r.code, 'unknown_channels'), 'eeglab_select_channels rejects unknown labels', r);
r = call('eegmcp_select_channels', 'channels', {'Fz', 'Cz', 'Pz'});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 3, 'eeglab_select_channels keeps 3 channels', r);
load_sample(sample);
r = call('eegmcp_select_channels', 'exclude_channels', {'EOG1', 'EOG2'});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 30 && ~any(strcmp(r.channel_labels, 'EOG1')), ...
    'eeglab_select_channels removes the EOG channels', r);

% ---- interpolate_channels --------------------------------------------------
load_sample(sample);
r = call('eegmcp_select_channels', 'exclude_channels', {'Cz', 'Pz'});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 30, 'two channels removed before interpolation', r);
r = eegmcp_call_tool('eegmcp_interpolate_channels(%s)', '');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_interpolate_channels is gate-blocked without context', r);
r = call('eegmcp_interpolate_channels', 'method', 'nearest');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_interpolate_channels rejects an unknown method', r);
r = call('eegmcp_interpolate_channels', 'ref_chanlocs', 'urchanlocs');
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32, 'eeglab_interpolate_channels restores 32 channels', r);
eegmcp_check(all(ismember({'Cz', 'Pz'}, r.channel_labels)), 'Cz and Pz are back', r);
r = call('eegmcp_interpolate_channels', 'ref_chanlocs', 'urchanlocs');
eegmcp_check(strcmp(r.code, 'nothing_to_interpolate'), 'nothing is left to interpolate', r);
load_sample(sample);
call('eegmcp_select_channels', 'exclude_channels', {'Oz'});
r = call('eegmcp_interpolate_channels', 'ref_chanlocs', locs, 'method', 'spherical');
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32 && any(strcmp(r.interpolated_channels, 'Oz')), ...
    'eeglab_interpolate_channels interpolates from a location file', r);

% ---- edit_channels ---------------------------------------------------------
load_sample(sample);
r = call('eegmcp_edit_channels', 'action', 'load_loc');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_edit_channels load_loc needs loc_file', r);
r = call('eegmcp_edit_channels', 'action', 'rename', 'rename_map', struct('Cz', ''));
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_edit_channels rejects an empty new label', r);
r = call('eegmcp_edit_channels', 'action', 'load_loc', 'loc_file', fullfile(tempdir, 'missing.locs'));
eegmcp_check(strcmp(r.code, 'file_not_found'), 'eeglab_edit_channels rejects a missing file', r);
r = call('eegmcp_edit_channels', 'action', 'load_loc', 'loc_file', locs);
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32 && r.has_channel_locations, ...
    'eeglab_edit_channels loads a location file', r);
r = call('eegmcp_edit_channels', 'action', 'rename', 'rename_map', struct('Cz', 'Vertex', 'Fz', 'FrontalZ'));
eegmcp_check(strcmp(r.status, 'success') && any(strcmp(r.channel_labels, 'Vertex')) && ...
    ~any(strcmp(r.channel_labels, 'Cz')), 'eeglab_edit_channels renames channels', r);
r = call('eegmcp_edit_channels', 'action', 'rename', 'rename_map', struct('NoSuchChannel', 'X'));
eegmcp_check(strcmp(r.code, 'unknown_channels'), 'eeglab_edit_channels rejects an unknown label', r);

% ---- clean_line_noise (on a 60 s crop to keep CleanLine short) -------------
load_sample(sample);
evalc('EEG = pop_select(EEG, ''time'', [0 60]);');
r = eegmcp_call_tool('eegmcp_clean_line_noise(%s)', '');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_clean_line_noise is gate-blocked without context', r);
r = call('eegmcp_clean_line_noise', 'line_freq', 100, override{:});
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_clean_line_noise rejects line_freq above Nyquist', r);
r = call('eegmcp_clean_line_noise', 'line_freq', 50, 'bandwidth', 2, ...
    'method_context', struct('derivative_output_planned', true));
eegmcp_check(strcmp(r.status, 'success') && r.line_freq == 50 && ~strcmp(r.official_gate.gate_status, 'blocked'), ...
    'eeglab_clean_line_noise runs with recorded parameters', r);
r = call('eegmcp_filter', 'filter_type', 'notch', 'notch_freq', 50, override{:});
eegmcp_check(strcmp(r.status, 'success') && isequal(r.notch_freqs(:)', 50), ...
    'eeglab_filter notch keeps only frequencies below Nyquist', r);

% ---- clean_rawdata ---------------------------------------------------------
load_sample(sample);
r = eegmcp_call_tool('eegmcp_clean_rawdata(%s)', '');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_clean_rawdata is gate-blocked without context', r);
r = call('eegmcp_clean_rawdata', 'burst_criterion', -5, override{:});
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_clean_rawdata rejects a negative criterion', r);
r = call('eegmcp_clean_rawdata', 'burst_criterion', 20, override{:});
eegmcp_check(strcmp(r.status, 'success') && r.nbchan <= 32 && r.pnts <= 30504 && r.burst_criterion == 20, ...
    'eeglab_clean_rawdata runs ASR', r);

% ---- save_data -------------------------------------------------------------
load_sample(sample);
r = eegmcp_call_tool('eegmcp_save_data(%s)', '{}');
eegmcp_check(strcmp(r.code, 'missing_required_argument'), 'eeglab_save_data needs filepath', r);
r = call('eegmcp_save_data', 'filepath', fullfile(out_dir, 'bad.txt'));
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_save_data writes only .set files', r);
target = fullfile(out_dir, 'sample_copy.set');
r = call('eegmcp_save_data', 'filepath', target);
eegmcp_check(strcmp(r.status, 'success') && isfile(target), 'eeglab_save_data writes a .set file', r);
r = call('eegmcp_save_data', 'filepath', out_dir, 'filename', 'sample_named.set');
eegmcp_check(strcmp(r.status, 'success') && isfile(fullfile(out_dir, 'sample_named.set')), ...
    'eeglab_save_data writes filename into the folder', r);
r = eegmcp_call_tool('eegmcp_load_data(%s)', target);
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32, 'the saved file loads back', r);

% ---- import_bids (no BIDS dataset in CI) -----------------------------------
r = eegmcp_call_tool('eegmcp_import_bids(%s)', '{}');
eegmcp_check(strcmp(r.code, 'missing_required_argument'), 'eeglab_import_bids needs bids_path', r);
r = call('eegmcp_import_bids', 'bids_path', tempdir);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_import_bids is gate-blocked without plugin context', r);
r = call('eegmcp_import_bids', 'bids_path', fullfile(tempdir, 'no_such_bids_folder'), override{:});
eegmcp_check(strcmp(r.code, 'bids_path_not_found'), 'eeglab_import_bids rejects a missing folder', r);
r = call('eegmcp_import_bids', 'bids_path', fullfile(tempdir, 'no_such_bids_folder'), ...
    'method_context', struct('plugins_available', {{'EEG-BIDS'}}));
eegmcp_check(strcmp(r.code, 'bids_path_not_found'), 'plugin context passes the eeglab_import_bids gate', r);

fprintf('All b1 tool tests passed.\n');
end

function r = call(tool, varargin)
% Call TOOL with options built from name/value pairs, encoded as JSON.
opts = struct();
for k = 1:2:numel(varargin)
    opts.(varargin{k}) = varargin{k + 1};
end
r = eegmcp_call_tool([tool '(%s)'], jsonencode(opts));
end

function load_sample(sample)
r = eegmcp_call_tool('eegmcp_load_data(%s)', sample);
eegmcp_check(strcmp(r.status, 'success') && r.nbchan == 32, 'sample dataset loads', r);
end
