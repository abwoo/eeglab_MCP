function eegmcp_pipeline(options)
%EEGMCP_PIPELINE Run a recorded ERP, resting or time-frequency tool sequence.
try
    opts = eegmcp_options(options);
    result = eegmcp_pipeline_run(opts, 'eeglab_pipeline', false);
    if ~isempty(result)
        eegmcp_emit(result);
    end
catch err
    eegmcp_workflow_fail(err, 'pipeline_failed');
end
end
