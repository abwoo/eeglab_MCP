function eegmcp_workflow_recommend(options)
%EEGMCP_WORKFLOW_RECOMMEND Plan a research branch without modifying EEG.
try
    eegmcp_emit(eegmcp_plan(eegmcp_options(options), 'eeglab_workflow_recommend'));
catch err
    eegmcp_workflow_fail(err, 'workflow_recommend_failed');
end
end
