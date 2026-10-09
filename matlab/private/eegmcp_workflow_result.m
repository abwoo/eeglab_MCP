function result = eegmcp_workflow_result(name, parameters, summary, outputs, steps)
%EEGMCP_WORKFLOW_RESULT Common research workflow result and provenance limits.
if nargin < 4
    outputs = struct();
end
if nargin < 5
    steps = {};
end
result = struct('status', 'success', 'workflow', name, 'steps', {steps}, ...
    'parameters', parameters, 'outputs', outputs, 'summary', summary, ...
    'limitations', {{'EEG signal processing is not clinical diagnosis.', ...
    'Results depend on recording quality, event semantics, channel metadata and installed plugins.'}});
end
