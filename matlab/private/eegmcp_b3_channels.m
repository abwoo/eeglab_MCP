function [indices, missing] = eegmcp_b3_channels(dataset, value)
%EEGMCP_B3_CHANNELS Resolve a channels option to channel indices of DATASET.
%   VALUE is a JSON list of channel labels (or 1-based indices). An empty
%   VALUE selects every channel. Labels are matched without regard to case;
%   MISSING lists the entries that match no channel.

names = eegmcp_cellstr(value);
if isempty(names)
    indices = 1:dataset.nbchan;
    missing = {};
    return
end
if isfield(dataset, 'chanlocs') && ~isempty(dataset.chanlocs) && isfield(dataset.chanlocs, 'labels')
    labels = {dataset.chanlocs.labels};
else
    labels = {};
end
indices = zeros(1, numel(names));
missing = {};
for k = 1:numel(names)
    match = find(strcmpi(labels, names{k}), 1);
    if isempty(match)
        number = str2double(names{k});
        if ~isnan(number) && number == round(number) && number >= 1 && number <= dataset.nbchan
            match = number;
        end
    end
    if isempty(match)
        missing{end + 1} = names{k}; %#ok<AGROW>
    else
        indices(k) = match;
    end
end
indices = unique(indices(indices > 0), 'stable');
end
