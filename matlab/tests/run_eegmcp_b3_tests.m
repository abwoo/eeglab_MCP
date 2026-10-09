function run_eegmcp_b3_tests(eeglab_root)
%RUN_EEGMCP_B3_TESTS Check the spectral, time-frequency, connectivity, plotting and source tools.
%   RUN_EEGMCP_B3_TESTS(EEGLAB_ROOT) runs the tools against EEGLAB's sample
%   dataset. Epochs and a small ICA are prepared directly with EEGLAB
%   (pop_epoch, pop_runica) on the shared global EEG. Figures are written
%   to a folder under tempdir and checked on disk.

global EEG ALLEEG CURRENTSET %#ok<GVMIS> the tools share EEGLAB's globals

addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');
out = strrep(fullfile(tempdir, 'eegmcp_b3_figures'), '\', '/');
override = '"override_gate":true,"override_reason":"CI test"';

r = eegmcp_call_tool('eegmcp_init(%s)', eeglab_root);
eegmcp_check(strcmp(r.status, 'success'), 'eeglab_init succeeds', r);
r = eegmcp_call_tool('eegmcp_load_data(%s)', sample);
eegmcp_check(strcmp(r.status, 'success'), 'sample loads', r);

% ---- eeglab_spectral (continuous data) ----
r = eegmcp_call_tool('eegmcp_spectral(%s)', '');
eegmcp_check(strcmp(r.status, 'error') && strcmp(r.code, 'official_gate_blocked'), ...
    'eeglab_spectral is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_spectral(%s)', '{"freq_range":[40,1]}');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_spectral rejects a descending freq_range', r);
r = eegmcp_call_tool('eegmcp_spectral(%s)', ['{"channels":["Oz","Pz"],"freq_range":[1,40],' ...
    '"method_context":{"artifact_policy":"none, CI sample"}}']);
eegmcp_check(strcmp(r.status, 'success') && strcmp(r.official_gate.gate_status, 'pass'), ...
    'eeglab_spectral passes the gate with a recorded context', r);
eegmcp_check(numel(r.channels) == 2 && isfield(r.band_power, 'alpha') && ...
    r.band_power.alpha.absolute_power > 0, 'eeglab_spectral reports alpha band power', r);
eegmcp_check(~isfield(r.band_power, 'gamma') || r.band_power.gamma.freq_range(1) == 30, ...
    'eeglab_spectral keeps the band definitions', r);
r = eegmcp_call_tool('eegmcp_spectral(%s)', ['{' override '}']);
eegmcp_check(strcmp(r.status, 'success') && numel(r.channels) == 32 && r.override_used, ...
    'eeglab_spectral runs on all channels with an override', r);
eegmcp_check(~isempty(r.warnings), 'eeglab_spectral warns that 100 Hz is above Nyquist', r);
r = eegmcp_call_tool('eegmcp_spectral(%s)', ['{"channels":["NoSuch"],' override '}']);
eegmcp_check(strcmp(r.code, 'unknown_channels'), 'eeglab_spectral rejects unknown channels', r);

% ---- eeglab_connectivity (continuous data) ----
r = eegmcp_call_tool('eegmcp_connectivity(%s)', '');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_connectivity is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_connectivity(%s)', ['{"channels":["Cz","Pz","Oz","Fz"],' ...
    '"method":"coherence","freq_range":[8,13],' override '}']);
eegmcp_check(strcmp(r.status, 'success') && r.n_pairs == 6 && r.mean_connectivity >= 0 && ...
    r.max_connectivity <= 1 + 1e-9, 'eeglab_connectivity computes coherence', r);
r = eegmcp_call_tool('eegmcp_connectivity(%s)', ['{"channels":["Cz","Pz","Oz"],"method":"plv",' override '}']);
eegmcp_check(strcmp(r.status, 'success') && strcmp(r.method, 'plv') && r.min_connectivity >= 0 && ...
    r.max_connectivity <= 1 + 1e-9, 'eeglab_connectivity computes PLV', r);
r = eegmcp_call_tool('eegmcp_connectivity(%s)', ['{"method":"granger",' override '}']);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_connectivity rejects an unknown method', r);

% ---- eeglab_topoplot (continuous data) ----
topo_path = [out '/topo_continuous.png'];
r = eegmcp_call_tool('eegmcp_topoplot(%s)', ['{"output_path":"' topo_path '"}']);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_topoplot is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_topoplot(%s)', '{}');
eegmcp_check(strcmp(r.code, 'missing_required_argument'), 'eeglab_topoplot needs output_path', r);
r = eegmcp_call_tool('eegmcp_topoplot(%s)', ['{"output_path":"' topo_path '","time_point":100,' ...
    '"time_window":[0,200]}']);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_topoplot rejects time_point with time_window', r);
