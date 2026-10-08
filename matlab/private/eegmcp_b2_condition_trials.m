function trials = eegmcp_b2_condition_trials(dataset, condition)
%EEGMCP_B2_CONDITION_TRIALS Epochs whose time-locking event type is CONDITION.
%   Event types are compared as text, so numeric markers work too.

trials = zeros(1, 0);
if ~isfield(dataset, 'epoch') || isempty(dataset.epoch)
    return
end
target = eegmcp_b2_type_text(condition);
for k = 1:numel(dataset.epoch)
    value = eegmcp_b2_locking_value(dataset.epoch(k), 'type');
    if strcmp(eegmcp_b2_type_text(value), target)
        trials(end + 1) = k; %#ok<AGROW>
    end
end
end
