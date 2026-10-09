function ok = eegmcp_check_requirement(check, ctx)
%EEGMCP_CHECK_REQUIREMENT Evaluate one method-gate requirement against a context.
%   The versioned official claims document defines the policy.
%   CTX is a struct decoded from JSON. matlab/tests checks this function
%   Uses the versioned MATLAB method-gate definitions and regression expectations.

switch check
    case 'confirmed_condition_events'
        roles = event_roles(ctx);
        ok = truthy(ctx, 'confirmed_condition_events', 'condition_markers', 'analysis_event_types') || ...
            any(ismember({'condition', 'trigger', 'task_condition', 'stimulus'}, roles));
    case 'no_only_nonanalysis_events'
        roles = event_roles(ctx);
        ok = isempty(roles) || ...
            ~all(ismember(roles, {'boundary', 'impedance', 'segment_marker', 'excluded', 'qc_annotation'}));
    case 'epoch_windows_recorded'
        ok = truthy(ctx, 'epoch_window', 'baseline_window', 'epoch_windows_recorded');
    case 'baseline_recorded'
        ok = truthy(ctx, 'baseline', 'baseline_window', 'baseline_recorded');
    case 'frequency_settings_recorded'
        ok = truthy(ctx, 'freq_range', 'cycles', 'frequency_settings_recorded');
    case 'continuous_data'
        ok = any(strcmp(lower_text(ctx, 'data_shape'), {'continuous', 'continuous_or_single_trial', 'single_trial'})) || ...
            is_true(ctx, 'has_continuous_raw');
    case 'plugin_clean_rawdata_available'
        ok = plugins_include(ctx, 'clean_rawdata', 'pop_clean_rawdata');
    case 'plugin_iclabel_available'
        ok = plugins_include(ctx, 'iclabel', 'pop_iclabel');
    case 'plugin_dipfit_available'
        ok = plugins_include(ctx, 'dipfit', 'pop_dipfit_settings');
    case 'plugin_eegbids_available'
        ok = plugins_include(ctx, 'eeg-bids', 'eegbids', 'pop_importbids');
    case 'thresholds_recorded'
        ok = truthy(ctx, 'thresholds_recorded', 'asr_thresholds', 'burst_criterion');
    case 'derivative_output_planned'
        ok = truthy(ctx, 'derivative_output_planned', 'output_path_separate', 'output_dir', 'output_path');
    case 'rank_reference_reviewed'
        ok = truthy(ctx, 'rank_reference_reviewed', 'rank_reviewed', 'reference_reviewed');
    case 'bad_channel_policy_defined'
        ok = truthy(ctx, 'bad_channel_policy_defined', 'bad_channels_reviewed', 'bad_channel_policy');
    case 'has_ica'
        ok = truthy(ctx, 'has_ica', 'ica_computed', 'ica_weights_present');
    case 'component_reviewed'
        ok = truthy(ctx, 'component_reviewed', 'iclabel_reviewed', 'component_review_policy', 'component_indices');
    case 'has_channel_locations'
        ok = is_true(ctx, 'has_channel_locations');
        if ~ok && isfield(ctx, 'channel_location_coverage')
            value = ctx.channel_location_coverage;
            ok = (isscalar(value) && (isnumeric(value) || islogical(value)) && double(value) == 1) || ...
                (ischar(value) && strcmp(value, 'complete'));
        end
    case 'has_channel_locations_or_repair_plan'
        ok = eegmcp_check_requirement('has_channel_locations', ctx) || ...
            truthy(ctx, 'channel_location_repair_planned', 'loc_file', 'ref_chanlocs', 'rename_map');
    case 'channel_location_repair_planned'
        ok = truthy(ctx, 'channel_location_repair_planned', 'loc_file', 'ref_chanlocs', 'rename_map');
    case 'head_model_defined'
        ok = truthy(ctx, 'head_model', 'template', 'head_model_defined');
    case 'multi_subject_or_bids'
        ok = any(strcmp(lower_text(ctx, 'project_scale'), {'multi_subject', 'bids_study', 'bids'})) || ...
            truthy(ctx, 'bids_path', 'dataset_paths');
    case 'single_subject_protocol_locked'
        ok = truthy(ctx, 'single_subject_protocol_locked', 'preprocessing_protocol_locked');
    case 'design_variables_defined'
        ok = truthy(ctx, 'design_variables_defined', 'design_variables', 'variable_name', 'variable_values');
    case 'study_measure_recorded'
        ok = truthy(ctx, 'study_measure_recorded', 'measure', 'measure_type', 'precomputed_measure', ...
            'erp_measure', 'ersp_measure');
    case 'raw_input_preserved'
        ok = is_true(ctx, 'raw_input_preserved') || is_true(ctx, 'input_preserved');
    case 'parameters_recorded'
        ok = is_true(ctx, 'parameters_recorded') || truthy(ctx, 'parameters', 'filter_cutoffs', 'ref_type');
    case 'pipeline_defaults_accepted'
        ok = is_true(ctx, 'pipeline_defaults_accepted');
    case 'reference_or_montage_recorded'
        ok = recorded_or_missing(ctx, 'reference', 'reference_or_montage', 'montage', 'ground', 'cap_layout', ...
            'eeg_reference', 'eeg_ground', 'eeg_placement_scheme');
    case 'power_line_frequency_recorded'
        ok = recorded_or_missing(ctx, 'power_line_frequency', 'powerlinefrequency', 'line_freq', 'line_frequency');
    case 'acquisition_filters_recorded'
        ok = recorded_or_missing(ctx, 'acquisition_filters', 'hardware_filters', 'software_filters', ...
            'hardware_filter', 'software_filter');
    case 'task_or_acquisition_system_recorded'
        ok = recorded_or_missing(ctx, 'task_name', 'task_description', 'acquisition_system', 'manufacturer', ...
            'recording_system');
    case 'impedance_or_quality_recorded'
        ok = recorded_or_missing(ctx, 'impedance', 'impedance_notes', 'channel_quality_notes', 'quality_notes', ...
            'channels_status');
    case 'bids_or_sidecars_available'
        ok = truthy(ctx, 'bids_path', 'events_json', 'events_sidecar', 'hed_tags', 'event_code_map', 'sidecar_paths');
    case 'bids_eeg_sidecar_complete'
        ok = is_true(ctx, 'bids_eeg_sidecar_complete') || ( ...
            (truthy(ctx, 'eeg_json') || sidecars_include(ctx, 'eeg.json', '_eeg.json')) && ...
            (truthy(ctx, 'channels_tsv') || sidecars_include(ctx, 'channels.tsv', '_channels.tsv')) && ...
            (truthy(ctx, 'electrodes_tsv') || sidecars_include(ctx, 'electrodes.tsv', '_electrodes.tsv')) && ...
            (truthy(ctx, 'coordsystem_json') || sidecars_include(ctx, 'coordsystem.json', '_coordsystem.json')));
    case 'bids_events_have_onset_duration'
        columns = first_truthy_value(ctx, {'events_tsv_columns', 'event_columns'});
        columns = lower(strtrim(text_items(columns)));
        ok = is_true(ctx, 'events_have_onset_duration') || all(ismember({'onset', 'duration'}, columns));
    case 'event_metadata_described'
        ok = truthy(ctx, 'event_metadata_described', 'events_json', 'hed_tags', 'event_code_map', 'behavioral_log');
    case 'bids_event_columns_described'
        ok = is_true(ctx, 'bids_event_columns_described') || is_true(ctx, 'trial_type_described') || ...
            truthy(ctx, 'events_json', 'event_code_map', 'hed_tags');
    case 'source_format_recorded'
        ok = truthy(ctx, 'source_format', 'data_format', 'input_format', 'file_format', 'input_path');
    case 'plugin_import_available'
        fmt = lower(strtrim(eegmcp_text(first_truthy_value(ctx, ...
            {'source_format', 'data_format', 'input_format', 'file_format'}, ''))));
        if any(strcmp(fmt, {'', 'set', '.set', 'eeglab', 'eeglab_set'})) || endsWith(fmt, '.set')
            ok = true;
        elseif truthy(ctx, 'plugin_import_available', 'import_plugin_available', 'import_function_available')
            ok = true;
        else
            ok = format_plugin_available(ctx, fmt, { ...
                'edf', {'biosig', 'pop_biosig'}; 'bdf', {'biosig', 'pop_biosig'}; ...
                'gdf', {'biosig', 'pop_biosig'}; 'biosig', {'biosig', 'pop_biosig'}; ...
                'fieldtrip', {'file-io', 'fileio', 'pop_fileio'}; 'file-io', {'file-io', 'fileio', 'pop_fileio'}; ...
                'fileio', {'file-io', 'fileio', 'pop_fileio'}; 'mff', {'mff-matlab-io', 'mff', 'mff_import'}; ...
                'egi', {'mff-matlab-io', 'mff', 'mff_import'}; 'nwb', {'nwb-io', 'nwbio', 'nwb_import'}; ...
                'brainvision', {'bva-io', 'bva', 'pop_loadbv'}; 'vhdr', {'bva-io', 'bva', 'pop_loadbv'}; ...
                'vmrk', {'bva-io', 'bva', 'pop_loadbv'}; 'bva', {'bva-io', 'bva', 'pop_loadbv'}; ...
                'bids', {'eeg-bids', 'eegbids', 'pop_importbids'}});
        end
    case 'import_event_channel_mapping_recorded'
        ok = truthy(ctx, 'import_event_channel_mapping_recorded', 'event_import_policy', 'event_mapping', ...
            'channel_mapping', 'header_mapping', 'sidecar_paths', 'events_json');
    case 'export_format_supported'
        fmt = lower(strtrim(eegmcp_text(first_truthy_value(ctx, ...
            {'export_format', 'target_format', 'output_format', 'file_format'}, ''))));
        if any(strcmp(fmt, {'set', '.set', 'eeglab', 'eeglab_set'})) || endsWith(fmt, '.set')
            ok = true;
        elseif truthy(ctx, 'export_format_supported', 'export_plugin_available', 'export_function_available')
            ok = true;
        else
            ok = format_plugin_available(ctx, fmt, { ...
                'mff', {'mff-matlab-io', 'mff', 'mff_export'}; 'nwb', {'nwb-io', 'nwbio', 'nwb_export'}; ...
                'brainvision', {'bva-io', 'bva', 'pop_writebva'}; 'vhdr', {'bva-io', 'bva', 'pop_writebva'}; ...
                'bva', {'bva-io', 'bva', 'pop_writebva'}; 'bids', {'eeg-bids', 'eegbids', 'pop_exportbids'}});
        end
    case 'export_metadata_complete'
        ok = is_true(ctx, 'export_metadata_complete') || is_true(ctx, 'channel_event_metadata_complete') || ...
            is_true(ctx, 'header_metadata_complete') || ...
            (eegmcp_check_requirement('bids_eeg_sidecar_complete', ctx) && ...
            eegmcp_check_requirement('event_metadata_described', ctx));
    case 'hed_schema_recorded'
        ok = truthy(ctx, 'hed_schema_recorded', 'hed_schema_version', 'hed_version', 'hed_schema', ...
            'hed_library', 'event_codebook_version');
    case 'event_code_map_validated'
        ok = truthy(ctx, 'event_code_map_validated', 'validated_event_code_map', 'codebook_validated', ...
            'behavioral_log', 'events_json');
    case 'processing_history_recorded'
        ok = truthy(ctx, 'processing_history_recorded', 'processing_history', 'eeglab_history', ...
            'history_script', 'EEG.history');
    case 'script_from_history_reviewed'
        ok = truthy(ctx, 'script_from_history_reviewed', 'history_script_reviewed', 'batch_script_reviewed', ...
            'script_parameters_reviewed');
    case 'event_modification_rule_recorded'
        ok = truthy(ctx, 'event_modification_rule_recorded', 'event_modification_rule', 'event_recode_table', ...
            'latency_shift_rule', 'deleted_event_policy');
    case 'event_latency_units_recorded'
        ok = truthy(ctx, 'event_latency_units_recorded', 'event_latency_units', 'latency_units', ...
            'sampling_rate_hz', 'srate');
    case 'urevent_preserved_or_relinked'
        ok = is_true(ctx, 'urevent_preserved') || is_true(ctx, 'urevent_relinked') || ...
            any(strcmp(strtrim(lower_text(ctx, 'urevent_link_status')), {'preserved', 'relinked', 'valid', 'consistent'}));
    case 'line_noise_parameters_recorded'
        ok = truthy(ctx, 'line_noise_parameters_recorded', 'line_freq', 'line_frequency') && ...
            truthy(ctx, 'line_noise_method', 'method', 'bandwidth');
    case 'artifact_policy_recorded'
        ok = truthy(ctx, 'artifact_policy_recorded', 'artifact_policy', 'rejection_policy', 'cleaning_summary');
    case 'channels_recorded'
        ok = truthy(ctx, 'channels', 'channel_set', 'roi', 'rois');
    case 'connectivity_limits_recorded'
        ok = truthy(ctx, 'connectivity_limits_recorded', 'connectivity_limits', 'sensor_space_limit', ...
            'source_space', 'model_assumptions');
    case 'plugin_limo_available'
        ok = plugins_include(ctx, 'limo', 'pop_limo', 'limo_eeg');
    case 'plugin_sift_available'
        ok = plugins_include(ctx, 'sift', 'groupsift', 'eegplugin_sift');
    case 'plugin_amica_available'
        ok = plugins_include(ctx, 'amica', 'runamica15', 'pop_runamica');
    case 'plugin_nsg_available'
        ok = plugins_include(ctx, 'nsgportal', 'pop_nsg', 'nsgportal');
    case 'plugin_relica_available'
        ok = plugins_include(ctx, 'relica', 'pop_relica', 'eegplugin_relica');
    case 'plugin_viewprops_available'
        ok = plugins_include(ctx, 'viewprops', 'pop_viewprops', 'pop_prop_extended');
    case 'plugin_get_chanlocs_available'
        ok = plugins_include(ctx, 'get_chanlocs', 'eegplugin_getchanlocs');
    case 'plugin_roiconnect_available'
        ok = plugins_include(ctx, 'roiconnect', 'pop_roi_connect', 'pop_roi_activity');
    case 'plugin_eegstats_available'
        ok = plugins_include(ctx, 'eegstats', 'pop_eegstats', 'eegplugin_eegstats');
    case 'statistical_design_defined'
        ok = truthy(ctx, 'statistical_design_defined', 'design_matrix', 'contrasts', 'first_level_model', ...
            'second_level_model', 'design_variables');
    case 'correction_policy_recorded'
        ok = truthy(ctx, 'correction_policy_recorded', 'correction', 'alpha', 'mcc');
    case 'model_validation_recorded'
        ok = truthy(ctx, 'model_validation_recorded', 'model_order', 'stationarity', 'validation', ...
            'whiteness_test', 'stability_test');
    case 'bootstrap_settings_recorded'
        ok = truthy(ctx, 'bootstrap_settings_recorded', 'bootstrap', 'bootstrap_samples', 'n_bootstrap', ...
            'reliability_settings');
    case 'plugin_goal_defined'
        ok = truthy(ctx, 'plugin_goal_defined', 'plugin_goal', 'extension_goal', 'user_story');
    case 'eeglab_function_family_recorded'
        ok = truthy(ctx, 'eeglab_function_family_recorded', 'function_family', 'gui_boundary', ...
            'command_line_boundary', 'pop_function');
    case 'validation_plan_recorded'
        ok = truthy(ctx, 'validation_plan_recorded', 'validation_plan', 'sample_data_plan', ...
            'documentation_plan', 'test_plan');
    case 'head_image_or_digitization_source_recorded'
        ok = truthy(ctx, 'head_image_or_digitization_source_recorded', 'head_image', 'digitization_file', ...
            'fiducial_file', 'electrode_photo');
    case 'fiducials_recorded'
        ok = truthy(ctx, 'fiducials_recorded', 'fiducials', 'nasion', 'lpa', 'rpa');
    case 'source_model_available'
        ok = truthy(ctx, 'source_model_available', 'source_model', 'dipfit', 'source_solution');
    case 'roi_atlas_recorded'
        ok = truthy(ctx, 'roi_atlas_recorded', 'roi_atlas', 'atlas', 'parcellation');
    case 'connectivity_metric_recorded'
        ok = truthy(ctx, 'connectivity_metric_recorded', 'connectivity_metric', 'roi_connectivity_metric', ...
            'roi_metric', 'method');
    case 'software_versions_recorded'
        ok = truthy(ctx, 'software_versions_recorded', 'software_versions', 'eeglab_version', ...
            'plugin_versions', 'processing_history');
    case 'clustering_policy_recorded'
        ok = truthy(ctx, 'clustering_policy_recorded', 'cluster_algorithm', 'cluster_count', 'n_clusters', ...
            'cluster_features', 'distance_metric', 'outlier_policy');
    case 'compute_strategy_recorded'
        ok = truthy(ctx, 'compute_strategy_recorded', 'compute_strategy', 'compute_plan', 'amica_settings', ...
            'max_threads', 'num_models');
    case 'remote_compute_approved'
        ok = is_true(ctx, 'remote_compute_approved') || is_true(ctx, 'nsg_remote_approved') || ...
            is_true(ctx, 'data_upload_approved');
    case 'job_provenance_recorded'
        ok = truthy(ctx, 'job_provenance_recorded', 'remote_job_parameters', 'nsg_job_id', 'upload_manifest', ...
            'download_plan', 'credential_policy', 'data_transfer_policy');
    otherwise
        ok = false;
