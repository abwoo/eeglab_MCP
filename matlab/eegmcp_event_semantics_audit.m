function eegmcp_event_semantics_audit(options)
%EEGMCP_EVENT_SEMANTICS_AUDIT Keep confirmed conditions separate from QC markers.
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'event_types', 'strings'; 'condition_markers', 'strings'; ...
        'exclude_markers', 'strings'; 'boundary_markers', 'strings'; 'segment_markers', 'strings'; ...
        'event_counts', 'object'; 'event_descriptions', 'object'});
    events = eegmcp_cellstr(eegmcp_opt(opts, 'event_types', {}));
    counts = eegmcp_opt(opts, 'event_counts', struct());
    if isempty(events)
        events = fieldnames(counts)';
    end
    confirmed = {}; candidates = {}; excluded = {}; boundary = {}; segments = {}; impedance = {};
    rows = {};
    for k = 1:numel(events)
        label = events{k};
        key = lower(strtrim(label));
        reason = 'heuristic fallback';
        role = '';
        descriptions = eegmcp_opt(opts, 'event_descriptions', struct());
        field = matlab.lang.makeValidName(label);
        if isfield(descriptions, field)
            item = descriptions.(field);
            if isstruct(item)
                item = eegmcp_opt(item, 'role', '');
            end
            role = lower(strtrim(eegmcp_text(item)));
            reason = 'event_descriptions mapping';
        end
        % Explicit exclusions take precedence even if a marker is also in a condition list.
        if listed(opts, 'exclude_markers', key)
            role = 'excluded';
        elseif listed(opts, 'boundary_markers', key) || contains(key, 'boundary')
            role = 'boundary';
        elseif listed(opts, 'segment_markers', key)
            role = 'segment_marker';
        elseif contains(key, 'impedance')
            role = 'impedance';
        elseif any(strcmp(key, {'start', 'end', 's1000', 'new segment', 'sync', 'pause', 'resume', 'calibration'}))
            role = 'qc_annotation';
        elseif listed(opts, 'condition_markers', key)
            role = 'condition';
            reason = 'explicit condition marker';
        elseif any(strcmp(role, {'trigger', 'stimulus', 'task_condition'}))
            role = 'condition';
        elseif ~any(strcmp(role, {'condition', 'excluded', 'boundary', 'segment_marker', 'impedance', 'qc_annotation'}))
            role = 'candidate_trigger';
        end
        row = struct('label', label, 'role', role, 'reason', reason, 'count', []);
        if isfield(counts, field)
            row.count = counts.(field);
        end
        rows{end + 1} = row; %#ok<AGROW>
        switch role
            case 'condition'
                confirmed{end + 1} = label; %#ok<AGROW>
            case 'candidate_trigger'
                candidates{end + 1} = label; %#ok<AGROW>
            case 'boundary'
                boundary{end + 1} = label; %#ok<AGROW>
            case 'segment_marker'
                segments{end + 1} = label; %#ok<AGROW>
            case 'impedance'
                impedance{end + 1} = label; %#ok<AGROW>
            otherwise
                excluded{end + 1} = label; %#ok<AGROW>
        end
    end
    blockers = {};
    if isempty(confirmed)
        blockers = {'No confirmed condition trigger exists; confirm candidate meanings before epoching.'};
    end
    summary = struct('classifications', {rows}, 'confirmed_analysis_events', {confirmed}, ...
        'candidate_analysis_events_need_confirmation', {candidates}, 'boundary_events', {boundary}, ...
        'segment_events', {segments}, 'impedance_events', {impedance}, 'excluded_events', {excluded}, ...
        'blocking_conditions', {blockers});
    eegmcp_emit(eegmcp_workflow_result('eeglab_event_semantics_audit', opts, summary));
catch err
    eegmcp_workflow_fail(err, 'event_audit_failed');
end
end

function yes = listed(opts, name, key)
items = eegmcp_cellstr(eegmcp_opt(opts, name, {}));
yes = any(strcmp(key, lower(strtrim(items))));
end
