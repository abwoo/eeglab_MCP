function errors = eegmcp_window_errors(epoch_window, baseline_window_ms, time_window_ms)
%   Validate option types before scientific operations.
%   Pass [] for a window that is not set. EPOCH_WINDOW is in seconds, the
%   other two in milliseconds. Returns a cell array of error messages.

errors = {};
if ~isempty(epoch_window)
    if numel(epoch_window) ~= 2
        errors{end + 1} = 'epoch_window must have exactly 2 items';
    elseif epoch_window(1) >= epoch_window(2)
        errors{end + 1} = 'epoch_window start must be less than its end';
    end
end
if ~isempty(baseline_window_ms)
    if numel(baseline_window_ms) ~= 2
        errors{end + 1} = 'baseline_window must have exactly 2 items';
    elseif baseline_window_ms(1) > baseline_window_ms(2)
        errors{end + 1} = 'baseline_window start must be less than or equal to its end';
    elseif numel(epoch_window) == 2
        epoch_ms = epoch_window * 1000;
        if baseline_window_ms(1) < epoch_ms(1) || baseline_window_ms(2) > epoch_ms(2)
            errors{end + 1} = 'baseline_window must fall inside epoch_window';
        end
    end
end
if ~isempty(time_window_ms)
    if numel(time_window_ms) ~= 2
        errors{end + 1} = 'time_window must have exactly 2 items';
    elseif time_window_ms(1) >= time_window_ms(2)
        errors{end + 1} = 'time_window start must be less than its end';
    end
end
end
