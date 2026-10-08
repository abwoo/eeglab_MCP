function eegmcp_qc_report()
%EEGMCP_QC_REPORT Quality-control summary of the current dataset (MCP tool eeglab_qc_report).
%   Read-only. Summarizes recording dimensions, events, channel locations,
%   ICA and history, and lists risks to resolve before preprocessing.

dataset = eegmcp_current_dataset();
if isempty(dataset)
    eegmcp_fail('no_dataset', 'No EEG dataset is loaded.', 'Call eeglab_load_data first.');
    return
end

try
    info = eegmcp_dataset_info(dataset);

    risks = {};
    hints = {};
    if info.num_events == 0
        risks{end + 1} = 'No events were found; event-locked analyses may not be possible.';
    elseif ~info.has_urevent_links
        hints{end + 1} = 'Event urevent links are absent; preserve event latencies and counts when epoching.';
    end
    if ~info.has_channel_locations
        if info.channels_with_locations == 0
            risks{end + 1} = 'Channel locations are missing; topography and source workflows need them.';
        else
            risks{end + 1} = 'Some channel locations are missing; topography and source workflows may be incomplete.';
        end
    end
    if ~info.ica_computed
        risks{end + 1} = 'ICA weights are absent; component-level artifact review is not available yet.';
    end
    if info.srate < 128
        risks{end + 1} = 'Sampling rate is low for high-frequency analyses.';
    end
    if ~info.processing_history_available
        hints{end + 1} = 'EEGLAB processing history is empty; report every step applied in this session.';
    end
    if ~info.has_comments
        hints{end + 1} = 'Dataset comments are absent; record acquisition context outside the .set file if needed.';
    end
    if isempty(info.filename)
        hints{end + 1} = 'Source filename is missing from the dataset; keep the absolute input path in reports.';
    end

    result.status = 'success';
    result.summary = info;
    result.risk_hints = risks;
    result.provenance_hints = hints;
    result.next_step = ['Resolve the risk hints, confirm which events are condition triggers, ' ...
        'then plan preprocessing. This report does not change the data.'];
    eegmcp_emit(result);
catch err
    eegmcp_fail('qc_report_failed', err.message, 'Check that the dataset passes eeg_checkset.');
end
end
