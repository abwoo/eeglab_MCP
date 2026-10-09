function eegmcp_plugin_check(options)
%EEGMCP_PLUGIN_CHECK Probe official plugin entry points without running them.
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'plugins', 'strings'});
    root = fileparts(fileparts(mfilename('fullpath')));
    doc = jsondecode(fileread(fullfile(root, 'generated', 'eeglab-official-plugins.json')));
    names = fieldnames(doc.plugins);
    requested = eegmcp_cellstr(eegmcp_opt(opts, 'plugins', names));
    entries = {};
    for k = 1:numel(requested)
        key = matlab.lang.makeValidName(requested{k});
        hit = find(strcmpi(key, names), 1);
        if isempty(hit)
            spec = struct('functions', {{}}, 'support_level', 'out_of_scope', 'claim_ids', {{}}, ...
                'dependent_profiles', {{}}, 'url', '', 'next_step_if_missing', 'Plugin is outside the official map.');
        else
            spec = doc.plugins.(names{hit});
        end
        functions = eegmcp_cellstr(spec.functions);
        found = {};
        for j = 1:numel(functions)
            if any(exist(functions{j}, 'file') == [2, 3, 6])
                found{end + 1} = functions{j}; %#ok<AGROW>
            end
        end
        spec.plugin = requested{k};
        spec.available = ~isempty(found);
        spec.found_functions = found;
        % Availability does not promote an indexed plugin to execution support.
        entries{end + 1} = spec; %#ok<AGROW>
    end
    eegmcp_emit(eegmcp_workflow_result('eeglab_plugin_check', opts, ...
        struct('plugins', {entries}), struct('plugin_matrix', {entries})));
catch err
    eegmcp_workflow_fail(err, 'plugin_check_failed');
end
end