end
end

% ---------------------------------------------------------------------------
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
% because jsondecode renames keys that are not valid MATLAB field names.

function [present, value] = get(ctx, name)
field = matlab.lang.makeValidName(name);
present = isfield(ctx, field);
if present
    value = ctx.(field);
else
    value = [];
end
end

function ok = value_truthy(value)
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
if ischar(value) || isstring(value)
    ok = ~isempty(strtrim(char(value)));
elseif iscell(value)
    ok = ~isempty(value);
elseif isstruct(value)
    ok = ~isempty(value) && (numel(value) > 1 || ~isempty(fieldnames(value)));
elseif isnumeric(value) || islogical(value)
    if isscalar(value)
        ok = value ~= 0;
    else
        ok = ~isempty(value);
    end
else
    ok = ~isempty(value);
end
end

function ok = truthy(ctx, varargin)
ok = false;
for k = 1:numel(varargin)
    [present, value] = get(ctx, varargin{k});
    if present && value_truthy(value)
        ok = true;
        return
    end
end
end

function ok = is_true(ctx, name)
[~, value] = get(ctx, name);
ok = islogical(value) && isscalar(value) && value;
end

function text = lower_text(ctx, name)
[present, value] = get(ctx, name);
if present
    text = lower(eegmcp_text(value));
