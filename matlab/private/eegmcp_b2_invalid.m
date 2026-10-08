function failed = eegmcp_b2_invalid(tool_name, errors)
%EEGMCP_B2_INVALID Print the invalid_arguments error when ERRORS is not empty.
%   ERRORS is a cell array of messages. Returns true when an error was
%   printed, so the caller just returns.

failed = ~isempty(errors);
if failed
    result = struct('status', 'error', 'code', 'invalid_arguments', ...
        'error', [tool_name ' arguments are invalid: ' strjoin(errors, '; ')], ...
        'next_step', 'adjust the options to match the tool description, then retry.', ...
        'details', struct('errors', {errors}));
    eegmcp_emit(result);
end
end
