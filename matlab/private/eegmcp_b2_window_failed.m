function failed = eegmcp_b2_window_failed(tool_name, errors)
%EEGMCP_B2_WINDOW_FAILED Print the invalid_analysis_window error when ERRORS is not empty.
%   Include every failed window constraint in details.errors.

failed = ~isempty(errors);
if failed
    result = struct('status', 'error', 'code', 'invalid_analysis_window', ...
        'error', [tool_name ' has an invalid analysis window: ' strjoin(errors, '; ')], ...
        'next_step', 'adjust the epoch, baseline, time and frequency windows, then retry.', ...
        'details', struct('errors', {errors}));
    eegmcp_emit(result);
end
end
