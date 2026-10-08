function eegmcp_history()
%EEGMCP_HISTORY EEGLAB command history of the current dataset (MCP tool eeglab_history).
%   Read-only. Returns EEG.history, the EEGLAB commands recorded since the
%   data were loaded, as text and as one entry per command line. The MCP
%   tools add each command they run, so the history can be replayed.

try
    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    history_text = '';
    if isfield(dataset, 'history') && ~isempty(dataset.history)
        history_text = dataset.history;
    end
    if ischar(history_text) && size(history_text, 1) > 1
        lines = cellstr(history_text)';
    elseif ischar(history_text) || isstring(history_text)
        lines = strsplit(char(history_text), {sprintf('\r\n'), newline});
    else
        lines = {};
    end
    lines = strtrim(lines);
    lines = lines(~cellfun(@isempty, lines));

    result.status = 'success';
    result.history_text = strjoin(lines, newline);
    result.history_lines = lines;
    result.num_entries = numel(lines);
    if isempty(lines)
        result.message = 'no operations recorded';
    end
    eegmcp_emit(result);
catch err
    eegmcp_fail('history_failed', err.message, 'Check that the dataset passes eeg_checkset.');
end
end
