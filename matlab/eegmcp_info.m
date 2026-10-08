function eegmcp_info()
%EEGMCP_INFO Describe the current EEGLAB dataset (MCP tool eeglab_info). Read-only.

dataset = eegmcp_current_dataset();
if isempty(dataset)
    eegmcp_fail('no_dataset', 'No EEG dataset is loaded.', 'Call eeglab_load_data first.');
    return
end

try
    result = eegmcp_dataset_info(dataset);
    result.status = 'success';
    eegmcp_emit(result);
catch err
    eegmcp_fail('info_failed', err.message, 'Check that the dataset passes eeg_checkset.');
end
end
