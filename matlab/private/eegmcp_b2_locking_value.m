function value = eegmcp_b2_locking_value(epoch, field)
%EEGMCP_B2_LOCKING_VALUE Value of an event field for the time-locking event of one epoch.
%   EPOCH is one element of EEG.epoch and FIELD an event field name such as
%   'type'. The time-locking event is the one at latency 0; when none is at
%   0, the first event of the epoch is used. Returns [] when absent.

value = [];
name = ['event' field];
if ~isfield(epoch, name)
    return
end
values = epoch.(name);
if ~iscell(values)
    value = values;
    return
end
if isempty(values)
    return
end
pick = 1;
if isfield(epoch, 'eventlatency') && iscell(epoch.eventlatency)
    latencies = epoch.eventlatency;
    for k = 1:numel(latencies)
        if isnumeric(latencies{k}) && isscalar(latencies{k}) && abs(latencies{k}) < 1e-6
            pick = k;
            break
        end
    end
end
value = values{pick};
end