r = eegmcp_call_tool('eegmcp_topoplot(%s)', ['{"output_path":"' topo_path '","time_window":[1000,2000],' ...
    '"title":"CI map","method_context":{"has_channel_locations":true}}']);
eegmcp_check(strcmp(r.status, 'success') && r.file_exists && isfile(topo_path) && r.n_channels == 32, ...
    'eeglab_topoplot writes a continuous-data map', r);

% ---- before epoching: tools that need epochs or ICA fail cleanly ----
r = eegmcp_call_tool('eegmcp_timefreq(%s)', ['{' override '}']);
eegmcp_check(strcmp(r.code, 'not_epoched'), 'eeglab_timefreq needs epoched data', r);
r = eegmcp_call_tool('eegmcp_plot_erp(%s)', ['{"channels":["Cz"],"output_path":"' out '/erp0.png"}']);
eegmcp_check(strcmp(r.code, 'not_epoched'), 'eeglab_plot_erp needs epoched data', r);
r = eegmcp_call_tool('eegmcp_plot_components(%s)', ['{"output_path":"' out '/ic0.png"}']);
eegmcp_check(strcmp(r.code, 'no_ica'), 'eeglab_plot_components needs ICA', r);
r = eegmcp_call_tool('eegmcp_source_localization(%s)', ['{' override '}']);
eegmcp_check(strcmp(r.code, 'no_ica'), 'eeglab_source_localization needs ICA', r);

% ---- epoch the sample directly with EEGLAB ----
evalc(['EEG = pop_epoch(EEG, {''square''}, [-1 2]); EEG = pop_rmbase(EEG, [-200 0]); ' ...
    '[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);']);
eegmcp_check(EEG.trials > 10, 'sample is epoched around square events', struct('trials', EEG.trials));

% ---- eeglab_timefreq ----
r = eegmcp_call_tool('eegmcp_timefreq(%s)', '{"channels":["Cz"]}');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_timefreq is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_timefreq(%s)', '{"baseline":[0,-200]}');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_timefreq rejects a reversed baseline', r);
r = eegmcp_call_tool('eegmcp_timefreq(%s)', ['{"channels":["Cz","Pz"],"freq_range":[4,30],' ...
    '"cycles":[3,10],"baseline":[-200,0],"method_context":{"confirmed_condition_events":true}}']);
eegmcp_check(strcmp(r.status, 'success') && strcmp(r.official_gate.gate_status, 'pass'), ...
    'eeglab_timefreq passes the gate with confirmed events', r);
eegmcp_check(r.freq_resolution > 1 && r.time_points > 1 && isfield(r.band_ersp, 'theta') && ...
    isfield(r.band_ersp.theta, 'mean_itc'), 'eeglab_timefreq reports band ERSP and ITC', r);
r = eegmcp_call_tool('eegmcp_timefreq(%s)', ['{"channels":["Oz"],"freq_range":[5,20],' ...
    '"output_type":"ersp",' override '}']);
eegmcp_check(strcmp(r.status, 'success') && ~isfield(r.band_ersp.alpha, 'mean_itc') && ...
    isfield(r, 'peak_abs_ersp'), 'eeglab_timefreq honours output_type ersp', r);

% ---- eeglab_plot_timefreq ----
tf_path = [out '/tf_cz.png'];
r = eegmcp_call_tool('eegmcp_plot_timefreq(%s)', ['{"channel":"Cz","output_path":"' tf_path '"}']);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_plot_timefreq is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_plot_timefreq(%s)', ['{"channel":"Cz","output_path":"' tf_path '",' ...
    '"plot_ersp":false,"plot_itc":false,' override '}']);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_plot_timefreq needs one panel', r);
r = eegmcp_call_tool('eegmcp_plot_timefreq(%s)', ['{"channel":"Cz","output_path":"' tf_path '",' ...
    '"title":"Cz ERSP/ITC",' override '}']);
eegmcp_check(strcmp(r.status, 'success') && r.file_exists && isfile(tf_path) && numel(r.panels) == 2, ...
    'eeglab_plot_timefreq writes ERSP and ITC images', r);

% ---- eeglab_plot_erp ----
erp_path = [out '/erp_square.png'];
r = eegmcp_call_tool('eegmcp_plot_erp(%s)', ['{"output_path":"' erp_path '"}']);
eegmcp_check(strcmp(r.code, 'missing_required_argument'), 'eeglab_plot_erp needs channels', r);
r = eegmcp_call_tool('eegmcp_plot_erp(%s)', ['{"channels":["Cz","Pz"],"conditions":["square"],' ...
    '"output_path":"' erp_path '","title":"ERP"}']);
