function eegmcp_protocol_export(options)
%EEGMCP_PROTOCOL_EXPORT Render a reproducible record, optionally to a cloud file.
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'format', 'string', {'json', 'markdown'}; 'output_path', 'string', []; ...
        'research_goal', 'string', []; 'analysis_type', 'string', []; 'parameters', 'object', []; ...
        'outputs', 'object', []; 'override_reason', 'string', []; 'override_used', 'boolean', []});
    if eegmcp_opt(opts, 'override_used', false) && isempty(strtrim(eegmcp_opt(opts, 'override_reason', '')))
        error('eegmcp:arguments', 'An override requires a non-empty override_reason.');
    end
    gates = eegmcp_opt(opts, 'gate_results', {});
    if isstruct(gates)
        gates = num2cell(gates);
    end
    claims = {}; missing = {}; overrides = {};
    for k = 1:numel(gates)
        gate = gates{k};
        claims = [claims, eegmcp_cellstr(eegmcp_opt(gate, 'source_claim_ids', {}))]; %#ok<AGROW>
        if isfield(gate, 'missing_requirements')
            requirements = gate.missing_requirements;
            if isstruct(requirements)
                requirements = num2cell(requirements);
            end
            for j = 1:numel(requirements)
                missing{end + 1} = requirements{j}.id; %#ok<AGROW>
            end
        end
        if eegmcp_opt(gate, 'override_used', false)
            reason = strtrim(eegmcp_opt(gate, 'override_reason', ''));
            if isempty(reason)
                error('eegmcp:arguments', 'A gate override requires a recorded reason.');
            end
            overrides{end + 1} = reason; %#ok<AGROW>
        end
    end
    if eegmcp_opt(opts, 'override_used', false)
        overrides{end + 1} = opts.override_reason;
    end
    root = fileparts(fileparts(mfilename('fullpath')));
    fields_doc = jsondecode(fileread(fullfile(root, 'generated', 'eeglab-report-fields.json')));
    record = struct('document', 'eeglab-research-protocol', 'document_version', '1.0.0', ...
        'research_goal', eegmcp_opt(opts, 'research_goal', ''), ...
        'analysis_type', eegmcp_opt(opts, 'analysis_type', ''), 'parameters', eegmcp_opt(opts, 'parameters', struct()), ...
        'outputs', eegmcp_opt(opts, 'outputs', struct()), 'steps', {eegmcp_opt(opts, 'steps', {})}, ...
        'gate_results', {gates}, 'source_claim_ids', {unique(claims, 'stable')}, ...
        'missing_requirements', {unique(missing, 'stable')}, 'override_used', ~isempty(overrides), ...
        'override_reasons', {overrides}, 'required_report_fields', fields_doc.fields, ...
        'not_for_clinical_use', true);
    format = eegmcp_opt(opts, 'format', 'markdown');
    text = jsonencode(record, 'PrettyPrint', true);
    if strcmp(format, 'markdown')
        text = sprintf('# EEGLAB research protocol\n\nGoal: %s\n\nAnalysis: %s\n\n```json\n%s\n```\n', ...
            record.research_goal, record.analysis_type, text);
    end
    path = strtrim(eegmcp_opt(opts, 'output_path', ''));
    if ~isempty(path)
        [folder, ~, ext] = fileparts(path);
        expected = '.md';
        if strcmp(format, 'json')
            expected = '.json';
        end
        if ~strcmpi(ext, expected)
            error('eegmcp:arguments', 'Protocol filename must end in %s.', expected);
        end
        if ~isempty(folder) && ~isfolder(folder)
            mkdir(folder);
        end
        fid = fopen(path, 'w', 'n', 'UTF-8');
        if fid < 0
            error('eegmcp:arguments', 'Cannot open the protocol output file.');
        end
        cleanup = onCleanup(@() fclose(fid));
        fprintf(fid, '%s', text);
        clear cleanup
    end
    outputs = struct('protocol_text', text, 'written_path', path);
    eegmcp_emit(eegmcp_workflow_result('eeglab_protocol_export', opts, record, outputs));
catch err
    eegmcp_workflow_fail(err, 'protocol_export_failed');
end
end
