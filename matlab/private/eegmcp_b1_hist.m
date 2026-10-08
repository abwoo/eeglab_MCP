function dataset = eegmcp_b1_hist(dataset, command)
%EEGMCP_B1_HIST Record an EEGLAB command in EEG.history.
%   pop_ functions return their command line but only the EEGLAB menus store
%   it, so the tools add it themselves; eeglab_history then lists every step
%   applied through MCP. The local variable name is written as EEG.

if isempty(command) || ~ischar(command)
    return
end
command = regexprep(command, '\<dataset\>', 'EEG');
if exist('eeg_hist', 'file') == 2
    dataset = eeg_hist(dataset, command);
elseif isfield(dataset, 'history') && ~isempty(dataset.history)
    dataset.history = [dataset.history newline command];
else
    dataset.history = command;
end
end