eegmcp_check(strcmp(r.status, 'success') && r.file_exists && isfile(erp_path) && ...
    r.conditions(1).n_trials == EEG.trials, 'eeglab_plot_erp writes condition ERPs', r);
r = eegmcp_call_tool('eegmcp_plot_erp(%s)', ['{"channels":["Cz"],"conditions":["no_such_event"],' ...
    '"output_path":"' erp_path '"}']);
eegmcp_check(strcmp(r.code, 'no_trials_for_condition'), 'eeglab_plot_erp rejects a condition without epochs', r);

% ---- eeglab_topoplot (epoched data) ----
topo_path = [out '/topo_300ms.png'];
r = eegmcp_call_tool('eegmcp_topoplot(%s)', ['{"output_path":"' topo_path '","time_point":300,' ...
    '"channels":["Fz","Cz","Pz","Oz","C3","C4","P3","P4"],' override '}']);
eegmcp_check(strcmp(r.status, 'success') && isfile(topo_path) && r.n_channels == 8 && ...
    abs(r.plotted.time_point_ms - 300) < 10, 'eeglab_topoplot writes an ERP map at 300 ms', r);

% ---- small ICA directly with EEGLAB ----
evalc(['EEG = pop_runica(EEG, ''icatype'', ''runica'', ''pca'', 5, ''maxsteps'', 50); ' ...
    '[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);']);
eegmcp_check(size(EEG.icaweights, 1) == 5, 'a 5-component ICA is computed', ...
    struct('ncomp', size(EEG.icaweights, 1)));

% ---- eeglab_plot_components ----
ic_path = [out '/ic_maps.png'];
r = eegmcp_call_tool('eegmcp_plot_components(%s)', ['{"output_path":"' ic_path '","component_indices":[9]}']);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_plot_components rejects a missing component', r);
r = eegmcp_call_tool('eegmcp_plot_components(%s)', ['{"output_path":"' ic_path '","component_indices":[1,2,3],' ...
    '"title":"ICs"}']);
eegmcp_check(strcmp(r.status, 'success') && isfile(ic_path) && numel(r.components) == 3, ...
    'eeglab_plot_components writes three maps', r);
r = eegmcp_call_tool('eegmcp_plot_components(%s)', ['{"output_path":"' out '/ic_default.png"}']);
eegmcp_check(strcmp(r.status, 'success') && numel(r.components) == 5, ...
    'eeglab_plot_components defaults to every component up to 10', r);

% ---- eeglab_source_settings and eeglab_source_localization ----
r = eegmcp_call_tool('eegmcp_source_settings(%s)', '');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'eeglab_source_settings is gate-blocked without context', r);
r = eegmcp_call_tool('eegmcp_source_settings(%s)', '{"head_model":"cylinder"}');
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'eeglab_source_settings rejects an unknown head model', r);
r = eegmcp_call_tool('eegmcp_source_localization(%s)', '{"component_indices":[1]}');
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), ...
    'eeglab_source_localization is gate-blocked without context', r);
has_fieldtrip = exist('ft_dipolefitting', 'file') == 2;
r = eegmcp_call_tool('eegmcp_source_settings(%s)', ['{"head_model":"spherical","template":"mni",' override '}']);
if has_fieldtrip
    eegmcp_check(strcmp(r.status, 'success') && strcmpi(r.coordformat, 'spherical'), ...
        'eeglab_source_settings applies the spherical template', r);
else
    eegmcp_check(strcmp(r.code, 'plugin_missing'), 'eeglab_source_settings reports missing FieldTrip-lite', r);
end
r = eegmcp_call_tool('eegmcp_source_localization(%s)', ['{"component_indices":[1],' ...
    '"head_model":"spherical",' override '}']);
if has_fieldtrip
    eegmcp_check(strcmp(r.status, 'success') && r.ncomponents == 1 && numel(r.dipoles) == 1, ...
        'eeglab_source_localization fits one dipole', r);
else
    eegmcp_check(strcmp(r.code, 'plugin_missing'), 'eeglab_source_localization reports missing FieldTrip-lite', r);
end

% ---- reload the sample so later suites start from clean data ----
r = eegmcp_call_tool('eegmcp_load_data(%s)', sample);
eegmcp_check(strcmp(r.status, 'success'), 'sample reloads', r);

fprintf('All b3 tool tests passed.\n');
end