else
    text = '';
end
end

function value = first_truthy_value(ctx, names, default)
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
if nargin < 3
    default = {};
end
value = default;
for k = 1:numel(names)
    [present, candidate] = get(ctx, names{k});
    %   Uses the versioned MATLAB method-gate definitions and regression expectations.
    if present && (value_truthy(candidate) || ((ischar(candidate) || isstring(candidate)) && strlength(candidate) > 0))
        value = candidate;
        return
    end
end
end

function items = text_items(value)
% Items of a list-like value as a cell of char; a non-list gives {}.
if iscell(value)
    items = cellfun(@eegmcp_text, value(:)', 'UniformOutput', false);
else
    items = {};
end
end

function roles = event_roles(ctx)
value = first_truthy_value(ctx, {'event_roles', 'marker_roles'});
if isstruct(value) && isscalar(value)
    value = struct2cell(value)';
end
if iscell(value)
    roles = lower(strtrim(cellfun(@eegmcp_text, value(:)', 'UniformOutput', false)));
    roles = unique(roles(~cellfun(@isempty, roles)));
else
    roles = {};
end
end

function ok = plugins_include(ctx, varargin)
value = first_truthy_value(ctx, {'plugins_available', 'available_plugins'});
if iscell(value)
    available = lower(cellfun(@eegmcp_text, value(:)', 'UniformOutput', false));
else
    available = {};
end
ok = false;
for k = 1:numel(varargin)
    name = lower(varargin{k});
    if truthy(ctx, ['plugin_' name '_available']) || any(strcmp(name, available))
        ok = true;
        return
    end
end
end

function ok = format_plugin_available(ctx, fmt, table)
ok = false;
for k = 1:size(table, 1)
    if contains(fmt, table{k, 1})
        ok = plugins_include(ctx, table{k, 2}{:});
        return
    end
end
end

function ok = recorded_or_missing(ctx, field, varargin)
% Metadata is recorded, or its absence was explicitly documented.
value = first_truthy_value(ctx, {'documented_missing_fields', 'missing_metadata_documented'});
if ischar(value) || isstring(value)
    raw = strsplit(strrep(char(value), ';', ','), ',');
elseif isstruct(value) && isscalar(value)
    names = fieldnames(value);
    raw = names(cellfun(@(n) value_truthy(value.(n)), names))';
elseif iscell(value)
    raw = value(:)';
else
    raw = {value};
end
keys = lower(strtrim(cellfun(@eegmcp_text, raw, 'UniformOutput', false)));
keys = keys(~cellfun(@isempty, keys));
if any(ismember(lower([{field}, varargin]), keys))
    ok = true;
else
    ok = truthy(ctx, field, varargin{:});
end
end

function ok = sidecars_include(ctx, varargin)
value = first_truthy_value(ctx, {'sidecars', 'sidecar_paths'});
haystack = {};
if isstruct(value) && isscalar(value)
    names = fieldnames(value);
    for k = 1:numel(names)
        item = value.(names{k});
        if value_truthy(item)
            haystack{end + 1} = lower(names{k}); %#ok<AGROW>
            haystack{end + 1} = lower(eegmcp_text(item)); %#ok<AGROW>
        end
    end
elseif iscell(value)
    haystack = lower(cellfun(@eegmcp_text, value(:)', 'UniformOutput', false));
end
ok = false;
for k = 1:numel(varargin)
    if any(contains(haystack, lower(varargin{k})))
        ok = true;
        return
    end
end
end
