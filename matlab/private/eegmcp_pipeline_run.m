function result = eegmcp_pipeline_run(opts, workflow, light)
%EEGMCP_PIPELINE_RUN Compose gated tools and stop on the first failed step.
eegmcp_validate_options(opts, {'data_path', 'string', []; 'output_dir', 'string', []; ...
    'output_filename', 'string', []; 'pipeline_type', 'string', {'erp', 'resting', 'timefreq'}; ...
    'low_cutoff', 'positive', []; 'high_cutoff', 'positive', []; 'event_types', 'strings', []; ...
    'channels', 'strings', []; 'run_ica', 'boolean', []; 'clean_artifacts', 'boolean', []; ...
    'method_context', 'object', []; 'ica_algorithm', 'string', {'runica', 'picard'}; ...
    'burst_criterion', 'positive', []});
input = eegmcp_opt(opts, 'data_path', '');
folder = eegmcp_opt(opts, 'output_dir', '');
branch = eegmcp_opt(opts, 'pipeline_type', 'erp');
filename = eegmcp_opt(opts, 'output_filename', [branch '_processed.set']);
output = eegmcp_derivative_path(input, folder, filename);
if ~isfile(input)
    error('eegmcp:arguments', 'data_path must identify an existing cloud dataset.');
end
epoch_window = eegmcp_opt(opts, 'epoch_window', [-0.2, 0.8]);
baseline = eegmcp_opt(opts, 'baseline_window', [-200, 0]);
time_window = eegmcp_opt(opts, 'time_window', [250, 450]);
check_window(epoch_window, 'epoch_window');
check_window(baseline, 'baseline_window');
check_window(time_window, 'time_window');
if baseline(1) < epoch_window(1) * 1000 || baseline(2) > epoch_window(2) * 1000
    error('eegmcp:arguments', 'baseline_window in milliseconds must fit within epoch_window in seconds.');
end
low = eegmcp_opt(opts, 'low_cutoff', 0.5);
high = eegmcp_opt(opts, 'high_cutoff', 40);
if low >= high
    error('eegmcp:arguments', 'low_cutoff must be below high_cutoff.');
end
events = eegmcp_cellstr(eegmcp_opt(opts, 'event_types', {}));
if any(strcmp(branch, {'erp', 'timefreq'})) && isempty(events)
    error('eegmcp:arguments', 'event_types must explicitly select confirmed condition triggers.');
end
if light
    gate_name = 'eeglab_erp_light_workflow';
else
    gate_name = 'eeglab_pipeline';
end
derived = struct('output_dir', folder, 'derivative_output_planned', true, ...
    'epoch_window', epoch_window, 'baseline_window', baseline);
[gate, blocked] = eegmcp_gate(gate_name, opts, derived);
if blocked
    result = [];
    return
end
ctx = eegmcp_opt(opts, 'method_context', struct());
if ~isfield(ctx, 'derivative_output_planned')
    ctx.derivative_output_planned = true;
end
% Preserve user facts and overrides for every child; never bypass a child gate.
child = struct('method_context', ctx);
if eegmcp_opt(opts, 'override_gate', false)
    child.override_gate = true;
    child.override_reason = opts.override_reason;
end
specs = {{'eegmcp_load_data', {input}}, {'eegmcp_info', {}}, {'eegmcp_qc_report', {}}};
filter = child;
filter.filter_type = 'bandpass'; filter.low_cutoff = low; filter.high_cutoff = high;
specs{end + 1} = {'eegmcp_filter', {jsonencode(filter)}};
if ~light && eegmcp_opt(opts, 'clean_artifacts', false)
    clean = child; clean.burst_criterion = eegmcp_opt(opts, 'burst_criterion', 20);
    specs{end + 1} = {'eegmcp_clean_rawdata', {jsonencode(clean)}};
end
if ~light
    ref = child; ref.ref_type = 'average';
    specs{end + 1} = {'eegmcp_reref', {jsonencode(ref)}};
    if eegmcp_opt(opts, 'run_ica', false)
        ica = child; ica.algorithm = eegmcp_opt(opts, 'ica_algorithm', 'runica');
        specs{end + 1} = {'eegmcp_run_ica', {jsonencode(ica)}};
    end
end
channels = eegmcp_cellstr(eegmcp_opt(opts, 'channels', {'Cz'}));
if any(strcmp(branch, {'erp', 'timefreq'}))
    epoch = child; epoch.event_types = events;
    epoch.pre_stimulus = epoch_window(1); epoch.post_stimulus = epoch_window(2);
    epoch.baseline_start = baseline(1) / 1000; epoch.baseline_end = baseline(2) / 1000;
    specs{end + 1} = {'eegmcp_epoch', {jsonencode(epoch)}};
end
if strcmp(branch, 'erp')
    analysis = struct('channels', {channels}, 'time_window', time_window);
    specs{end + 1} = {'eegmcp_erp_analysis', {jsonencode(analysis)}};
elseif strcmp(branch, 'resting')
    analysis = child; analysis.channels = channels; analysis.freq_range = eegmcp_opt(opts, 'freq_range', [1, 40]);
    specs{end + 1} = {'eegmcp_spectral', {jsonencode(analysis)}};
else
    analysis = child; analysis.channels = channels; analysis.freq_range = eegmcp_opt(opts, 'freq_range', [3, 40]);
    analysis.baseline_window = baseline;
    specs{end + 1} = {'eegmcp_timefreq', {jsonencode(analysis)}};
end
specs{end + 1} = {'eegmcp_save_data', {jsonencode(struct('filepath', output))}};
steps = {}; outputs = struct();
for k = 1:numel(specs)
    spec = specs{k};
    response = eegmcp_run_step(spec{1}, spec{2}{:});
    steps{end + 1} = struct('name', spec{1}, 'status', response.status); %#ok<AGROW>
    outputs.(spec{1}) = response;
    if strcmp(response.status, 'error')
        result = eegmcp_workflow_result(workflow, opts, ...
            struct('failed_step', spec{1}, 'official_gate', gate), outputs, steps);
        result.status = 'error';
        result.code = response.code;
        result.error = response.error;
        result.next_step = response.next_step;
        return
    end
end
outputs.output_path = output;
result = eegmcp_workflow_result(workflow, opts, ...
    struct('official_gate', gate, 'output_path', output, 'raw_input_preserved', true, ...
    'automatic_component_removal', false), outputs, steps);
end

function check_window(value, name)
if ~isnumeric(value) || numel(value) ~= 2 || any(~isfinite(value)) || value(1) > value(2)
    error('eegmcp:arguments', '%s must be two finite values in ascending order.', name);
end
end
