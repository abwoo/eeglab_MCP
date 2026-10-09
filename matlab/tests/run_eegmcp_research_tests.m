function run_eegmcp_research_tests(eeglab_root)
%RUN_EEGMCP_RESEARCH_TESTS Research workflows, derivatives and real STUDY statistics.
global EEG ALLEEG STUDY
addpath(fileparts(fileparts(mfilename('fullpath'))));
sample = fullfile(eeglab_root, 'sample_data', 'eeglab_data.set');
out = fullfile(tempdir, 'eegmcp_research_tests');
if ~isfolder(out)
    mkdir(out);
end

r = call('eegmcp_method_preflight', struct('method', 'epoch'));
eegmcp_check(strcmp(r.summary.gate_status, 'blocked'), 'empty epoch context is blocked', r);
r = call('eegmcp_method_preflight', struct('method', 'epoch', 'override_reason', 'CI acceptance'));
eegmcp_check(r.summary.override_used, 'preflight records explicit overrides', r);
r = eegmcp_call_tool('eegmcp_method_preflight(%s)', '[]');
eegmcp_check(strcmp(r.code, 'invalid_options'), 'preflight rejects non-object options', r);
r = eegmcp_call_tool('eegmcp_official_claims()');
eegmcp_check(r.claim_count == 47 && r.method_profile_count == 39, 'versioned official map is readable', r);
r = call('eegmcp_workflow_recommend', struct());
eegmcp_check(strcmp(r.summary.analysis_type_resolved, 'qc'), 'unknown goal starts with QC', r);
r = call('eegmcp_project_plan', struct('analysis_type', 'erp', 'event_types', {{'boundary'}}));
eegmcp_check(~isempty(r.summary.blocking_conditions), 'ERP project blocks without confirmed triggers', r);
r = call('eegmcp_event_semantics_audit', struct('event_types', {{'boundary', 'impedance', 'square', 'rt'}}, ...
    'condition_markers', {{'boundary', 'square'}}, 'exclude_markers', {{'rt'}}));
eegmcp_check(isequal(r.summary.confirmed_analysis_events, {'square'}), 'QC markers cannot become condition triggers', r);
eegmcp_check(isequal(r.summary.excluded_events, {'rt'}), 'explicit exclusions are preserved', r);
r = call('eegmcp_plugin_check', struct('plugins', {{'ICLabel', 'DefinitelyMissingPlugin'}}));
plugins = r.summary.plugins;
if isstruct(plugins)
    plugins = num2cell(plugins);
end
eegmcp_check(plugins{1}.available && ~plugins{2}.available, 'plugin probes report found/missing functions', r);

gate = eegmcp_call_tool('eegmcp_method_preflight(%s)', '{"method":"epoch"}');
protocol_path = fullfile(out, 'blocked-protocol.json');
r = call('eegmcp_protocol_export', struct('format', 'json', 'output_path', protocol_path, ...
    'research_goal', 'CI protocol', 'gate_results', {{gate.summary}}));
eegmcp_check(strcmp(r.status, 'success') && isfile(protocol_path) && ...
    ~isempty(r.summary.missing_requirements), 'protocol preserves failed gates and writes JSON', r);
r = call('eegmcp_protocol_export', struct('format', 'json', 'output_path', sample));
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'protocol cannot overwrite raw EEG', r);
r = call('eegmcp_protocol_export', struct('override_used', true));
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'protocol override needs a reason', r);

params = struct('data_path', sample, 'output_dir', out, 'event_types', {{'square'}}, 'channels', {{'Cz'}}, ...
    'method_context', struct('confirmed_condition_events', true, 'raw_input_preserved', true, ...
    'derivative_output_planned', true));
r = call('eegmcp_erp_light_workflow', params);
eegmcp_check(strcmp(r.status, 'success') && isfile(r.outputs.output_path), 'MATLAB light ERP saves a derivative', r);
eegmcp_check(EEG.trials > 1 && isfile(sample), 'ERP keeps the raw file and produces epochs', r);
params.output_dir = fileparts(sample); params.output_filename = 'eeglab_data.set';
r = call('eegmcp_erp_light_workflow', params);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'ERP refuses to overwrite the input', r);
params.output_dir = out; params.output_filename = 'should-not-exist.set';
params.method_context = struct('confirmed_condition_events', true);
r = call('eegmcp_erp_light_workflow', params);
eegmcp_check(strcmp(r.code, 'official_gate_blocked') && ...
    ~isfile(fullfile(out, params.output_filename)), 'child derivative gate cannot be bypassed by the workflow', r);

