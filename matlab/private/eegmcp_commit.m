function eegmcp_commit(dataset)
%EEGMCP_COMMIT Store a processed dataset as the current EEGLAB dataset.
%   Overwrites the current set in ALLEEG, as EEGLAB's own menus do, so the
%   EEGLAB session and the MCP tools keep seeing the same dataset. Console
%   output from EEGLAB is captured so only the tool's JSON is printed.

global EEG ALLEEG CURRENTSET
evalc('dataset = eeg_checkset(dataset);');
if isempty(CURRENTSET) || CURRENTSET == 0
    evalc('[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, dataset, 0);');
else
    evalc('[ALLEEG, EEG] = eeg_store(ALLEEG, dataset, CURRENTSET);');
end
end
