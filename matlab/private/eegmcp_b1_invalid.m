function eegmcp_b1_invalid(tool_name, errors)
%EEGMCP_B1_INVALID Print the invalid_arguments error for a list of option errors.
%   ERRORS is a cell array of messages, reported in details.errors.

result = struct('status', 'error', 'code', 'invalid_arguments', ...
    'error', [tool_name ' options are invalid: ' strjoin(errors, '; ')], ...
    'next_step', 'Adjust the options to match the tool description, then retry.', ...
    'details', struct('errors', {errors}));
eegmcp_emit(result);
end
