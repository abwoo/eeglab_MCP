function [indices, missing] = eegmcp_b1_channels(dataset, names)
%EEGMCP_B1_CHANNELS Indices of channel labels in a dataset, ignoring case.
%   NAMES is a cell array of labels. MISSING lists the labels not found.

labels = {};
if isfield(dataset, 'chanlocs') && ~isempty(dataset.chanlocs) && isfield(dataset.chanlocs, 'labels')
    labels = {dataset.chanlocs.labels};
end
indices = zeros(1, 0);
missing = {};
for k = 1:numel(names)
    hit = find(strcmpi(strtrim(names{k}), labels), 1);
    if isempty(hit)
        missing{end + 1} = names{k}; %#ok<AGROW>
    else
        indices(end + 1) = hit; %#ok<AGROW>
    end
end
indices = unique(indices, 'stable');
end
