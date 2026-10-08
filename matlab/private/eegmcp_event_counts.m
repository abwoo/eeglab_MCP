function [types, counts] = eegmcp_event_counts(events)
%EEGMCP_EVENT_COUNTS Unique event types of an EEG.event array and their counts.
%   TYPES is a 1xN cell array of char. COUNTS is a 1xN cell array of structs
%   with fields type and count; a cell keeps jsonencode output a JSON array
%   even when there is a single type. Numeric event types are converted to text, so
%   datasets with numeric markers are handled the same way as text markers.

labels = cell(1, numel(events));
for k = 1:numel(events)
    value = events(k).type;
    if isnumeric(value) || islogical(value)
        labels{k} = num2str(value);
    else
        labels{k} = char(value);
    end
end

if isempty(labels)
    types = {};
    counts = {};
    return
end

[types, ~, index] = unique(labels);
types = reshape(types, 1, []);
totals = reshape(accumarray(index(:), 1), 1, []);
counts = num2cell(struct('type', types, 'count', num2cell(totals)));
end
