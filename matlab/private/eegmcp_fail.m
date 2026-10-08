function eegmcp_fail(code, message, next_step)
%EEGMCP_FAIL Print a JSON error result with a code and a suggested next step.

result = struct('status', 'error', 'code', code, 'error', message, 'next_step', next_step);
eegmcp_emit(result);
end
