function eegmcp_get_events()
%EEGMCP_GET_EVENTS List event types and counts of the current dataset (MCP tool eeglab_get_events). Read-only.

dataset = eegmcp_current_dataset();
if isempty(dataset)
    eegmcp_fail('no_dataset', 'No EEG dataset is loaded.', 'Call eeglab_load_data first.');
    return
end

try
    info = eegmcp_dataset_info(dataset);
    result.status = 'success';
    result.num_events = info.num_events;
    result.event_types = info.event_types;
    result.event_counts = info.event_counts;
    result.event_latency_range_sec = info.event_latency_range_sec;
    result.has_urevent_links = info.has_urevent_links;
    result.num_urevents = info.num_urevents;
    eegmcp_emit(result);
catch err
    eegmcp_fail('get_events_failed', err.message, 'Check the EEG.event structure of the dataset.');
end
end
