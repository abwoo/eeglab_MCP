function labels = eegmcp_b3_labels(dataset, indices)
%EEGMCP_B3_LABELS Channel labels of DATASET at INDICES, as a 1xN cell of char.
%   Channels without a label are named by their index.

labels = arrayfun(@(k) num2str(k), indices, 'UniformOutput', false);
if isfield(dataset, 'chanlocs') && isfield(dataset.chanlocs, 'labels')
    for k = 1:numel(indices)
        if indices(k) <= numel(dataset.chanlocs) && ~isempty(dataset.chanlocs(indices(k)).labels)
            labels{k} = char(dataset.chanlocs(indices(k)).labels);
        end
    end
end
end
