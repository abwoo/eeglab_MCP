function [indices, unknown] = eegmcp_b2_channels(dataset, channels)
%EEGMCP_B2_CHANNELS Channel indices of the labels in CHANNELS (exact, case-insensitive).
%   An empty CHANNELS selects every channel. UNKNOWN lists the labels that
%   are not in dataset.chanlocs.

names = eegmcp_cellstr(channels);
unknown = {};
if isempty(names)
    indices = 1:dataset.nbchan;
    return
end
if isempty(dataset.chanlocs) || ~isfield(dataset.chanlocs, 'labels')
    indices = [];
    unknown = names;
    return
end
labels = {dataset.chanlocs.labels};
indices = zeros(1, 0);
for k = 1:numel(names)
    hit = find(strcmpi(strtrim(names{k}), labels), 1);
    if isempty(hit)
        unknown{end + 1} = names{k}; %#ok<AGROW>
    elseif ~ismember(hit, indices)
        indices(end + 1) = hit; %#ok<AGROW>
    end
end
end
