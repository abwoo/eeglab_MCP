function dataset = eegmcp_current_dataset()
%EEGMCP_CURRENT_DATASET Return the current EEGLAB dataset, or [] if none is loaded.
%   The tools share EEGLAB's own global EEG, so a dataset loaded through MCP
%   is the same dataset the EEGLAB session sees, and the other way round.

global EEG
if isempty(EEG) || ~isstruct(EEG) || ~isfield(EEG, 'data') || isempty(EEG.data)
    dataset = [];
else
    dataset = EEG;
end
end
