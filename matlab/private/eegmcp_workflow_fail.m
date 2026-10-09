function eegmcp_workflow_fail(err, code)
%EEGMCP_WORKFLOW_FAIL Preserve useful option errors in the JSON error contract.
if strcmp(err.identifier, 'eegmcp:options')
    code = 'invalid_options';
elseif strcmp(err.identifier, 'eegmcp:arguments')
    code = 'invalid_arguments';
end
eegmcp_fail(code, err.message, 'Correct the options and resolve the reported prerequisites before retrying.');
end