resting = struct('data_path', sample, 'output_dir', out, 'pipeline_type', 'resting', 'channels', {{'Cz'}}, ...
    'method_context', struct('raw_input_preserved', true, 'derivative_output_planned', true, ...
    'pipeline_defaults_accepted', true, 'data_shape', 'continuous', 'artifact_policy_recorded', true));
r = call('eegmcp_pipeline', resting);
eegmcp_check(strcmp(r.status, 'success') && isfile(r.outputs.output_path), 'recorded MATLAB resting pipeline succeeds', r);
resting.method_context.pipeline_defaults_accepted = false;
r = call('eegmcp_pipeline', resting);
eegmcp_check(strcmp(r.code, 'official_gate_blocked'), 'pipeline requires acceptance of its defaults', r);

% Four subjects, two conditions, real precomputed ERP measures in cloud temp files.
eegmcp_call_tool('eegmcp_load_data(%s)', sample);
base = EEG;
evalc('base = pop_epoch(base, {''square''}, [-0.2 0.8]); base = pop_select(base, ''channel'', {''Cz''}, ''trial'', 1:12);');
paths = {}; subjects = {}; conditions = {};
for subject = 1:4
    for condition = 1:2
        data = base;
        data.data = data.data + subject * 0.1 + condition * subject * 0.2;
        data.subject = sprintf('S%d', subject); data.condition = sprintf('C%d', condition);
        filename = sprintf('S%d_C%d.set', subject, condition);
        evalc('data = pop_saveset(data, ''filename'', filename, ''filepath'', out);');
        paths{end + 1} = fullfile(out, filename); %#ok<AGROW>
        subjects{end + 1} = data.subject; %#ok<AGROW>
        conditions{end + 1} = data.condition; %#ok<AGROW>
    end
end
r = call('eegmcp_study_create', struct('dataset_paths', {paths}, 'subjects', {subjects}, ...
    'conditions', {conditions}, 'study_name', 'Cloud regression STUDY'));
eegmcp_check(strcmp(r.status, 'success') && r.num_datasets == 8 && ~r.raw_datasets_resaved, 'STUDY creation preserves input files', r);
r = call('eegmcp_study_design', struct('variable_name', 'condition', 'variable_values', {{'C1', 'C2'}}, 'paired', true));
eegmcp_check(strcmp(r.status, 'success') && r.paired, 'MATLAB creates a paired condition design', r);
evalc('[STUDY, ALLEEG] = std_precomp(STUDY, ALLEEG, ''channels'', {''Cz''}, ''erp'', ''on'', ''recompute'', ''on'');');
stats_opts = struct('measure', 'erp', 'channels', {{'Cz'}}, 'correction', 'fdr', ...
    'method_context', struct('single_subject_protocol_locked', true, 'design_variables_defined', true));
r = call('eegmcp_study_statistics', stats_opts);
eegmcp_check(strcmp(r.status, 'success') && ~isempty(r.corrected_pvalues), 'real STUDY ERP statistics run in MATLAB', r);
eegmcp_check(all(r.corrected_pvalues(:) >= r.pvalues(:) - eps) && ...
    all(r.corrected_pvalues(:) <= 1), 'FDR adjusted p-values are bounded and conservative', r);
stats_opts.alpha = 2;
r = call('eegmcp_study_statistics', stats_opts);
eegmcp_check(strcmp(r.code, 'invalid_arguments'), 'statistics rejects invalid alpha', r);
eegmcp_call_tool('eegmcp_load_data(%s)', sample);
fprintf('All MATLAB research workflow tests passed.\n');
end

function r = call(tool, options)
r = eegmcp_call_tool([tool '(%s)'], jsonencode(options));
end
