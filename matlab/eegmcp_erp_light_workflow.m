function eegmcp_erp_light_workflow(options)
%EEGMCP_ERP_LIGHT_WORKFLOW Filter, epoch, summarize and save a derivative ERP.
try
    opts = eegmcp_options(options);
    opts.pipeline_type = 'erp';
    result = eegmcp_pipeline_run(opts, 'eeglab_erp_light_workflow', true);
    if ~isempty(result)
        eegmcp_emit(result);
    end
catch err
    eegmcp_workflow_fail(err, 'erp_workflow_failed');
end
end
