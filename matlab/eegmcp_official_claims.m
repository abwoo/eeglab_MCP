function eegmcp_official_claims()
%EEGMCP_OFFICIAL_CLAIMS Return the versioned official claims and method profiles.
try
    eegmcp_emit(eegmcp_claims());
catch err
    eegmcp_workflow_fail(err, 'claims_read_failed');
end
end
