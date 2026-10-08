function info = eegmcp_dataset_info(EEG)
%EEGMCP_DATASET_INFO Read-only summary of an EEGLAB dataset structure.

info.nbchan = EEG.nbchan;
info.srate = EEG.srate;
info.pnts = EEG.pnts;
info.trials = EEG.trials;
info.xmin = EEG.xmin;
info.xmax = EEG.xmax;
info.duration_sec = EEG.pnts / EEG.srate;
info.total_data_duration_sec = EEG.pnts * max(1, EEG.trials) / EEG.srate;
if EEG.trials > 1
    info.data_shape = 'epoched';
else
    info.data_shape = 'continuous_or_single_trial';
end
info.setname = EEG.setname;
info.filename = EEG.filename;
info.filepath = EEG.filepath;
info.saved = EEG.saved;
info.has_comments = isfield(EEG, 'comments') && ~isempty(EEG.comments);
info.has_etc_metadata = isfield(EEG, 'etc') && ~isempty(EEG.etc);
if isfield(EEG, 'ref') && ~isempty(EEG.ref)
    info.reference = EEG.ref;
else
    info.reference = '';
end
info.processing_history_available = isfield(EEG, 'history') && ~isempty(EEG.history);

% Channels and channel locations
if isfield(EEG, 'chanlocs') && ~isempty(EEG.chanlocs)
    if isfield(EEG.chanlocs, 'labels')
        info.channel_labels = {EEG.chanlocs.labels};
    else
        info.channel_labels = {};
    end
    located = false(1, numel(EEG.chanlocs));
    for ci = 1:numel(EEG.chanlocs)
        has_xyz = isfield(EEG.chanlocs, 'X') && ~isempty(EEG.chanlocs(ci).X) && ...
            isfield(EEG.chanlocs, 'Y') && ~isempty(EEG.chanlocs(ci).Y) && ...
            isfield(EEG.chanlocs, 'Z') && ~isempty(EEG.chanlocs(ci).Z);
        has_polar = isfield(EEG.chanlocs, 'theta') && ~isempty(EEG.chanlocs(ci).theta) && ...
            isfield(EEG.chanlocs, 'radius') && ~isempty(EEG.chanlocs(ci).radius);
        located(ci) = has_xyz || has_polar;
    end
    info.channels_with_locations = sum(located);
else
    info.channel_labels = {};
    info.channels_with_locations = 0;
end
info.channels_missing_locations = max(0, EEG.nbchan - info.channels_with_locations);
info.has_channel_locations = EEG.nbchan > 0 && info.channels_with_locations == EEG.nbchan;
info.channel_location_coverage = info.channels_with_locations / max(1, EEG.nbchan);

% Events
if isfield(EEG, 'event') && ~isempty(EEG.event)
    [info.event_types, info.event_counts] = eegmcp_event_counts(EEG.event);
    info.num_events = numel(EEG.event);
    if isfield(EEG.event, 'latency')
        latencies = [EEG.event.latency];
        info.event_latency_range_sec = [min(latencies), max(latencies)] / EEG.srate;
    else
        info.event_latency_range_sec = [];
    end
    info.has_urevent_links = isfield(EEG.event, 'urevent');
else
    info.event_types = {};
    info.event_counts = {};
    info.num_events = 0;
    info.event_latency_range_sec = [];
    info.has_urevent_links = false;
end
if isfield(EEG, 'urevent')
    info.num_urevents = numel(EEG.urevent);
else
    info.num_urevents = 0;
end

% ICA
info.ica_computed = isfield(EEG, 'icaweights') && ~isempty(EEG.icaweights);
if info.ica_computed
    info.ica_ncomponents = size(EEG.icaweights, 1);
else
    info.ica_ncomponents = 0;
end
info.ica_classified = isfield(EEG, 'etc') && isfield(EEG.etc, 'ic_classification') && ...
    isfield(EEG.etc.ic_classification, 'ICLabel');
end
