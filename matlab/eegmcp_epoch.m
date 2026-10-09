function eegmcp_epoch(options)
%EEGMCP_EPOCH Epoch the current dataset and remove the baseline (MCP tool eeglab_epoch).
%   Options (JSON object): event_types (list of event types, default all
%   events), pre_stimulus (seconds, default -0.2), post_stimulus (seconds,
%   default 0.8), baseline_start (seconds, default -0.2), baseline_end
%   (seconds, default 0), plus the gate options method_context,
%   override_gate and override_reason. Wraps pop_epoch and pop_rmbase.

try
    opts = eegmcp_options(options);
    event_types = eegmcp_cellstr(eegmcp_opt(opts, 'event_types', {}));
    pre_stim = eegmcp_opt(opts, 'pre_stimulus', -0.2);
    post_stim = eegmcp_opt(opts, 'post_stimulus', 0.8);
    bl_start = eegmcp_opt(opts, 'baseline_start', -0.2);
    bl_end = eegmcp_opt(opts, 'baseline_end', 0);

    errors = {};
    names = {'pre_stimulus', 'post_stimulus', 'baseline_start', 'baseline_end'};
    values = {pre_stim, post_stim, bl_start, bl_end};
    for k = 1:numel(names)
        value = values{k};
        if ~(isnumeric(value) && isscalar(value) && isreal(value) && isfinite(value))
            errors{end + 1} = [names{k} ' must be a finite number']; %#ok<AGROW>
        end
    end
    errors = eegmcp_b2_override_errors(opts, errors);
    if eegmcp_b2_invalid('eeglab_epoch', errors)
        return
    end
    pre_stim = double(pre_stim);
    post_stim = double(post_stim);
    bl_start = double(bl_start);
    bl_end = double(bl_end);
    if eegmcp_b2_window_failed('eeglab_epoch', ...
            eegmcp_window_errors([pre_stim, post_stim], [bl_start, bl_end] * 1000, []))
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    [gate, blocked] = eegmcp_gate('eeglab_epoch', opts, gate_context(opts, event_types));
    if blocked
        return
    end

    if ~isfield(dataset, 'event') || isempty(dataset.event)
        eegmcp_fail('no_events', 'The dataset has no events to epoch on.', ...
            'Load a dataset with event markers, or import events first.');
        return
    end

    % An empty type list makes pop_epoch use every event.
    evalc('dataset = pop_epoch(dataset, event_types, [pre_stim, post_stim], ''epochinfo'', ''yes'');');
    baseline_requested = [bl_start, bl_end] * 1000;
    baseline_points = find(dataset.times >= baseline_requested(1) & dataset.times <= baseline_requested(2));
    if isempty(baseline_points)
        eegmcp_fail('invalid_analysis_window', 'No samples fall inside the requested baseline window.', ...
            'Widen the baseline window (baseline_start, baseline_end); the dataset was not changed.');
        return
    end
    evalc('dataset = pop_rmbase(dataset, [], baseline_points);');
    evalc('eegmcp_commit(dataset);');

    result.status = 'success';
    result.trials = dataset.trials;
    result.xmin = dataset.xmin;
    result.xmax = dataset.xmax;
    result.pnts = dataset.pnts;
    result.baseline_requested = baseline_requested;
    result.baseline_applied = [dataset.times(baseline_points(1)), dataset.times(baseline_points(end))];
    result.baseline_points = [baseline_points(1), baseline_points(end)];
    if isempty(event_types)
        result.event_types = {'all'};
    else
        result.event_types = event_types;
    end
    [result.epoch_event_types, result.epoch_event_counts] = eegmcp_event_counts(dataset.event);
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('epoch_failed', err.message, ...
        'Check event_types against eeglab_get_events and that the epoch window fits the data.');
end
end

function derived = gate_context(opts, event_types)
% Port of the eeglab_epoch block of _preflight_context_from_arguments.
derived = struct();
if ~isempty(event_types)
    derived.candidate_event_types = event_types;
end
epoch_window = eegmcp_opt(opts, 'epoch_window', []);
baseline_window = eegmcp_opt(opts, 'baseline_window', []);
if ~isempty(epoch_window) || ~isempty(baseline_window)
    derived.epoch_window = epoch_window;
    derived.baseline_window = baseline_window;
end
if isfield(opts, 'pre_stimulus') || isfield(opts, 'post_stimulus')
    % Preserve explicitly supplied epoch and baseline bounds for the gate.
    if ~isfield(derived, 'epoch_window')
        derived.epoch_window = [raw(opts, 'pre_stimulus'), raw(opts, 'post_stimulus')];
    end
    if ~isfield(derived, 'baseline_window')
        derived.baseline_window = [raw(opts, 'baseline_start'), raw(opts, 'baseline_end')];
    end
end
derived = eegmcp_b2_output_context(opts, derived);
end

function value = raw(opts, name)
value = NaN;
if isfield(opts, name) && isnumeric(opts.(name)) && isscalar(opts.(name))
    value = double(opts.(name));
end
end
