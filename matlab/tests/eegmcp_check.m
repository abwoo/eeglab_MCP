function eegmcp_check(condition, name, result)
%EEGMCP_CHECK Fail the test run with the tool result when CONDITION is false.
if ~condition
    error('eegmcp:test', 'FAILED: %s\n%s', name, jsonencode(result, 'PrettyPrint', true));
end
fprintf('ok: %s\n', name);
end
