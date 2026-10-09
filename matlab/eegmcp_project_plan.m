function eegmcp_project_plan(options)
%EEGMCP_PROJECT_PLAN Return staged QC, method gates and reporting requirements.
try
    eegmcp_emit(eegmcp_plan(eegmcp_options(options), 'eeglab_project_plan'));
catch err
    eegmcp_workflow_fail(err, 'project_plan_failed');
end
end
